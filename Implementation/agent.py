
# """Minimal CLI for ASI:One agentic model with 5-second polling."""
# import os
# import uuid
# import json
# import sys
# import time
# import requests
# import dotenv
# dotenv.load_dotenv()

# BASE_URL = "https://api.asi1.ai/v1"
# API_KEY = os.getenv("ASI_ONE_API_KEY") 
# ENDPOINT = "https://api.asi1.ai/v1/chat/completions"
# MODEL = "asi1-fast-agentic"
# TIMEOUT = 90  # single request timeout in seconds


# BASE_URL = "https://api.asi1.ai/v1"
# API_KEY = os.getenv("ASI_ONE_API_KEY")
# MODEL = "asi1-fast-agentic"

# if not API_KEY:
#     raise ValueError("ASI_ONE_API_KEY not found in environment variables. Please create a .env file.")

# # Generate a unique session ID for this conversation run
# session_id = str(uuid.uuid4())

# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json",
#     "X-Session-Id": session_id
# }

# Available_currency_to_swap = ["eth","polygon"]

# SESSION_MAP: dict[str, str] = {}

# def get_session_id(conv_id: str) -> str:
#     sid = SESSION_MAP.get(conv_id)
#     if sid is None:
#         sid = str(uuid.uuid4())
#         SESSION_MAP[conv_id] = sid
#     return sid

# def ask(conv_id: str, messages: list[dict], *, stream: bool = False) -> str:
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "x-session-id": get_session_id(conv_id),
#         "Content-Type": "application/json",
#     }
#     payload = {"model": MODEL, "messages": messages, "stream": stream}

#     if not stream:
#         resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=TIMEOUT)
#         resp.raise_for_status()
#         return resp.json()["choices"][0]["message"]["content"]

#     # Streaming
#     with requests.post(ENDPOINT, headers=headers, json=payload, timeout=TIMEOUT, stream=True) as resp:
#         resp.raise_for_status()
#         full = ""
#         for line in resp.iter_lines(decode_unicode=True):
#             if not line or not line.startswith("data: "):
#                 continue
#             chunk = line.removeprefix("data: ")
#             if chunk == "[DONE]":
#                 break
#             try:
#                 delta = json.loads(chunk)["choices"][0]["delta"]
#                 token = delta.get("content", "")
#                 sys.stdout.write(token)
#                 sys.stdout.flush()
#                 full += token
#             except Exception:
#                 continue
#         print()
#         return full

# def poll_for_async_reply(conv_id: str, history: list[dict], *, wait_sec: int = 5, max_attempts: int = 24) -> str | None:
#     """Every `wait_sec` seconds send "Any update?" until the assistant reply changes."""
#     for attempt in range(max_attempts):
#         time.sleep(wait_sec)
#         print(f"polling (attempt {attempt + 1}) …")
#         update_prompt = {"role": "user", "content": "Any update?"}
#         latest = ask(conv_id, history + [update_prompt])
#         if latest and latest.strip() != history[-1]["content"].strip():
#             return latest
#     return None

# # --- Single, Generic Tool Definition ---
# # --- Tool Definition ---
# def convert_and_transfer(from_currency: str, to_currency: str, from_address: str, to_address: str, amount: float) -> str:
#     """
#     Simulates the conversion and transfer between two currencies.
#     """
#     # In a real system, these rates would come from a live oracle or API
#     eth_price_inr = 280000.0
#     eth_price_usd = 3400.0
    
#     poly_price_inr = 200.0
#     poly_price_usd = 2.5
    
#     output_amount = 0.0
    
#     # Define conversion logic
#     if from_currency.upper() == "INR" and to_currency.upper() == "ETH":
#         output_amount = amount / eth_price_inr
#     elif from_currency.upper() == "ETH" and to_currency.upper() == "USD":
#         output_amount = amount * eth_price_usd
#     elif from_currency.upper() == "INR" and to_currency.upper() == "POLYGON":
#         output_amount = amount / poly_price_inr
#     elif from_currency.upper() == "POLYGON" and to_currency.upper() == "USD":
#         output_amount = amount * poly_price_usd    
#     else:
#         return json.dumps({
#             "status": "error",
#             "message": f"Conversion from {from_currency} to {to_currency} is not supported."
#         })

#     print(f"[TOOL LOG] Converting {amount:.2f} {from_currency} to {output_amount:.6f} {to_currency}...")
    
#     return json.dumps({
#         "status": "success",
#         "from_currency": from_currency,
#         "to_currency": to_currency,
#         "amount_in": amount,
#         "amount_out": output_amount
#     })

# # --- Single Tool Schema for the Model ---
# convert_and_transfer_func = {
#     "type": "function",
#     "function": {
#         "name": "convert_and_transfer",
#         "description": "Converts an amount from a source currency to a target currency and simulates the transfer.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "from_currency": {"type": "string", "description": "The source currency code (e.g., 'INR', 'ETH')."},
#                 "to_currency": {"type": "string", "description": "The target currency code (e.g., 'ETH', 'USD')."},
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
#     """
#     Manages the conversation flow, including making API calls and executing the single tool.
#     """
#     available_tools = {
#         "convert_and_transfer": convert_and_transfer
#     }

#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are an expert currency exchange agent. You have one tool, `convert_and_transfer`. "
#                 "To handle a complex request like converting INR to USD, you must create a plan to chain tool calls. First, call the tool to convert INR to an intermediate currency, ETH. Then, use the output amount from that first call as the input `amount` for a second call to the same tool to convert ETH to USD."
#             )
#         },
#         {
#             "role": "user",
#             "content": "I am in India and I need to pay a merchant in the US $1200. My account is '0xIndianAccount' and the merchant's is '0xUSMerchant'. Please handle the transaction."
#         }
#     ]

#     print("--- 1. Sending initial request to the model ---")
#     print(f"User Prompt: {messages[-1]['content']}")

#     payload = {
#         "model": MODEL,
#         "messages": messages,
#         "tools": [convert_and_transfer_func], # Only provide the single tool
#         "tool_choice": "auto",
#     }
    
#     print(f"1. Payload: {json.dumps(payload, indent=2)}")
    

#     try:
        
#         response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
#         response.raise_for_status()
#         response_json = response.json()
        

#         print("\n--- 2. Received response from the model ---")
#         print(json.dumps(response_json, indent=2))

#         response_message = response_json["choices"][0]["message"]
#         messages.append(response_message)

#         if not response_message.get("tool_calls"):
#             print("\n--- Model responded directly without using a tool. ---")
#             print(f"Assistant: {response_message['content']}")
#             return

#         print("\n--- 3. Model decided to use the tool. Executing plan now. ---")
        
#         tool_calls = response_message["tool_calls"]
#         tool_outputs = []
#         intermediate_amount = None

#         # The planner should call the tool twice. We need to execute them in order.
#         # First, find and execute the INR -> ETH call
#         for tool_call in tool_calls:
#             args = json.loads(tool_call["function"]["arguments"])
#             if args.get("from_currency") == "INR" and args.get("to_currency") == "ETH":
#                 function_response_json = convert_and_transfer(**args)
#                 print(f"<--- Tool call (INR->ETH) returned: {function_response_json}")
#                 tool_outputs.append({
#                     "tool_call_id": tool_call["id"], "role": "tool", "name": "convert_and_transfer", "content": function_response_json
#                 })
#                 # Extract the crucial output amount for the next step
#                 intermediate_amount = json.loads(function_response_json).get("amount_out")

#         # Next, find and execute the ETH -> USD call
#         for tool_call in tool_calls:
#             args = json.loads(tool_call["function"]["arguments"])
#             if args.get("from_currency") == "ETH" and args.get("to_currency") == "USD":
#                 if intermediate_amount is None:
#                     print("[ERROR] Cannot run ETH->USD step, the intermediate amount was not calculated.")
#                     continue
#                 # Inject the calculated amount from the first step
#                 args["amount"] = intermediate_amount
#                 function_response_json = convert_and_transfer(**args)
#                 print(f"<--- Tool call (ETH->USD) returned: {function_response_json}")
#                 tool_outputs.append({
#                     "tool_call_id": tool_call["id"], "role": "tool", "name": "convert_and_transfer", "content": function_response_json
#                 })
        
#         messages.extend(tool_outputs)

#         if response_message.get("content"):
#              print("\n--- 5. Planner provided a final response. ---")
#              print(f"Assistant: {response_message['content']}")
#              return

#         print("\n--- 4. Sending tool outputs back to the model for a final answer ---")
#         second_payload = {"model": MODEL, "messages": messages, "use_planner": True}
#         second_response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=second_payload)
#         second_response.raise_for_status()

#         final_response_json = second_response.json()
#         final_answer = final_response_json["choices"][0]["message"]["content"]

#         print("\n--- 5. Received final, user-facing response ---")
#         print(f"Assistant: {final_answer}")

#     except requests.exceptions.HTTPError as e:
#         print(f"HTTP Error: {e.response.status_code} {e.response.reason}")
#         print(f"Response Body: {e.response.text}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")

    

# if __name__ == "__main__":
#     conv_id = str(uuid.uuid4())
#     history: list[dict] = [
#         {"role": "user", "content": "Discover a model which best answers the query regarding crypto buy signals today and fetch what will be the lowest price to buy ethereum and polygon today?"}
#     ]

#     # First request – stream tokens so the user sees progress immediately
#     first_reply = ask(conv_id, history, stream=True)
#     history.append({"role": "assistant", "content": first_reply})

#     # If the model reports it has delegated the task, start polling
#     if first_reply.strip() == "I've sent the message":
#         final_reply = poll_for_async_reply(conv_id, history)
#         if final_reply:
#             print("\n[Agentverse agent reply]\n" + final_reply)
    
#     #based on the reply use the tool to swap between eth or polygon
    
#     run_conversation()        





"""
An advanced agent that can reason and choose the most cost-effective 
cryptocurrency for a cross-border transaction.
"""
import os
import uuid
import json
import requests
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
API_KEY = os.getenv("ASI_ONE_API_KEY")
BASE_URL = "https://api.asi1.ai/v1"
MODEL = "asi1-fast-agentic"
ENDPOINT = f"{BASE_URL}/chat/completions"

if not API_KEY:
    raise ValueError("ASI_ONE_API_KEY not found in environment variables. Please create a .env file.")

# --- Tool Definition ---
def convert_and_transfer(from_currency: str, to_currency: str, amount: float, from_address: str = "N/A", to_address: str = "N/A") -> str:
    """
    Performs a currency conversion. Can be used for calculations or to simulate transfers.
    Available currencies: INR, USD, ETH, POLYGON.
    """
    # In a real system, these rates would come from a live oracle (like The Graph Substream)
    eth_price_inr = 280000.0
    eth_price_usd = 3400.0
    poly_price_inr = 60.0  # Example price for Polygon (MATIC)
    poly_price_usd = 0.70 # Example price for Polygon (MATIC)
    
    output_amount = 0.0
    conversion_path = f"{from_currency.upper()}->{to_currency.upper()}"
    
    print(f"[TOOL LOG] Executing conversion for {amount:.4f} {from_currency.upper()} to {to_currency.upper()}...")

    # Expanded dictionary to handle all paths, including reverse calculations
    supported_conversions = {
        # Forward paths
        "INR->ETH": amount / eth_price_inr,
        "ETH->USD": amount * eth_price_usd,
        "INR->POLYGON": amount / poly_price_inr,
        "POLYGON->USD": amount * poly_price_usd,
        # Reverse paths for calculation
        "USD->ETH": amount / eth_price_usd,
        "ETH->INR": amount * eth_price_inr,
        "USD->POLYGON": amount / poly_price_usd,
        "POLYGON->INR": amount * poly_price_inr,
    }

    if conversion_path in supported_conversions:
        output_amount = supported_conversions[conversion_path]
        return json.dumps({
            "status": "success",
            "message": f"Converted {amount:.4f} {from_currency.upper()} to {output_amount:.6f} {to_currency.upper()}.",
            "amount_in": amount,
            "amount_out": output_amount
        })
    else:
        return json.dumps({
            "status": "error",
            "message": f"Conversion from {from_currency.upper()} to {to_currency.upper()} is not supported."
        })

# --- Tool Schema for the Model ---
convert_and_transfer_schema = {
    "type": "function",
    "function": {
        "name": "convert_and_transfer",
        "description": "Converts an amount from a source currency to a target currency. Use this for both calculations and simulating transfers.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_currency": {"type": "string", "description": "The source currency code (e.g., 'INR', 'ETH', 'USD', 'POLYGON')."},
                "to_currency": {"type": "string", "description": "The target currency code (e.g., 'ETH', 'USD', 'INR', 'POLYGON')."},
                "amount": {"type": "number", "description": "The amount in the source currency to be converted."},
                "from_address": {"type": "string", "description": "Sender's account identifier. Can be 'N/A' for pure calculations."},
                "to_address": {"type": "string", "description": "Receiver's account identifier. Can be 'N/A' for pure calculations."}
            },
            "required": ["from_currency", "to_currency", "amount"]
        }
    }
}

# --- Main Conversation Logic ---
def run_conversation():
    """
    Manages the conversation loop, allowing the agent to reason, compare, 
    and execute a multi-step plan.
    """
    session_id = str(uuid.uuid4())
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-Session-Id": session_id
    }
    
    # The available cryptocurrencies for the agent to choose from.
    available_cryptos = ["ETH", "POLYGON"]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a highly advanced financial agent. Your goal is to optimize cross-border payments by choosing the most cost-effective cryptocurrency from an available list. "
                f"The available intermediate cryptocurrencies are: {', '.join(available_cryptos)}.\n"
                "When a user wants to pay a target amount in a foreign currency (e.g., pay $1200 USD from INR), you must follow a three-stage plan:\n"
                "1. **Comparison Stage:** First, you must determine the best path. To do this, simulate the conversion of a test amount (e.g., 10,000 INR) through EACH available cryptocurrency (ETH and POLYGON) to see which one yields more USD. You must use your `convert_and_transfer` tool multiple times for this simulation and state which path is better.\n"
                "2. **Calculation Stage:** Once you have identified the optimal path, perform the main calculation. Work backward from the user's target amount (e.g., $1200 USD) along the *chosen path* to determine the exact starting INR amount needed.\n"
                "3. **Summary Stage:** Finally, present a clear, step-by-step summary of the forward transaction using the optimal path and the calculated amounts as your final answer to the user. Do not try to execute the forward steps; just describe them."
            )
        },
        {
            "role": "user",
            "content": "I am in India and I need to pay a merchant in the US $1200. My account is '0xIndianAccount' and the merchant's is '0xUSMerchant'. Please handle the transaction."
        }
    ]

    print(f"User: {messages[-1]['content']}\n")

    # Agentic loop continues until the model provides a final text response
    while True:
        try:
            print("--- Sending request to model... ---")
            payload = { "model": MODEL, "messages": messages, "tools": [convert_and_transfer_schema], "tool_choice": "auto" }
            
            response = requests.post(ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            response_message = response.json()["choices"][0]["message"]
            messages.append(response_message)

            if not response_message.get("tool_calls"):
                print("\n--- Agent provided final response ---")
                print(f"Assistant: {response_message['content']}")
                break 

            print("--- Model requested tool calls ---")
            tool_calls = response_message["tool_calls"]
            tool_outputs = []

            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                if function_name == "convert_and_transfer":
                    args = json.loads(tool_call["function"]["arguments"])
                    function_response = convert_and_transfer(**args)
                    print(f"<--- Tool output: {function_response}")
                    tool_outputs.append({
                        "tool_call_id": tool_call["id"], "role": "tool", "name": function_name, "content": function_response
                    })
            
            messages.extend(tool_outputs)

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

if __name__ == "__main__":
    run_conversation()
