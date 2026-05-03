from langgraph.graph import END, START, StateGraph

from repo_fix_agent.graph.routes import route_after_review
from repo_fix_agent.graph.state import AgentState
from repo_fix_agent.nodes.analyze_request import analyze_request_node
from repo_fix_agent.nodes.inspect_repo import inspect_repo_node
from repo_fix_agent.nodes.plan_fix import plan_fix_node
from repo_fix_agent.nodes.edit_files import edit_files_node
from repo_fix_agent.nodes.run_tests import run_tests_node
from repo_fix_agent.nodes.review_result import review_result_node
from repo_fix_agent.nodes.rollback import rollback_node
from repo_fix_agent.nodes.final_summary import final_summary_node


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("analyze_request", analyze_request_node)
    graph.add_node("inspect_repo", inspect_repo_node)
    graph.add_node("plan_fix", plan_fix_node)
    graph.add_node("edit_files", edit_files_node)
    graph.add_node("run_tests", run_tests_node)
    graph.add_node("review_result", review_result_node)
    graph.add_node("rollback", rollback_node)
    graph.add_node("final_summary", final_summary_node)

    graph.add_edge(START, "analyze_request")
    graph.add_edge("analyze_request", "inspect_repo")
    graph.add_edge("inspect_repo", "plan_fix")
    graph.add_edge("plan_fix", "edit_files")
    graph.add_edge("edit_files", "run_tests")
    graph.add_edge("run_tests", "review_result")
    graph.add_conditional_edges(
        "review_result",
        route_after_review,
        {
            "inspect_repo": "inspect_repo",
            "rollback": "rollback",
            "final_summary": "final_summary",
        },
    )
    graph.add_edge("rollback", "final_summary")
    graph.add_edge("final_summary", END)

    return graph
