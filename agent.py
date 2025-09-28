"""
An advanced ASI:One agent that iteratively executes a multi-step financial plan,
updating its knowledge graph and reasoning over it to complete a transaction.
This version is corrected for logical errors and architectural soundness.
"""
import os
import json
import uuid
import requests
from datetime import datetime

# --- Placeholder Imports for Custom Modules ---
from payment_gateway import pay_inr
from payment_sender import send_native

# --- uAgents Imports ---
from uagents import Agent, Context, Protocol, Bureau
from uagents.setup import fund_agent_if_low

# Import the Chat Protocol components for standardized communication
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,  # Correctly import the protocol instance
)

# --- Knowledge Graph & RAG Imports ---
from hyperon import MeTTa
from knowledge import initialize_financial_knowledge_graph
from financerag import FinancialRAG

# --- Initialization ---
import dotenv
dotenv.load_dotenv()

metta = MeTTa()
initialize_financial_knowledge_graph(metta)
financial_rag = FinancialRAG(metta)

# --- API and Pool Configuration ---
API_KEY = os.getenv("ASI_ONE_API_KEY")
if not API_KEY:
    raise ValueError("ASI_ONE_API_KEY not found in environment variables. Please create a .env file.")

BASE_URL = "https://api.asi1.ai/v1"
MODEL = "asi1-mini"

# These addresses represent the system's operational accounts/pools
INDIAN_BANK_POOL = os.getenv("INDIAN_BANK_POOL")
INDIAN_CRYPTO_POOL = os.getenv("INDIAN_CRYPTO_POOL")
USA_CRYPTO_POOL = os.getenv("USA_CRYPTO_POOL")
USA_BANK_POOL = os.getenv("USA_USD_ACCOUNT")

if not all([INDIAN_CRYPTO_POOL, INDIAN_BANK_POOL, USA_CRYPTO_POOL, USA_BANK_POOL]):
    raise ValueError("Pool addresses (INDIAN_CRYPTO_POOL, INDIAN_BANK_POOL, USA_CRYPTO_POOL, USA_BANK_POOL) must be set in .env file.")

# --- Tool Definitions ---
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

# --- Tool Schemas for the Model ---
tools_schema = [
    {"type": "function", "function": {"name": "multiply", "description": "Multiplies two numbers.", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
    {"type": "function", "function": {"name": "fetch_and_update_realtime_rates", "description": "Use this tool first to get the latest market conversion rates before making any decisions.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "find_best_conversion_path", "description": "After getting rates, use this to find the cheapest crypto path between two fiat currencies.", "parameters": {"type": "object", "properties": {"from_currency": {"type": "string", "description": "The source currency code (e.g., 'INR')."}, "to_currency": {"type": "string", "description": "The final target currency code (e.g., 'USD')."}}, "required": ["from_currency", "to_currency"]}}},
    {"type": "function", "function": {"name": "convert_and_transfer", "description": "Executes a single conversion and transfer step. Use this for each leg of the journey.", "parameters": {"type": "object", "properties": {"from_currency": {"type": "string", "description": "The source currency for this step (e.g., 'INR', 'ETH')."}, "to_currency": {"type": "string", "description": "The target currency for this step (e.g., 'ETH', 'USD')."}, "from_address": {"type": "string", "description": "Sender's account identifier for this step."}, "to_address": {"type": "string", "description": "Receiver's account identifier for this step."}, "amount": {"type": "number", "description": "The amount in the source currency."}}, "required": ["from_currency", "to_currency", "from_address", "to_address", "amount"]}}}
]

# --- Main Conversation Logic ---
# def process_request(messages: list, session_id: str) -> list:
#     """
#     Runs one turn of the agentic loop: sends messages to the API,
#     executes tools if requested, and returns the updated message history.
#     """
#     available_tools = {
#         "fetch_and_update_realtime_rates": fetch_and_update_realtime_rates,
#         "find_best_conversion_path": find_best_conversion_path,
#         "convert_and_transfer": convert_and_transfer,
#         "multiply": multiply
#     }
#     headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-Session-Id": session_id}

#     try:
#         payload = {"model": MODEL, "messages": messages, "tools": tools_schema}
#         response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=90)
#         response.raise_for_status()
#         response_json = response.json()

#         if not response_json.get("choices"):
#             raise ValueError(f"Invalid API response: {response_json.get('message', 'No choices returned.')}")
        
#         response_message = response_json["choices"][0]["message"]
#         messages.append(response_message)
        
#         if response_message.get("tool_calls"):
#             print(f"Agent wants to use tools: {[call['function']['name'] for call in response_message['tool_calls']]}")
#             tool_outputs = []
#             for call in response_message["tool_calls"]:
#                 func_name = call["function"]["name"]
#                 args_str = call["function"].get("arguments", "{}")
#                 args = json.loads(args_str) if args_str else {}
                
#                 tool_to_call = available_tools.get(func_name)
#                 result = tool_to_call(**args) if tool_to_call else json.dumps({"status": "error", "message": f"Unknown tool: {func_name}"})
                
#                 tool_outputs.append({"tool_call_id": call["id"], "role": "tool", "name": func_name, "content": result})
#             messages.extend(tool_outputs)

#     except requests.exceptions.HTTPError as e:
#         error_message = f"HTTP Error: {e.response.status_code} - {e.response.text}"
#         print(f"[ERROR] {error_message}")
#         # Append an error message for the agent to see and return the list
#         messages.append({"role": "system", "content": f"An error occurred: {error_message}"})
#         return messages
#     except Exception as e:
#         error_message = f"An unexpected error occurred: {e}"
#         print(f"[ERROR] {error_message}")
#         messages.append({"role": "system", "content": f"An error occurred: {error_message}"})
#         return messages
    
#     return messages


# --- Stateful Conversation Class ---
class StatefulAgentConversation:
    """Manages the state and interaction loop for an agent conversation."""
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.messages = [
            {"role": "system", "content": f"You are an intelligent financial agent that executes tasks without asking for confirmation. Your goal is to execute currency conversions. You MUST follow this plan: 1. `fetch_and_update_realtime_rates`. 2. `find_best_conversion_path`. 3. Reason about amounts and create a 3-step execution plan using `convert_and_transfer` for each leg: a) User INR payment to the Indian bank '{INDIAN_BANK_POOL}'. b) A crypto transfer from the Indian crypto pool '{INDIAN_CRYPTO_POOL}' to the US crypto pool '{USA_CRYPTO_POOL}'. c) A final USD payout from the US bank pool '{USA_BANK_POOL}' to the merchant. Execute the full plan, then give a summary. If any step fails after user payment, refund the user from '{INDIAN_BANK_POOL}'."}
        ]
        self.available_tools = {
            "fetch_and_update_realtime_rates": fetch_and_update_realtime_rates,
            "find_best_conversion_path": find_best_conversion_path,
            "convert_and_transfer": convert_and_transfer,
            "multiply": multiply
        }

    def process_request(self):
        """Runs one turn of the agentic loop."""
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-Session-Id": self.session_id}
        try:
            payload = {"model": MODEL, "messages": self.messages, "tools": tools_schema}
            response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=90)
            response.raise_for_status()
            response_message = response.json()["choices"][0]["message"]
            self.messages.append(response_message)
            
            if tool_calls := response_message.get("tool_calls"):
                print(f"Agent wants to use tools: {[call['function']['name'] for call in tool_calls]}")
                tool_outputs = []
                for call in tool_calls:
                    func_name = call["function"]["name"]
                    args = json.loads(call["function"].get("arguments", "{}"))
                    tool_to_call = self.available_tools.get(func_name)
                    result = tool_to_call(**args) if tool_to_call else json.dumps({"status": "error", "message": f"Unknown tool: {func_name}"})
                    tool_outputs.append({"tool_call_id": call["id"], "role": "tool", "name": func_name, "content": str(result)})
                self.messages.extend(tool_outputs)
        except requests.exceptions.HTTPError as e:
            error_message = f"HTTP Error: {e.response.status_code} - {e.response.text}"
            print(f"[ERROR] {error_message}")
            self.messages.append({"role": "system", "content": f"An error occurred: {error_message}"})
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            print(f"[ERROR] {error_message}")
            self.messages.append({"role": "system", "content": f"An error occurred: {error_message}"})

    def send_message(self, user_prompt: str):
        """Sends a user prompt to the agent and processes the conversation."""
        print(f"\nUser: {user_prompt}")
        self.messages.append({"role": "user", "content": user_prompt})
        
        max_turns = 10
        for turn in range(max_turns):
            print(f"\n--- Turn {turn + 1} ---")
            self.process_request()
            
            last_message = self.messages[-1]
            if last_message["role"] == "assistant" and not last_message.get("tool_calls"):
                print("\n--- Final Response ---")
                print(f"Assistant: {last_message.get('content')}")
                return
            
# --- uAgent Definition with Chat Protocol ---
agent = Agent(name="financial_agent", seed="2_financial_agent_secret_phrase")
fund_agent_if_low(agent.wallet.address())
chat_proto = Protocol("FinancialTransactionChat", spec=chat_protocol_spec)

@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id))
    
    user_query = "".join(item.text for item in msg.content if isinstance(item, TextContent))
    ctx.logger.info(f"Received transaction request from {sender}: '{user_query}'")

    session_id = str(uuid.uuid4())
    messages = [
        {"role": "system", "content": f"You are an intelligent financial agent and don't ask confirmations. Your goal is to execute a currency conversion from INR to USD. You MUST follow this plan: 1. `fetch_and_update_realtime_rates`. 2. `find_best_conversion_path`. 3. Reason about the required amounts and create a 3-step execution plan using `convert_and_transfer` for each leg: a) User INR payment to the Indian pool address '{INDIAN_BANK_POOL}'. b) A crypto transfer from the Indian pool '{INDIAN_CRYPTO_POOL}' to the US pool '{USA_CRYPTO_POOL}' by calling the tool convert_and_transfer. c) A final USD payout from the US pool '{USA_CRYPTO_POOL}' to the merchant. Execute this plan until the final payment is made, then give a summary. And also if there is any error after transaction from User, just return his money back by transfering equivalent money to User account from {INDIAN_BANK_POOL}"},
        {"role": "user", "content": user_query}
    ]
    
    max_turns = 6 # Increased max turns for multi-step execution
    for turn in range(max_turns):
        ctx.logger.info(f"--- Agent Turn {turn + 1} ---")
        messages = process_request(messages, session_id)
        
        # Add a check to ensure messages is not None before proceeding
        if messages is None:
            ctx.logger.error("process_request returned None. Aborting turn.")
            break
            
        last_message = messages[-1]
        if last_message["role"] == "assistant" and not last_message.get("tool_calls"):
            final_answer = last_message.get('content', "Process complete.")
            ctx.logger.info(f"--- Final Response ---\nAssistant: {final_answer}")
            await ctx.send(sender, ChatMessage(timestamp=datetime.utcnow(), msg_id=uuid.uuid4(), content=[TextContent(text=final_answer), EndSessionContent()]))
            return

    # If the loop finishes without a final answer
    timeout_msg = "The process took too long and has timed out."
    ctx.logger.warning(timeout_msg)
    await ctx.send(sender, ChatMessage(timestamp=datetime.utcnow(), msg_id=uuid.uuid4(), content=[TextContent(text=timeout_msg), EndSessionContent()]))

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")
    
agent.include(chat_proto, publish_manifest=True)

# def run_standalone_conversation():
#     print("--- Running Standalone Test Conversation ---")
#     session_id = str(uuid.uuid4())
#     messages = [
#         {"role": "system", "content": f"You are an intelligent financial agent. Your goal is to execute a currency conversion from INR to USD. You MUST follow this plan: 1. `fetch_and_update_realtime_rates`. 2. `find_best_conversion_path`. 3. Reason about the required amounts and create a 3-step execution plan using `convert_and_transfer` for each leg: a) User INR payment to the Indian bank account '{INDIAN_BANK_POOL}'. b) A crypto transfer from the Indian pool '{INDIAN_CRYPTO_POOL}' to the US pool '{USA_CRYPTO_POOL}'. c) A final USD payout from the US pool '{USA_CRYPTO_POOL}' to the merchant. Execute this plan until the final payment is made, then give a summary."},
#         {"role": "user", "content": "I need to pay a US merchant 10 ruppees from my Indian account '0xPayerBank'. The merchant's account is '0xUSMerchantBank'. Please find the cheapest way to do this and handle the transaction."}
#     ]
#     max_turns = 10 # Increased max turns for the 3-step execution
#     for turn in range(max_turns):
#         print(f"\n--- Turn {turn + 1} ---")
#         updated_messages = process_request(messages, session_id)
        
#         if updated_messages is None:
#             print("[ERROR] process_request returned None. Aborting conversation.")
#             break
        
#         messages = updated_messages
#         last_message = messages[-1]
#         if last_message["role"] == "assistant" and not last_message.get("tool_calls"):
#             print("\n--- Final Response ---")
#             print(f"Assistant: {last_message.get('content')}")
#             break

if __name__ == "__main__":
    # run_standalone_conversation()
    print("--- Starting Interactive Agent Conversation ---")
    conversation = StatefulAgentConversation()
    while True:
        try:
            prompt = input("You: ")
            if prompt.lower() in ["exit", "quit"]:
                break
            conversation.send_message(prompt)
        except KeyboardInterrupt:
            print("\nExiting.")
            break

