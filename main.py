# 显示代理
from IPython.display import Image, display
from lc.graph_api import agent
from langchain.messages import HumanMessage

if __name__ == "__main__":
    try:
        display(Image(agent.get_graph(xray=True).draw_mermaid_png()))
    except Exception as e:
        print(f"无法显示图表: {e}")

    # 调用
    messages = [HumanMessage(content="3123421加43242在减45422之后乘以2等于多少。")]
    messages = agent.invoke({"messages": messages})
    for m in messages["messages"]:
        m.pretty_print()