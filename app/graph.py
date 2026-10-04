from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.nodes import (
    planner_node,
    reviewer_node,
    worker_node,
)
from app.state import WorkflowState


def route_after_review(
    state: WorkflowState,
) -> Literal["finish", "revise", "escalate"]:
    """
    Decide what the workflow should do after the Reviewer.

    APPROVED:
        Finish the workflow.

    REJECTED with fewer than two consecutive rejections:
        Send the draft back to the Worker for revision.

    REJECTED with two or more consecutive rejections:
        Escalate and terminate the workflow.
    """
    review_status = state.get("review_status", "")
    rejection_count = state.get("rejection_count", 0)

    if review_status == "approved":
        return "finish"

    if review_status == "rejected":
        if rejection_count < 2:
            return "revise"

        return "escalate"

    # Unknown review status is treated as a terminal condition
    # rather than allowing the graph to loop indefinitely.
    return "escalate"


def escalate_node(state: WorkflowState) -> dict:
    """
    Produce a terminal result after two consecutive reviewer rejections.
    """
    history = state.get("review_history", [])

    return {
        "final_output": (
            "REVIEW FAILED\n\n"
            "The workflow reached two consecutive reviewer rejections "
            "without producing an approved draft.\n\n"
            f"Review decisions recorded: {len(history)}"
        ),
    }


def finish_node(state: WorkflowState) -> dict:
    """
    Store the approved draft as the final workflow output.
    """
    return {
        "final_output": state.get("draft", ""),
    }


def build_workflow_graph(
    planner=planner_node,
    worker=worker_node,
    reviewer=reviewer_node,
):
    """
    Build and compile the Planner → Worker → Reviewer workflow.

    Agent nodes can be injected for deterministic integration testing
    while production execution uses the real LLM-backed nodes by default.
    """
    graph = StateGraph(WorkflowState)

    # Agent nodes.
    graph.add_node("planner", planner)
    graph.add_node("worker", worker)
    graph.add_node("reviewer", reviewer)

    # Terminal/control nodes.
    graph.add_node("finish", finish_node)
    graph.add_node("escalate", escalate_node)

    # Initial workflow.
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "worker")
    graph.add_edge("worker", "reviewer")

    # Conditional Reviewer routing.
    graph.add_conditional_edges(
        "reviewer",
        route_after_review,
        {
            "finish": "finish",
            "revise": "worker",
            "escalate": "escalate",
        },
    )

    # Terminal nodes.
    graph.add_edge("finish", END)
    graph.add_edge("escalate", END)

    return graph.compile()