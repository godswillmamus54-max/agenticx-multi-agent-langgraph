from typing import TypedDict


class WorkflowState(TypedDict):
    """
    Shared state passed between the Planner, Worker, Reviewer,
    and workflow routing logic.
    """

    # Original user request.
    task: str

    # Structured plan produced by the Planner.
    plan: list[str]

    # Current report/draft produced by the Worker.
    draft: str

    # Current Reviewer decision: "", "approved", or "rejected".
    review_status: str

    # Actionable feedback from the Reviewer.
    review_feedback: str

    # Number of consecutive reviewer rejections.
    rejection_count: int

    # Number of Worker/Reviewer execution cycles.
    iteration: int

    # Complete audit trail of reviewer decisions.
    review_history: list[dict]

    # Final approved output or terminal escalation message.
    final_output: str