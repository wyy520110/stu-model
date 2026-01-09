from langchain.tools import tool
from langchain_community.chat_models.tongyi import ChatTongyi
import dotenv
import os

dotenv.load_dotenv()

@tool
def add(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b
  
@tool
def sub(a: int, b: int) -> int:
    """Subtracts two numbers together."""
    return a - b
  
@tool
def mul(a: int, b: int) -> int:
    """Multiplies two numbers together."""
    return a * b
  
@tool
def div(a: int, b: int) -> int:
    """Divides two numbers together."""
    return a / b
  
tools = [add, sub, mul, div]
tools_name = {tool.name: tool for tool in tools}
model = ChatTongyi(
    model="qwen-flash",
    api_key=os.getenv("Qwen_API_Key"),
    temperature=0.5,
)
model_bind_tools = model.bind_tools(tools)