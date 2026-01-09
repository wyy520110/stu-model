# -*- coding: utf-8 -*-
from langgraph.graph import START, StateGraph
from typing import TypedDict

from langgraph.runtime import Runtime

# Define subgraph
class SubgraphState(TypedDict):
    foo: str  # Note that this key is shared with parent graph
    bar: str

def subgraph_node_1(state: SubgraphState, runtime: Runtime):
    runtime.stream_writer('子图node1')
    return {"bar": "bar"}

def subgraph_node_2(state: SubgraphState, runtime: Runtime):
    runtime.stream_writer('子图node2')
    return {"foo": state["foo"] + state["bar"]}

subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_node(subgraph_node_2)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
subgraph = subgraph_builder.compile()

# Define parent graph
class ParentState(TypedDict):
    foo: str

def node_1(state: ParentState):
    return {"foo": "hi! " + state["foo"]}

builder = StateGraph(ParentState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", subgraph)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
graph = builder.compile()

for chunk in graph.stream(
    {"foo": "foo"},
    stream_mode='debug',
    # Set subgraphs=True to stream subgraph outputs
    subgraphs=True,
):
    print('++++',chunk,"++++++")