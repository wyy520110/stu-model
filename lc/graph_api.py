from langchain.messages import AnyMessage, SystemMessage, ToolMessage
from typing_extensions import Annotated, TypedDict
import operator
from langgraph.graph import StateGraph, START, END, add_messages
from typing import Literal
import utils.graph_tools as tools


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int
    
    
# 模型节点
def llm_node(state: MessagesState):
    """LLM决定是否调用工具"""
    return {
        "messages": [
          tools.model_bind_tools.invoke([
            SystemMessage(content="你是一个有用的助手，负责对一组输入执行算术运算。"),
            *state["messages"]
          ])
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }

# 工具节点
def tool_node(state: MessagesState):
    """调用工具"""
    result = []
    tool_calls = state["messages"][-1].tool_calls
    for tool_call in tool_calls:
        tool = tools.tools_name[tool_call['name']]
        output = tool.invoke(tool_call['args'])
        result.append(ToolMessage(
          tool_call_id=tool_call['id'],
          content=output
        ))
    return {
        "messages": result,
    }
    
def should_continue(state: dict) -> Literal["tool_node", END]:
    """决定是否继续循环或停止，基于LLM是否进行了工具调用"""

    messages = state["messages"]
    last_message = messages[-1]

    # 如果LLM进行了工具调用，则执行操作
    if last_message.tool_calls:
        return "tool_node"

    # 否则，我们停止（回复用户）
    return END


agent_builder = StateGraph(MessagesState)

agent_builder.add_node(llm_node)
agent_builder.add_node(tool_node)

agent_builder.add_edge(START, 'llm_node')
agent_builder.add_conditional_edges(
    'llm_node',
    should_continue,
    {
        "tool_node": "tool_node",
        END: END,
    }
)
agent_builder.add_edge('tool_node', 'llm_node')

agent = agent_builder.compile()


from typing import TypedDict, Literal
from langgraph.types import Command
Command()
# 定义电子邮件分类的结构
class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str

class EmailAgentState(TypedDict):
    # 原始邮件数据
    email_content: str
    sender_email: str
    email_id: str

    # 分类结果
    classification: EmailClassification | None

    # 原始搜索/API结果
    search_results: list[str] | None  # 原始文档块列表
    customer_history: dict | None  # 来自CRM的原始客户数据

    # 生成的内容
    draft_response: str | None
    messages: list[str] | None