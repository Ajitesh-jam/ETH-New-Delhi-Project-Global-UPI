# #!/usr/bin/env python3
# """
# An advanced ASI:One agent that updates its knowledge graph with real-time data,
# reasons over it to find the optimal path, then executes the transaction.
# """
# import os
# import json
# import requests
# import dotenv
# import uuid
# from hyperon import MeTTa

# from knowledge import initialize_financial_knowledge_graph
# from financerag import FinancialRAG

# # --- Initialization ---
# dotenv.load_dotenv()
# metta = MeTTa()
# initialize_financial_knowledge_graph(metta)
# financial_rag = FinancialRAG(metta)

# BASE_URL = "https://api.asi1.ai/v1"
# API_KEY = os.getenv("ASI_ONE_API_KEY")
# MODEL = "asi1-mini"
# session_id = str(uuid.uuid4())
# headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-Session-Id": session_id}

# # --- Tool Definitions ---

# def fetch_and_update_realtime_rates() -> str:
#     """
#     Fetches the latest currency conversion rates from an external API (simulated)
#     and updates the agent's knowledge graph with this new information.
#     """
#     print("[TOOL LOG] Fetching real-time rates from external API...")
#     # In a real app, this would be an actual API call, e.g., to CoinGecko.
#     mock_api_response = {
#         "INR-ETH": 1 / 285000.0, # Price of ETH has changed
#         "ETH-USD": 3550.0,       # Price of ETH has changed
#         "INR-MATIC": 1 / 58.0,   # Price of MATIC has changed
#         "MATIC-USD": 0.72,       # Price of MATIC has changed
#     }
    
#     for pair, rate in mock_api_response.items():
#         from_curr, to_curr = pair.split('-')
#         financial_rag.update_rate(from_curr, to_curr, rate)
        
#     return json.dumps({"status": "success", "message": "Knowledge graph updated with latest market rates."})

# def find_best_conversion_path(from_currency: str, to_currency: str) -> str:
#     """Finds the most cost-effective intermediate currency for a conversion."""
#     print(f"[TOOL LOG] Finding best path from {from_currency} to {to_currency}...")
#     path = financial_rag.find_best_path(from_currency.upper(), to_currency.upper())
#     if path: return json.dumps({"status": "success", "best_path_via": path})
#     return json.dumps({"status": "error", "message": "No valid conversion path found."})

# def convert_and_transfer(from_currency: str, to_currency: str, from_address: str, to_address: str, amount: float) -> str:
#     """Simulates a conversion using the latest rates from the knowledge graph."""
#     rate = financial_rag.get_exchange_rate(from_currency.upper(), to_currency.upper())
#     if rate is None: return json.dumps({"status": "error", "message": f"No rate found for {from_currency}->{to_currency}."})
#     output_amount = amount * rate
#     print(f"[TOOL LOG] Converting {amount:.2f} {from_currency} to {output_amount:.6f} {to_currency}...")
#     return json.dumps({"status": "success", "amount_in": amount, "amount_out": output_amount})

# # --- Tool Schemas for the Model ---
# # --- Tool Schemas for the Model ---
# update_rates_func = {
#     "type": "function",
#     "function": {
#         "name": "fetch_and_update_realtime_rates",
#         "description": "Use this tool first to get the latest market conversion rates before making any decisions.",
#         "parameters": {
#             "type": "object",
#             "properties": {},
#             "required": []
#         }
#     }
# }
# find_best_path_func = {
#     "type": "function",
#     "function": {
#         "name": "find_best_conversion_path",
#         "description": "After getting rates, use this tool to find the cheapest conversion path.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "from_currency": {"type": "string", "description": "The source currency code (e.g., 'INR')."},
#                 "to_currency": {"type": "string", "description": "The final target currency code (e.g., 'USD')."}
#             },
#             "required": ["from_currency", "to_currency"]
#         }
#     }
# }
# convert_func = {
#     "type": "function",
#     "function": {
#         "name": "convert_and_transfer",
#         "description": "Converts an amount from a source to a target currency. Use this for each step of the path.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "from_currency": {"type": "string", "description": "The source currency for this specific conversion step (e.g., 'INR', 'ETH')."},
#                 "to_currency": {"type": "string", "description": "The target currency for this specific conversion step (e.g., 'ETH', 'USD')."},
#                 "from_address": {"type": "string", "description": "Sender's account identifier."},
#                 "to_address": {"type": "string", "description": "Receiver's account identifier."},
#                 "amount": {"type": "number", "description": "The amount in the source currency to be converted."}
#             },
#             "required": ["from_currency", "to_currency", "from_address", "to_address", "amount"]
#         }
#     }
# }


# # --- Main Conversation Logic ---
# def run_conversation():
#     messages = [
#         {"role": "system", "content": "You are an intelligent financial agent. Your goal is to execute a currency conversion from INR to USD. You MUST follow this plan: 1. Call `fetch_and_update_realtime_rates` to get current data. 2. Call `find_best_conversion_path` to choose the optimal route. 3. Create a plan to call `convert_and_transfer` for each leg of the journey (e.g., INR->best_path, best_path->USD)."},
#         {"role": "user", "content": "I need to pay a US merchant $1200 from my Indian account '0xIndianAccount'. The merchant's account is '0xUSMerchant'. Please find the cheapest way to do this and handle the transaction. Remember to update your knowledge with the latest rates first! Also help me do the transaction like from the best path convert my inr to cheaptest crypto and given buy usd from crypto and send in to merchant"}
#     ]

#     print("--- 1. Sending initial request to the model ---")
#     payload = {
#         "model": MODEL, 
#         "messages": messages, 
#         "tools": [update_rates_func, find_best_path_func, convert_func],
#         "tool_choice": "auto"
#         }

    
#     try:
#         response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload).json()
#         print("\n--- 2. Received response from model ---")
#         print(json.dumps(response, indent=2))
        
#         response_message = response["choices"][0]["message"]
#         messages.append(response_message)
        
#         if not response_message.get("tool_calls"):
#             print("Model responded without tools.")
#             return

#         print("\n--- 3. Executing agent's plan ---")
#         tool_calls = response_message["tool_calls"]
#         tool_outputs = []
#         available_tools = {
#             "fetch_and_update_realtime_rates": fetch_and_update_realtime_rates,
#             "find_best_conversion_path": find_best_conversion_path,
#             "convert_and_transfer": convert_and_transfer
#         }

#         for call in tool_calls:
#             func_name = call["function"]["name"]
#             args = json.loads(call["function"]["arguments"])
#             tool_to_call = available_tools.get(func_name)
            
#             if tool_to_call:
#                 result = tool_to_call(**args)
#             else:
#                 result = json.dumps({"status": "error", "message": "Unknown tool."})
            
#             print(f"<--- Tool '{func_name}' returned: {result}")
#             tool_outputs.append({"tool_call_id": call["id"], "role": "tool", "name": func_name, "content": result})

#         messages.extend(tool_outputs)
        
#         print("\n--- 4. Sending tool outputs back for final response ---")
#         second_payload = {"model": MODEL, "messages": messages, "use_planner": True}
#         final_response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=second_payload).json()

#         print("\n--- 5. Received final user-facing response ---")
#         print(f"Assistant: {final_response['choices'][0]['message']['content']}")

#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")

# if __name__ == "__main__":
#     run_conversation()

#!/usr/bin/env python3
"""
An advanced ASI:One agent that iteratively executes a multi-step plan,
updating its knowledge graph and reasoning over it to complete a transaction.
"""
import os
import json
import requests
import dotenv
import uuid
from hyperon import MeTTa

from knowledge import initialize_financial_knowledge_graph
from financerag import FinancialRAG

# --- Initialization ---
dotenv.load_dotenv()
metta = MeTTa()
initialize_financial_knowledge_graph(metta)
financial_rag = FinancialRAG(metta)

BASE_URL = "https://api.asi1.ai/v1"
API_KEY = os.getenv("ASI_ONE_API_KEY")
MODEL = "asi1-mini"
session_id = str(uuid.uuid4())
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "X-Session-Id": session_id}

# --- Tool Definitions ---

def fetch_and_update_realtime_rates() -> str:
    """
    Fetches the latest currency conversion rates from an external API (simulated)
    and updates the agent's knowledge graph with this new information.
    """
    print("\n[TOOL LOG] Fetching real-time rates from external API...")
    mock_api_response = {
        "INR-ETH": 1 / 285000.0, "ETH-USD": 3550.0,
        "INR-MATIC": 1 / 58.0, "MATIC-USD": 0.72,
    }
    for pair, rate in mock_api_response.items():
        from_curr, to_curr = pair.split('-')
        financial_rag.update_rate(from_curr, to_curr, rate)
    return json.dumps({"status": "success", "message": "Knowledge graph updated with latest market rates."})

def find_best_conversion_path(from_currency: str, to_currency: str) -> str:
    """Finds the most cost-effective intermediate currency for a conversion."""
    print(f"\n[TOOL LOG] Finding best path from {from_currency} to {to_currency}...")
    path = financial_rag.find_best_path(from_currency.upper(), to_currency.upper())
    if path: return json.dumps({"status": "success", "best_path_via": path})
    return json.dumps({"status": "error", "message": "No valid conversion path found."})

def convert_and_transfer(from_currency: str, to_currency: str, from_address: str, to_address: str, amount: float) -> str:
    """Simulates a conversion using the latest rates from the knowledge graph."""
    rate = financial_rag.get_exchange_rate(from_currency.upper(), to_currency.upper())
    if rate is None: return json.dumps({"status": "error", "message": f"No rate found for {from_currency}->{to_currency}."})
    output_amount = amount * rate
    print(f"\n[TOOL LOG] Converting {amount:.2f} {from_currency} to {output_amount:.6f} {to_currency}...")
    return json.dumps({"status": "success", "amount_in": amount, "amount_out": output_amount})

# --- Tool Schemas for the Model ---
update_rates_func = {"type": "function","function": {"name": "fetch_and_update_realtime_rates","description": "Use this tool first to get the latest market conversion rates before making any decisions.","parameters": {"type": "object","properties": {},"required": []}}}
find_best_path_func = {"type": "function","function": {"name": "find_best_conversion_path","description": "After getting rates, use this tool to find the cheapest conversion path.","parameters": {"type": "object","properties": {"from_currency": {"type": "string","description": "The source currency code (e.g., 'INR')."},"to_currency": {"type": "string","description": "The final target currency code (e.g., 'USD')."}},"required": ["from_currency", "to_currency"]}}}
convert_func = {"type": "function","function": {"name": "convert_and_transfer","description": "Converts an amount from a source to a target currency. Use this for each step of the path.","parameters": {"type": "object","properties": {"from_currency": {"type": "string","description": "The source currency for this specific conversion step (e.g., 'INR', 'ETH')."},"to_currency": {"type": "string","description": "The target currency for this specific conversion step (e.g., 'ETH', 'USD')."},"from_address": {"type": "string","description": "Sender's account identifier."},"to_address": {"type": "string","description": "Receiver's account identifier."},"amount": {"type": "number","description": "The amount in the source currency to be converted."}},"required": ["from_currency", "to_currency", "from_address", "to_address", "amount"]}}}

# --- Main Conversation Logic ---
def run_conversation():
    messages = [
        {"role": "system", "content": "You are an intelligent financial agent. Your goal is to execute a currency conversion from INR to USD. You MUST follow this plan: 1. Call `fetch_and_update_realtime_rates` to get current data. 2. Call `find_best_conversion_path` to choose the optimal route. 3. Create a plan to call `convert_and_transfer` for each leg of the journey (e.g., INR->best_path, and best_path->USD). You must reason about the amounts for each step."},

        {"role": "user", "content": "I need to pay a US merchant $1200 from my Indian account '0xIndianAccount'. The merchant's account is '0xUSMerchant'. Please find the cheapest way to do this and handle the transaction. Remember to update your knowledge with the latest rates first! Also help me do the transaction like from the best path convert my inr to cheaptest crypto and given buy usd from crypto and send in to merchant"}
    ]
    
    available_tools = {
        "fetch_and_update_realtime_rates": fetch_and_update_realtime_rates,
        "find_best_conversion_path": find_best_conversion_path,
        "convert_and_transfer": convert_and_transfer
    }
    
    max_turns = 5 # Safety break to prevent infinite loops
    turn_count = 0

    while turn_count < max_turns:
        turn_count += 1
        print(f"\n--- Turn {turn_count} ---")

        try:
            payload = {"model": MODEL, "messages": messages, "tools": [update_rates_func, find_best_path_func, convert_func], "use_planner": True}
            response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            response_json = response.json()

            if "choices" not in response_json or not response_json["choices"]:
                print("\n[ERROR] Invalid response from API:", response_json.get("message", "No choices returned."))
                break
            
            response_message = response_json["choices"][0]["message"]
            messages.append(response_message)
            
            # Check if the agent is done and providing a final answer
            if not response_message.get("tool_calls"):
                print("\n--- Final Response ---")
                print(f"Assistant: {response_message.get('content')}")
                break

            # If there are tool calls, execute them
            print(f"Agent wants to use tools: {[call['function']['name'] for call in response_message['tool_calls']]}")
            tool_outputs = []
            for call in response_message["tool_calls"]:
                func_name = call["function"]["name"]
                args = json.loads(call["function"]["arguments"])
                tool_to_call = available_tools.get(func_name)
                
                if tool_to_call:
                    result = tool_to_call(**args)
                else:
                    result = json.dumps({"status": "error", "message": f"Unknown tool: {func_name}"})
                
                tool_outputs.append({"tool_call_id": call["id"], "role": "tool", "name": func_name, "content": result})

            messages.extend(tool_outputs)

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} {e.response.reason}")
            print(f"Response Body: {e.response.text}")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

if __name__ == "__main__":
    run_conversation()

