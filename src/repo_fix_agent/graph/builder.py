from langgraph.graph import END, START, StateGraph

from repo_fix_agent.graph.state import AgentState
from repo_fix_agent.nodes.analyze_request import analyze_request_node


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("analyze_request", analyze_request_node)
    graph.add_edge(START, "analyze_request")
    graph.add_edge("analyze_request", END)

    return graph
