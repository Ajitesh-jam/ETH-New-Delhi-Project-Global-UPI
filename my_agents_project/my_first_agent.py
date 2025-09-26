# # from uagents import Agent, Context

# # # instantiate agent
# # agent = Agent(
# #     name="alice",
# #     seed="secret_seed_phrase",
# #     port=8000,
# #     endpoint=["http://localhost:8000/submit"]
# # )

# # # startup handler
# # @agent.on_event("startup")
# # async def startup_function(ctx: Context):
# #     ctx.logger.info(f"Hello, I'm agent {agent.name} and my address is {agent.address}.")

# # if __name__ == "__main__":
# #     agent.run()


# from concurrent.futures import process
# from pickle import load
# from uagents_adapter import LangchainRegisterTool
# import dotenv
# load.dotenv()

# # Import or define your LangGraph app instance before using it
# from langgraph import LangGraphApp  # Replace with actual import if different

# # Initialize your LangGraph app (replace with actual initialization as needed)
# langgraph_app = LangGraphApp()

# # Wrap LangGraph agent function for uAgent integration
# def langgraph_agent_func(query):
#     # Process with LangGraph
#     result = langgraph_app.invoke(query)
#     return result

# # Register the LangGraph function as a uAgent
# tool = LangchainRegisterTool()
# agent_info = tool.invoke({
#     "agent_obj": langgraph_agent_func,
#     "name": "my_langgraph_agent",
#     "port": 8080,
#     "description": "A LangGraph orchestration agent",
#     "api_token": process.env.AGENTVERSE_API_KEY

# })


from multiprocessing import process
from uagents_adapter import LangchainRegisterTool

# Wrap LangGraph agent function for uAgent integration
def langgraph_agent_func(query):
    # Process with LangGraph
    result = langgraph_app.invoke(query)
    return result

# Register the LangGraph function as a uAgent
tool = LangchainRegisterTool()
agent_info = tool.invoke({
    "agent_obj": langgraph_agent_func,
    "name": "my_langgraph_agent",
    "port": 8080,
    "description": "A LangGraph orchestration agent",
    "api_token": process.env.AGENTVERSE_API_KEY
})