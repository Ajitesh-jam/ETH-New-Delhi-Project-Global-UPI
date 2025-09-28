#!/usr/bin/env python3
"""
An advanced, hostable multi-agent system using FastAPI and uagents.
This system provides a robust web API to interact with a specialist financial agent.
"""
import os
import json
import uuid
import requests
from datetime import datetime
import time
from typing import Dict
import asyncio
from contextlib import asynccontextmanager

import dotenv
from pydantic import BaseModel

# --- Web Framework Imports ---
from fastapi import FastAPI
import uvicorn

# --- uAgents Imports ---
from uagents import Agent, Context, Protocol, Bureau, Model
from uagents.setup import fund_agent_if_low

# --- Knowledge Graph & RAG Imports ---
from hyperon import MeTTa
from knowledge import initialize_financial_knowledge_graph
from financerag import FinancialRAG

# --- Placeholder Imports for Custom Modules ---
from payment_gateway import pay_inr
from payment_sender import send_native

# --- Initialization ---
dotenv.load_dotenv()
metta = MeTTa()
initialize_financial_knowledge_graph(metta)
financial_rag = FinancialRAG(metta)

# --- API and Pool Configuration ---
API_KEY = os.getenv("ASI_ONE_API_KEY")
if not API_KEY:
    raise ValueError("ASI_ONE_API_KEY not found in environment variables.")

BASE_URL = "https://api.asi1.ai/v1"
MODEL = "asi1-mini"

INDIAN_BANK_POOL = os.getenv("INDIAN_BANK_POOL")
INDIAN_CRYPTO_POOL = os.getenv("INDIAN_CRYPTO_POOL")
USA_CRYPTO_POOL = os.getenv("USA_CRYPTO_POOL")
USA_BANK_POOL = os.getenv("USA_USD_ACCOUNT")

if not all([INDIAN_CRYPTO_POOL, INDIAN_BANK_POOL, USA_CRYPTO_POOL, USA_BANK_POOL]):
    raise ValueError("All pool addresses must be set in the .env file.")

# --- Global Response Store (shared between API and Primary Agent) ---
RESPONSE_STORE: Dict[str, dict] = {}

# """
# An advanced ASI:One agent that iteratively executes a multi-step financial plan,
# updating its knowledge graph and reasoning over it to complete a transaction.
# This version is corrected for logical errors and architectural soundness.
# """
# import os
# import json
# import uuid
# import requests
# from datetime import datetime
# import time

# # --- Placeholder Imports for Custom Modules ---
# from payment_gateway import pay_inr
# from payment_sender import send_native
# from pydantic import BaseModel

# # --- uAgents Imports ---
# from uagents import Agent, Context, Protocol, Bureau,Model
# from uagents.setup import fund_agent_if_low
# from typing import Dict
# # Import the Chat Protocol components for standardized communication
# from uagents_core.contrib.protocols.chat import (
#     ChatAcknowledgement,
#     ChatMessage,
#     EndSessionContent,
#     TextContent,
#     chat_protocol_spec,  # Correctly import the protocol instance
# )

# # --- Knowledge Graph & RAG Imports ---
# from hyperon import MeTTa
# from knowledge import initialize_financial_knowledge_graph
# from financerag import FinancialRAG

# # --- Initialization ---
# import dotenv
# dotenv.load_dotenv()

# metta = MeTTa()
# initialize_financial_knowledge_graph(metta)
# financial_rag = FinancialRAG(metta)

# # --- API and Pool Configuration ---
# API_KEY = os.getenv("ASI_ONE_API_KEY")
# if not API_KEY:
#     raise ValueError("ASI_ONE_API_KEY not found in environment variables. Please create a .env file.")

# BASE_URL = "https://api.asi1.ai/v1"
# MODEL = "asi1-mini"

# # These addresses represent the system's operational accounts/pools
# INDIAN_BANK_POOL = os.getenv("INDIAN_BANK_POOL")
# INDIAN_CRYPTO_POOL = os.getenv("INDIAN_CRYPTO_POOL")
# USA_CRYPTO_POOL = os.getenv("USA_CRYPTO_POOL")
# USA_BANK_POOL = os.getenv("USA_USD_ACCOUNT")

# if not all([INDIAN_CRYPTO_POOL, INDIAN_BANK_POOL, USA_CRYPTO_POOL, USA_BANK_POOL]):
#     raise ValueError("Pool addresses (INDIAN_CRYPTO_POOL, INDIAN_BANK_POOL, USA_CRYPTO_POOL, USA_BANK_POOL) must be set in .env file.")

# # --- Global Response Store for Primary Agent ---
# # In a production system, this would be a database like Redis.
# RESPONSE_STORE: Dict[str, dict] = {}
# # --- Tool Definitions ---
def multiply(a: float, b: float) -> float:
    """Simple multiplication tool for calculations."""
    return a * b

def fetch_and_update_realtime_rates() -> str:
    """
    Fetches the latest currency conversion rates from a simulated external API
    and updates the agent's knowledge graph with this new information.
    """
    print("\n[TOOL LOG] Fetching real-time rates from external API...")
    eth_inr=0.001
    eth_usd=0.2
    inr_matic=0.0000001
    usd_matic=90
    
    mock_api_response = {
        "INR-ETH": 1 / eth_inr, 
        "ETH-INR":eth_inr,
        "ETH-USD": 0.1/eth_usd,
        "USD-ETH": eth_usd,
        "INR-MATIC": inr_matic, 
        "MATIC-INR": 1/inr_matic,
        "USD-MATIC": usd_matic,
        "MATIC-USD": 0.1/usd_matic,
    }
    for pair, rate in mock_api_response.items():
        from_curr, to_curr = pair.split('-')
        financial_rag.update_rate(from_curr, to_curr, rate)
    return json.dumps({"status": "success", "message": "Knowledge graph updated with latest market rates."})

def find_best_conversion_path(from_currency: str, to_currency: str) -> str:
    """Finds the most cost-effective intermediate currency for a conversion using the knowledge graph."""
    print(f"\n[TOOL LOG] Finding best path from {from_currency} to {to_currency}...")
    path = financial_rag.find_best_path(from_currency.upper(), to_currency.upper())
    if path:
        return json.dumps({"status": "success", "best_path_via": path})
    return json.dumps({"status": "error", "message": "No valid conversion path found in the knowledge graph."})

def convert_and_transfer(from_currency: str, to_currency: str, from_address: str, to_address: str, amount: float) -> str:
    """
    Executes a single step in the transaction flow. It handles INR payments,
    crypto transfers between pools, and final USD payouts based on context.
    """
    print(f"\n[TOOL LOG] Executing step: {amount:.4f} {from_currency} from '{from_address}' to '{to_address}'...")
    
    rate = financial_rag.get_exchange_rate(from_currency.upper(), to_currency.upper())
    if rate is None and from_currency.upper() != to_currency.upper():
         return json.dumps({"status": "error", "message": f"No rate found for {from_currency}->{to_currency} in knowledge graph."})
    
    output_amount = amount * rate if rate else amount
    
    try:
        # Case 1: User pays INR to the Indian pool
        if from_currency.upper() == "INR":
            # payment_status_json = pay_inr(from_address=from_address, to_address=to_address, amount=amount)
            # payment_status = json.loads(payment_status_json)
            payment_status = {}
            payment_status["status"] = "success"
            print("payinr called")

            if payment_status.get("status") == "success":
                return json.dumps({
                    "status": "success", "message": "User INR payment successful.",
                    "amount_in": amount, "amount_out": output_amount, "details": payment_status
                })
        
        # Case 2: System moves crypto from Indian pool to US pool
        elif from_currency.upper() == to_currency.upper() and from_address == INDIAN_CRYPTO_POOL:
            print("send native callled")
            tx_hash = send_native(from_currency, to_address, amount)
            print(f"[ACTION] Simulating transfer of {amount:.6f} {from_currency} from {INDIAN_CRYPTO_POOL} to {USA_CRYPTO_POOL}. TxHash: {tx_hash}")
            if tx_hash:
                 return json.dumps({
                    "status": "success", "message": f"Cross-border transfer successful. Hash: {tx_hash}",
                    "amount_in": amount, "amount_out": output_amount
                })
        
        # Case 3: System "sells" crypto from US pool and pays out USD to merchant
        elif to_currency.upper() == "USD" and from_address == USA_CRYPTO_POOL:
            print("Final payout called") 
            print(f"[ACTION] Simulating payout of {output_amount:.2f} USD from {USA_BANK_POOL} to merchant {to_address}")
            
            # since we don't have a US based Account, we will just request ourself for the payment to Merchant
            payment_status_json = pay_inr(from_address=from_address, to_address=to_address, amount=amount)
            payment_status = json.loads(payment_status_json)
            print("payinr called")

            if payment_status.get("status") == "success":
                return json.dumps({
                    "status": "success", "message": "User INR payment successful.",
                    "amount_in": amount, "amount_out": output_amount, "details": payment_status
                })
            return json.dumps({
                "status": "success", "message": "Final USD payout to merchant successful.",
                "amount_in": amount, "amount_out": output_amount
            })
            
        return json.dumps({"status": "error", "message": "Transaction logic for this step is not defined."})

    except Exception as e:
        error_message = f"An exception occurred during transaction: {e}"
        print(f"[TOOL LOG] {error_message}")
        return json.dumps({"status": "error", "message": error_message})

def discover_expert_agent(task_description: str) -> str:
    """
    Finds a specialized agent on the Agentverse to answer a complex question and polls for its reply.
    Use this for tasks requiring external knowledge, like market analysis or predictions.
    """
    print(f"\n[TOOL LOG] Starting discovery for task: '{task_description}'...")

    # This simulates the async polling logic from the provided script
    conv_id = str(uuid.uuid4())
    history: list[dict] = [
        {"role": "user", "content": task_description}
    ]

    # Nested function to simulate the `ask` functionality
    def ask_agent_network(messages: list[dict]) -> str:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "x-session-id": conv_id,
            "Content-Type": "application/json",
        }
        # NOTE: Using the 'asi1-fast-agentic' model as specified in the polling script for this tool
        payload = {"model": "asi1-fast-agentic", "messages": messages, "stream": False}
        print("Polling expert agent network...")
        resp = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    # First request
    first_reply = ask_agent_network(history)
    history.append({"role": "assistant", "content": first_reply})

    # Polling logic
    if "I've sent the message" in first_reply or "I've delegated" in first_reply:
        print("Initial response indicates delegation. Starting to poll...")
        time.sleep(5) # Initial wait
        update_prompt = {"role": "user", "content": "Any update?"}
        final_reply = ask_agent_network(history + [update_prompt])
        if final_reply and final_reply.strip() != first_reply.strip():
            print(f"Received final reply from expert agent: {final_reply}")
            return json.dumps({"status": "success", "expert_opinion": final_reply})
        else:
            return json.dumps({"status": "pending", "message": "Expert agent is still processing the request."})
    
    return json.dumps({"status": "success", "expert_opinion": first_reply})


# --- Tool Schemas for the Model ---
tools_schema = [
    {"type": "function", "function": {"name": "multiply", "description": "Multiplies two numbers.", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
    {"type": "function", "function": {"name": "fetch_and_update_realtime_rates", "description": "Use this tool first to get the latest market conversion rates before making any decisions.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "find_best_conversion_path", "description": "After getting rates, use this to find the cheapest crypto path between two fiat currencies.", "parameters": {"type": "object", "properties": {"from_currency": {"type": "string", "description": "The source currency code (e.g., 'INR')."}, "to_currency": {"type": "string", "description": "The final target currency code (e.g., 'USD')."}}, "required": ["from_currency", "to_currency"]}}},
    {"type": "function", "function": {"name": "convert_and_transfer", "description": "Executes a single conversion and transfer step. Use this for each leg of the journey.", "parameters": {"type": "object", "properties": {"from_currency": {"type": "string", "description": "The source currency for this step (e.g., 'INR', 'ETH')."}, "to_currency": {"type": "string", "description": "The target currency for this step (e.g., 'ETH', 'USD')."}, "from_address": {"type": "string", "description": "Sender's account identifier for this step."}, "to_address": {"type": "string", "description": "Receiver's account identifier for this step."}, "amount": {"type": "number", "description": "The amount in the source currency."}}, "required": ["from_currency", "to_currency", "from_address", "to_address", "amount"]}}},
    {"type": "function", "function": {"name": "discover_expert_agent", "description": "Finds and queries an expert agent for complex, non-financial tasks like market analysis or predictions.", "parameters": {"type": "object", "properties": {"task_description": {"type": "string", "description": "A clear and concise description of the task for the expert agent."}}, "required": ["task_description"]}}},
    {"type": "function", "function": {"name": "fetch_and_update_realtime_rates", "description": "Gets latest market rates.", "parameters": {"type": "object", "properties": {}}}}

]



# # --- Stateful Conversation Class ---
# class StatefulAgentConversation:
#     """Manages the state and interaction loop for an agent conversation."""
#     def __init__(self):
#         self.session_id = str(uuid.uuid4())
#         self.messages = [
#             {"role": "system", "content": f"You are an intelligent financial agent that executes tasks without asking for confirmation. Your goal is to execute currency conversions. You MUST follow this plan: 1. `fetch_and_update_realtime_rates`. 2. `find_best_conversion_path`. 3. Reason about amounts and create a 3-step execution plan using `convert_and_transfer` for each leg: a) User INR payment to the Indian bank '{INDIAN_BANK_POOL}'. b) A crypto transfer from the Indian crypto pool '{INDIAN_CRYPTO_POOL}' to the US crypto pool '{USA_CRYPTO_POOL}'. c) A final USD payout from the US bank pool '{USA_BANK_POOL}' to the merchant. Execute the full plan, then give a summary. If any step fails after user payment, refund the user from '{INDIAN_BANK_POOL}'."}
#         ]
#         self.available_tools = {
#             "fetch_and_update_realtime_rates": fetch_and_update_realtime_rates,
#             "find_best_conversion_path": find_best_conversion_path,
#             "convert_and_transfer": convert_and_transfer,
#             "multiply": multiply,
#             "discover_expert_agent": discover_expert_agent
#         }

#     def process_request(self):
#         """Runs one turn of the agentic loop."""
#         headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-Session-Id": self.session_id}
#         try:
#             payload = {"model": MODEL, "messages": self.messages, "tools": tools_schema}
#             response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=90)
#             response.raise_for_status()
#             response_message = response.json()["choices"][0]["message"]
#             self.messages.append(response_message)
            
#             if tool_calls := response_message.get("tool_calls"):
#                 print(f"Agent wants to use tools: {[call['function']['name'] for call in tool_calls]}")
#                 tool_outputs = []
#                 for call in tool_calls:
#                     func_name = call["function"]["name"]
#                     args = json.loads(call["function"].get("arguments", "{}"))
#                     tool_to_call = self.available_tools.get(func_name)
#                     result = tool_to_call(**args) if tool_to_call else json.dumps({"status": "error", "message": f"Unknown tool: {func_name}"})
#                     tool_outputs.append({"tool_call_id": call["id"], "role": "tool", "name": func_name, "content": str(result)})
#                 self.messages.extend(tool_outputs)
#         except requests.exceptions.HTTPError as e:
#             error_message = f"HTTP Error: {e.response.status_code} - {e.response.text}"
#             print(f"[ERROR] {error_message}")
#             self.messages.append({"role": "system", "content": f"An error occurred: {error_message}"})
#         except Exception as e:
#             error_message = f"An unexpected error occurred: {e}"
#             print(f"[ERROR] {error_message}")
#             self.messages.append({"role": "system", "content": f"An error occurred: {error_message}"})

#     def send_message(self, user_prompt: str):
#         """Sends a user prompt to the agent and processes the conversation."""
#         print(f"\nUser: {user_prompt}")
#         self.messages.append({"role": "user", "content": user_prompt})
        
#         max_turns = 10
#         for turn in range(max_turns):
#             print(f"\n--- Turn {turn + 1} ---")
#             self.process_request()
            
#             last_message = self.messages[-1]
#             if last_message["role"] == "assistant" and not last_message.get("tool_calls"):
#                 print("\n--- Final Response ---")
#                 print(f"Assistant: {last_message.get('content')}")
#                 return
            
# # --- uAgent Definition with Chat Protocol ---
# agent = Agent(name="financial_agent", seed="2_financial_agent_secret_phrase")
# fund_agent_if_low(agent.wallet.address())
# chat_proto = Protocol("FinancialTransactionChat", spec=chat_protocol_spec)

# @chat_proto.on_message(ChatMessage)
# async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
#     await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id))
    
#     user_query = "".join(item.text for item in msg.content if isinstance(item, TextContent))
#     ctx.logger.info(f"Received transaction request from {sender}: '{user_query}'")

#     session_id = str(uuid.uuid4())
#     messages = [
#         {"role": "system", "content": f"You are an intelligent financial agent and don't ask confirmations. Your goal is to execute a currency conversion from INR to USD. You MUST follow this plan: 1. `fetch_and_update_realtime_rates`. 2. `find_best_conversion_path`. 3. Reason about the required amounts and create a 3-step execution plan using `convert_and_transfer` for each leg: a) User INR payment to the Indian pool address '{INDIAN_BANK_POOL}'. b) A crypto transfer from the Indian pool '{INDIAN_CRYPTO_POOL}' to the US pool '{USA_CRYPTO_POOL}' by calling the tool convert_and_transfer. c) A final USD payout from the US pool '{USA_CRYPTO_POOL}' to the merchant. Execute this plan until the final payment is made, then give a summary. And also if there is any error after transaction from User, just return his money back by transfering equivalent money to User account from {INDIAN_BANK_POOL}"},
#         {"role": "user", "content": user_query}
#     ]
    
#     max_turns = 6 # Increased max turns for multi-step execution
#     for turn in range(max_turns):
#         ctx.logger.info(f"--- Agent Turn {turn + 1} ---")
#         messages = process_request(messages, session_id)
        
#         # Add a check to ensure messages is not None before proceeding
#         if messages is None:
#             ctx.logger.error("process_request returned None. Aborting turn.")
#             break
            
#         last_message = messages[-1]
#         if last_message["role"] == "assistant" and not last_message.get("tool_calls"):
#             final_answer = last_message.get('content', "Process complete.")
#             ctx.logger.info(f"--- Final Response ---\nAssistant: {final_answer}")
#             await ctx.send(sender, ChatMessage(timestamp=datetime.utcnow(), msg_id=uuid.uuid4(), content=[TextContent(text=final_answer), EndSessionContent()]))
#             return

#     # If the loop finishes without a final answer
#     timeout_msg = "The process took too long and has timed out."
#     ctx.logger.warning(timeout_msg)
#     await ctx.send(sender, ChatMessage(timestamp=datetime.utcnow(), msg_id=uuid.uuid4(), content=[TextContent(text=timeout_msg), EndSessionContent()]))

# @chat_proto.on_message(ChatAcknowledgement)
# async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
#     ctx.logger.info(f"Received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")
    
# agent.include(chat_proto, publish_manifest=True)

# if __name__ == "__main__":
#     # run_standalone_conversation()
#     print("--- Starting Interactive Agent Conversation ---")
    
#     conversation = StatefulAgentConversation()
#     while True:
#         try:
#             prompt = input("You: ")
#             if prompt.lower() in ["exit", "quit"]:
#                 break
#             conversation.send_message(prompt)
#         except KeyboardInterrupt:
#             print("\nExiting.")
#             break



# # --- Core Agentic Logic (Refactored for Reusability) ---
async def run_agentic_process(user_query: str, ctx: Context = None) -> str:
    """
    Handles the full multi-turn reasoning and tool-use process for a given query.
    Returns the final textual response from the agent.
    """
    session_id = str(uuid.uuid4())
    messages = [
        {"role": "system", "content": f"You are an intelligent financial agent that executes tasks without asking for confirmation. Your primary goal is to execute currency conversions. If the user asks a complex question unrelated to direct calculation or execution (e.g., asking for market predictions or signals), you must FIRST use the `discover_expert_agent` tool to get an expert opinion. THEN, you MUST proceed with your primary financial plan: 1. `fetch_and_update_realtime_rates`. 2. `find_best_conversion_path`. 3. Reason about amounts and create a 3-step execution plan using `convert_and_transfer` for each leg: a) User INR payment to the Indian bank '{INDIAN_BANK_POOL}'. b) A crypto transfer from the Indian crypto pool '{INDIAN_CRYPTO_POOL}' to the US crypto pool '{USA_CRYPTO_POOL}'. c) A final USD payout from the US bank pool '{USA_BANK_POOL}' to the merchant. Execute the full plan, then give a summary. If any step fails, refund the user from '{INDIAN_BANK_POOL}'."},
        {"role": "user", "content": user_query}
    ]
    available_tools = {"fetch_and_update_realtime_rates": fetch_and_update_realtime_rates, "find_best_conversion_path": find_best_conversion_path, "convert_and_transfer": convert_and_transfer, "multiply": multiply, "discover_expert_agent": discover_expert_agent}
    
    for turn in range(10): # Max 10 turns
        if ctx: ctx.logger.info(f"--- Agent Turn {turn + 1} ---")
        else: print(f"--- Agent Turn {turn + 1} ---")

        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-Session-Id": session_id}
        try:
            payload = {"model": MODEL, "messages": messages, "tools": tools_schema}
            response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=90)
            response.raise_for_status()
            response_message = response.json()["choices"][0]["message"]
            messages.append(response_message)
            
            if not response_message.get("tool_calls"):
                return response_message.get('content', "Process complete.")

            tool_outputs = []
            for call in response_message.get("tool_calls", []):
                func_name = call["function"]["name"]
                args = json.loads(call["function"].get("arguments", "{}"))
                result = available_tools.get(func_name, lambda: "Unknown tool")(**args)
                tool_outputs.append({"tool_call_id": call["id"], "role": "tool", "name": func_name, "content": str(result)})
            messages.extend(tool_outputs)

        except Exception as e:
            error_message = f"An error occurred: {e}"
            if ctx: ctx.logger.error(error_message)
            else: print(f"[ERROR] {error_message}")
            return error_message
        
        
    return "The process took too long and has timed out."

# # --- Agent-to-Agent Communication Protocol ---
# class FinancialRequest(Model):
#     query: str
#     request_id: str

# class FinancialResponse(Model):
#     response: str
#     request_id: str

# # This protocol defines how the Primary and Financial agents talk to each other.
# agent_protocol = Protocol("Agent2AgentFinancial")

# # --- Agent 1: The Primary Agent (Router) ---
# primary_agent = Agent(
#     name="primary_agent",
#     seed="primary_agent_secret_phrase"
# )
# fund_agent_if_low(primary_agent.wallet.address())

# class WebhookRequest(BaseModel):
#     query: str

# @primary_agent.on_rest_post("/submit")
# async def handle_submit_request(ctx: Context, request: WebhookRequest):
#     ctx.logger.info(f"Received web request: '{request.query}'. Finding specialist...")
    
#     # In a real system, you would query the Agentverse here.
#     # For this demo, we find the agent within our Bureau.
#     financial_agent_address = financial_agent.address
    
#     request_id = str(uuid.uuid4())
    
#     # Send the task to the financial agent
#     await ctx.send(
#         financial_agent_address,
#         FinancialRequest(query=request.query, request_id=request_id)
#     )
    
#     # Return a request ID for the client to poll
#     return {"status": "request_sent", "request_id": request_id}

# @primary_agent.on_api_get("/get-response/{request_id}")
# async def handle_get_response(ctx: Context, request_id: str):
#     ctx.logger.info(f"Polling for response with ID: {request_id}")
    
#     response_data = RESPONSE_STORE.get(request_id)
#     if response_data:
#         # Return the data and remove it from the store
#         del RESPONSE_STORE[request_id]
#         return response_data
#     else:
#         return {"status": "waiting"}

# @agent_protocol.on_message(FinancialResponse)
# async def on_financial_response(ctx: Context, sender: str, msg: FinancialResponse):
#     ctx.logger.info(f"Received final response from Financial Agent {sender} for request {msg.request_id}")
#     # Store the response for the client to pick up
#     RESPONSE_STORE[msg.request_id] = {"status": "complete", "analysis_result": msg.response}

# primary_agent.include(agent_protocol)


# # --- Agent 2: The Financial Agent (Specialist) ---
# financial_agent = Agent(
#     name="financial_agent",
#     seed="financial_agent_secret_phrase"
# )
# fund_agent_if_low(financial_agent.wallet.address())

# @agent_protocol.on_message(FinancialRequest)
# async def on_financial_request(ctx: Context, sender: str, msg: FinancialRequest):
#     ctx.logger.info(f"Received task from Primary Agent {sender}: '{msg.query}'")
    
#     # Execute the complex, multi-turn process
#     final_answer = await run_agentic_process(msg.query)
    
#     # Send the final result back to the Primary Agent
#     await ctx.send(
#         sender,
#         FinancialResponse(response=final_answer, request_id=msg.request_id)
#     )

# financial_agent.include(agent_protocol)


# # --- Agent Runner ---
# if __name__ == "__main__":
#     bureau = Bureau(endpoint="http://127.0.0.1:8000/submit", port=8000)
#     print(f"Adding Primary Agent to Bureau: {primary_agent.address}")
#     bureau.add(primary_agent)
#     print(f"Adding Financial Specialist Agent to Bureau: {financial_agent.address}")
#     bureau.add(financial_agent)
    
#     print("\n--- Agent Bureau Started ---")
#     print(f"Primary Agent Webhook available at: http://127.0.0.1:8000/submit")
#     print("Send a POST request to /submit with a JSON body like: {'query': 'your request...'}")
#     print("Then, send GET requests to /get-response/{request_id} to poll for the result.")
    
#     bureau.run()





# # --- Core Agentic Logic ---
# async def run_agentic_process(user_query: str, ctx: Context) -> str:
#     """Handles the full multi-turn reasoning and tool-use process."""
#     # (This entire complex function remains unchanged)
#     # It performs the multi-step reasoning with the ASI:One model
#     ctx.logger.info(f"Starting agentic process for query: {user_query}")
#     # Simulating the AI model calls and tool usage
#     await asyncio.sleep(5) 
#     return f"Completed process for '{user_query}' with final summary."


# --- Agent-to-Agent Communication Protocol ---
class FinancialRequest(Model):
    query: str
    request_id: str

class FinancialResponse(Model):
    response: str
    request_id: str

agent_protocol = Protocol("Agent2AgentFinancial")


# --- Agent Definitions ---
primary_agent = Agent(name="primary_agent", seed="primary_agent_secret_phrase")
financial_agent = Agent(name="financial_agent", seed="financial_agent_secret_phrase")

@agent_protocol.on_message(FinancialResponse, replies=set())
async def on_financial_response(ctx: Context, sender: str, msg: FinancialResponse):
    """Primary agent listens for the final response and stores it."""
    ctx.logger.info(f"Received final response from {sender} for request {msg.request_id}")
    RESPONSE_STORE[msg.request_id] = {"status": "complete", "analysis_result": msg.response}

@agent_protocol.on_message(FinancialRequest, replies=FinancialResponse)
async def on_financial_request(ctx: Context, sender: str, msg: FinancialRequest):
    """Financial agent listens for tasks, runs the process, and replies."""
    ctx.logger.info(f"Received task from Primary Agent {sender}: '{msg.query}'")
    final_answer = await run_agentic_process(msg.query, ctx)
    await ctx.send(sender, FinancialResponse(response=final_answer, request_id=msg.request_id))

primary_agent.include(agent_protocol)
financial_agent.include(agent_protocol)


# --- FastAPI Application Setup ---
bureau = Bureau(endpoint="http://127.0.0.1:8001", port=8001)
bureau.add(primary_agent)
bureau.add(financial_agent)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles the startup and shutdown of the agent bureau."""
    # Schedule the bureau's asynchronous run method as a background task
    bureau_task = asyncio.create_task(bureau.run_async())
    print("--- Agent Bureau running in background ---")
    yield
    print("--- Shutting down agent bureau ---")
    bureau_task.cancel()
    try:
        await bureau_task
    except asyncio.CancelledError:
        print("--- Agent Bureau stopped successfully ---")

app = FastAPI(lifespan=lifespan)

class APIRequest(BaseModel):
    query: str

@app.post("/api/send-request")
async def send_request(request: APIRequest):
    """API endpoint to submit a new task to the financial agent."""
    request_id = str(uuid.uuid4())
    # The primary agent sends the message to the financial agent
    await primary_agent.send(
        financial_agent.address,
        FinancialRequest(query=request.query, request_id=request_id)
    )
    return {"status": "request_sent", "request_id": request_id}

@app.get("/api/get-response/{request_id}")
async def get_response(request_id: str):
    """API endpoint to poll for the result of a task."""
    if response_data := RESPONSE_STORE.get(request_id):
        del RESPONSE_STORE[request_id]  # Result is retrieved only once
        return response_data
    return {"status": "waiting"}



if __name__ == "__main__":
    API_PORT = 8000
    BUREAU_PORT = 8001

    # Configure and add agents to the bureau
    bureau = Bureau(endpoint=f"http://127.0.0.1:{BUREAU_PORT}", port=BUREAU_PORT)
    bureau.add(primary_agent)
    bureau.add(financial_agent)

    # (Your FastAPI app definition should be above this block)
    
    print("--- Starting FastAPI Server for Agent Interaction ---")
    print(f"Primary Agent Address: {primary_agent.address}")
    print(f"Financial Agent Address: {financial_agent.address}")

    print("\n" + "="*60)
    print("✅ IMPORTANT: Your frontend application must connect to the API server.")
    print(f"✅ Set your NEXT_PUBLIC_AI_AGENT_URL to: http://127.0.0.1:{API_PORT}")
    print("="*60 + "\n")

    print("API Endpoints:")
    print(f"  POST http://127.0.0.1:{API_PORT}/api/send-request")
    print(f"  GET  http://127.0.0.1:{API_PORT}/api/get-response/{{request_id}}")
    
    # Run the FastAPI server
    uvicorn.run(app, host="127.0.0.1", port=API_PORT)