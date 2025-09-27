#!/usr/bin/env python3
"""
Interactive Token Metrics AI Client - Ask questions naturally via command line

Instructions:
1. Ensure TOKENMETRICS_API_KEY is set in your .env file
2. Run: python interactive_client.py  
3. Type your crypto questions and get instant responses!

Note: OpenAI API key is now handled server-side for security and cost control.
"""
import os
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import asyncio
import threading
import sys
import json
from datetime import datetime
from pathlib import Path
import dotenv           
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# LOCAL DATA STORAGE SETUP
# ============================================================================
# Create data directory for storing conversation logs
DATA_DIR = Path(__file__).parent / "data_logs"
DATA_DIR.mkdir(exist_ok=True)

# File paths for different types of data
QUESTIONS_FILE = DATA_DIR / "questions_log.jsonl"
RESPONSES_FILE = DATA_DIR / "responses_log.jsonl"
CONVERSATION_FILE = DATA_DIR / "conversation_history.jsonl"
DAILY_SUMMARY_FILE = DATA_DIR / f"daily_summary_{datetime.now().strftime('%Y%m%d')}.json"

def save_to_jsonl(file_path: Path, data: dict):
    """Save data to JSONL file (one JSON object per line)"""
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

def save_question(question: str, timestamp: datetime = None):
    """Save user question to local storage"""
    if timestamp is None:
        timestamp = datetime.now()
    
    question_data = {
        "timestamp": timestamp.isoformat(),
        "type": "question",
        "content": question,
        "user": "human"
    }
    
    save_to_jsonl(QUESTIONS_FILE, question_data)
    save_to_jsonl(CONVERSATION_FILE, question_data)
    print(f"📝 Question saved to: {QUESTIONS_FILE}")

def save_response(response: str, success: bool, error: str = None, timestamp: datetime = None):
    """Save AI response to local storage"""
    if timestamp is None:
        timestamp = datetime.now()
    
    response_data = {
        "timestamp": timestamp.isoformat(),
        "type": "response",
        "content": response,
        "success": success,
        "error": error,
        "source": "token_metrics_ai"
    }
    
    save_to_jsonl(RESPONSES_FILE, response_data)
    save_to_jsonl(CONVERSATION_FILE, response_data)
    print(f"💾 Response saved to: {RESPONSES_FILE}")

def save_daily_summary():
    """Save a daily summary of conversation stats"""
    try:
        if not CONVERSATION_FILE.exists():
            return
            
        # Read all conversation data for today
        today = datetime.now().strftime('%Y-%m-%d')
        conversations = []
        
        with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if data['timestamp'].startswith(today):
                        conversations.append(data)
                except json.JSONDecodeError:
                    continue
        
        # Calculate stats
        questions = [c for c in conversations if c['type'] == 'question']
        responses = [c for c in conversations if c['type'] == 'response']
        successful_responses = [r for r in responses if r['success']]
        
        summary = {
            "date": today,
            "total_questions": len(questions),
            "total_responses": len(responses),
            "successful_responses": len(successful_responses),
            "success_rate": len(successful_responses) / len(responses) if responses else 0,
            "topics_discussed": [q['content'][:50] + "..." if len(q['content']) > 50 else q['content'] for q in questions[-5:]],  # Last 5 questions
            "last_updated": datetime.now().isoformat()
        }
        
        with open(DAILY_SUMMARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        print(f"📊 Daily summary saved to: {DAILY_SUMMARY_FILE}")
        
    except Exception as e:
        print(f"⚠️ Error saving daily summary: {e}")

# ============================================================================
# CONFIGURATION - Only need Token Metrics API key now
# ============================================================================
TOKENMETRICS_API_KEY = os.getenv('TOKENMETRICS_API_KEY')
print( "Keyy:")
print( TOKENMETRICS_API_KEY)
TOKENMETRICS_AGENT_ADDRESS = "agent1qwrcq6kwddq6sda3c64qw7wkcz6q6de9e9k5zm2fs6pgpefsyjuej5sayrq"

# ============================================================================  
# Message Models
# ============================================================================
class CryptoQuestion(Model):
    message: str
    tokenmetrics_api_key: str

class CryptoAnswer(Model):
    response: str
    success: bool
    error: str = None

# ============================================================================
# Interactive Agent
# ============================================================================
agent = Agent(
    name="name_your_own_agent",
    seed="your-agent-seed-could-be-anything",
    port=8003,
    mailbox=True
)

# Global state for handling responses
response_received = asyncio.Event()
latest_response = None
agent_loop = None  # Store agent's event loop

@agent.on_message(model=CryptoAnswer)
async def handle_crypto_response(ctx: Context, sender: str, msg: CryptoAnswer):
    """Handle responses from Token Metrics AI"""
    global latest_response, response_received
    
    # Clear any animation line before printing response
    print("\r" + " " * 20 + "\r", end="", flush=True)
    
    if msg.success:
        latest_response = msg.response
        print(f"🤖 Token Metrics AI: {msg.response}\n", flush=True)
        
        # Save successful response to local storage
        save_response(msg.response, True)
    else:
        latest_response = f"Error: {msg.error}"
        print(f"❌ Error: {msg.error}\n", flush=True)
        
        # Save error response to local storage
        save_response(msg.error or "Unknown error", False, msg.error)
    
    # Signal that response was received
    response_received.set()

async def send_question(question: str):
    """Send a question and wait for response"""
    global response_received, latest_response
    
    # Reset response state
    response_received.clear()
    latest_response = None
    
    # Create and send message
    message = CryptoQuestion(
        message=question,
        tokenmetrics_api_key=TOKENMETRICS_API_KEY
    )
    
    # Send through agent context
    if hasattr(agent, '_ctx') and agent._ctx:
        result = await agent._ctx.send(TOKENMETRICS_AGENT_ADDRESS, message)
    else:
        return "❌ Agent not ready. Please wait."
    
    # Wait for response (with timeout)
    try:
        await asyncio.wait_for(response_received.wait(), timeout=60.0)
        return latest_response
    except asyncio.TimeoutError:
        return "⏰ Request timed out. Please try again."

def interactive_chat():
    """Interactive chat loop"""
    print("🚀 Token Metrics AI Interactive Client")
    print("=" * 50)
    print("Ask me anything about cryptocurrency!")
    print("Type 'quit' or 'exit' to stop")
    print("=" * 50)
    
    while True:
        try:
            # Get user input
            question = input("\n💬 You: ").strip()
            
            # Check for exit
            if question.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Goodbye! Thanks for using Token Metrics AI!")
                break
            
            if not question:
                continue
                
            # Send question and get response with elegant animation
            import threading
            import time
            import sys
            
            # Animation control
            animation_running = True
            
            def elegant_animation():
                """Clean thinking animation"""
                frames = [
                    "○ Analyzing...",
                    "◉ Analyzing...", 
                    "○ Analyzing..."
                ]
                
                idx = 0
                while animation_running:
                    print(f"\r{frames[idx % len(frames)]}", end="", flush=True)
                    time.sleep(0.5)
                    idx += 1
            
            # Start animation in background thread
            animation_thread = threading.Thread(target=elegant_animation, daemon=True)
            animation_thread.start()
            
            try:
                # Use thread-safe communication with agent's event loop
                if agent_loop and agent_loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(send_question(question), agent_loop)
                    response = future.result(timeout=60)
                else:
                    response = "⚠️ Agent not ready, please wait..."
            finally:
                # Stop animation and clear line
                animation_running = False
                animation_thread.join(timeout=0.2)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using Token Metrics AI!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def run_agent():
    """Run the agent in background"""
    agent.run()

@agent.on_event("startup")
async def startup(ctx: Context):
    """Agent startup"""
    global agent_loop
    print(f"🔗 Connected to Token Metrics AI at {TOKENMETRICS_AGENT_ADDRESS}")
    
    # Store context and event loop globally for sending messages
    agent._ctx = ctx
    agent_loop = asyncio.get_event_loop()

if __name__ == "__main__":
    # Validate API key
    if not TOKENMETRICS_API_KEY or TOKENMETRICS_API_KEY.startswith("YOUR_"):
        print("❌ Please update your Token Metrics API key in the .env file!")
        sys.exit(1)
    
    # Fund agent wallet
    fund_agent_if_low(agent.wallet.address())
    
    # Start agent in background thread
    agent_thread = threading.Thread(target=run_agent, daemon=True)
    agent_thread.start()
    
    # Wait a moment for agent to start
    import time
    time.sleep(3)
    
    # Start interactive chat
    try:
        interactive_chat()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
