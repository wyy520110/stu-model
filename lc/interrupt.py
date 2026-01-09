# hitl_streaming_example.py
# 说明：按实际环境替换 model 的调用（Qwen 的 LangChain adapter）
# 依赖（示例）： pip install langchain langgraph
import uuid
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from langchain.messages import HumanMessage
import dotenv
import os
from langchain_community.llms.tongyi import Tongyi
dotenv.load_dotenv()
# 下面示例用一个 placeholder model.invoke; 在真实环境请用你的 Qwen model adapter
# e.g., from langchain.chat_models import init_chat_model; model = init_chat_model("qwen:xxx")

def call_model_simulator(prompt: str) -> str:
    """示意：把这行替换为真实模型调用（同步或异步按需）"""
    model = Tongyi(
      api_key=os.getenv("Qwen_API_Key"),
      model="qwen-flash",
    )
    print('第一步prompt', prompt)
    res = model.invoke(prompt)
    return f"（模型部分回复）基于提示：{res}"

# 1) 定义状态结构（简单 dict 用法）
# node_a: 生成初步回复并在中间点 interrupt 请求人类补充信息
# node_b: 使用人类补充信息完成最终回复
def node_a(state):
    # 生成初步内容（示例）
    user_text = state.get("user_text", "")
    partial = call_model_simulator(f"初步回答: {user_text}")
    # 请求人工补充（interrupt 会暂停，并把 payload 返回给调用者）
    # 这里传出一个简单的 prompt，告诉人类需要补充哪个字段
    human_value = interrupt({"ask": "请提供补充说明（最多 1 段话）以便继续生成：", "context": partial})
    # 当 resume 时，interrupt(...) 表达式返回 human 提交的文本
    return {"partial": partial, "human_extra": human_value}

def node_b(state):
    # 使用 human_extra 完成最终回复
    partial = state.get("partial", "")
    extra = state.get("human_extra", "")
    final = call_model_simulator(f"{partial}\n\n基于用户补充：{extra}\n生成完整回答：")
    return {"final": final}

# 2) 构建并编译图，必须带 checkpointer 以便中断时持久化状态
graph = StateGraph(dict)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")
graph.add_edge("node_b", END)

checkpointer = InMemorySaver()  # 开发用；生产用 PostgresSaver/AsyncPostgresSaver
compiled = graph.compile(checkpointer=checkpointer)

# 3) 运行并流式读取（在控制台做示例交互）
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

print("Invoke graph,等待中断并流式输出中间进度...")
# 用 stream(mode='values') 获取增量更新（每次 super-step 的状态快照）
for chunk in compiled.stream({"user_text": "请解释llm"}, config, stream_mode="values"):
    # chunk 是一个状态快照（dict），可能含有 __interrupt__（当中断发生）
    # 打印当前已写入的 messages/values 以便观察
    print("<< 更新片段 >>", chunk)
    # 检查是否出现中断（在 stream 中会以 '__interrupt__' 出现）
    if chunk.get("__interrupt__"):
        intr = chunk["__interrupt__"][0].value
        # 显示给人工审阅（此处用 input 模拟人工在 UI 填充）
        print("\n=== 需要人工输入 ===")
        print(intr)  # 包含 ask/context 等
        human_text = input("请在终端输入补充文本，然后回车提交（模拟人工）： ")
        print("已提交，恢复执行并以流式返回剩余结果...\n")
        # 4) 用 Command(resume=...) 恢复并继续流式获取后续输出
        # 注意：必须使用相同的 config（相同 thread_id）
        for resume_chunk in compiled.stream(Command(resume=human_text), config, stream_mode="values"):
            print("<< 恢复后更新 >>", resume_chunk)
        break  # 完成一次中断-恢复流程后结束示例