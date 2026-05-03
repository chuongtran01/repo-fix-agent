from langgraph.graph import END, START, StateGraph

from repo_fix_agent.graph.state import AgentState
from repo_fix_agent.nodes.analyze_request import analyze_request_node
from repo_fix_agent.nodes.inspect_repo import inspect_repo_node
from repo_fix_agent.nodes.plan_fix import plan_fix_node
from repo_fix_agent.nodes.edit_files import edit_files_node


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("analyze_request", analyze_request_node)
    graph.add_node("inspect_repo", inspect_repo_node)
    graph.add_node("plan_fix", plan_fix_node)
    graph.add_node("edit_files", edit_files_node)

    graph.add_edge(START, "analyze_request")
    graph.add_edge("analyze_request", "inspect_repo")
    graph.add_edge("inspect_repo", "plan_fix")
    graph.add_edge("plan_fix", "edit_files")
    graph.add_edge("edit_files", END)

    return graph
