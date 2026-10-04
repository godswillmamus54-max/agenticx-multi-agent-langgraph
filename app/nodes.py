from typing import Literal, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.config import MODEL_NAME, OPENAI_API_KEY
from app.prompts import (
    PLANNER_PROMPT,
    REVIEWER_PROMPT,
    WORKER_PROMPT,
)
from app.state import WorkflowState


class ReviewResult(BaseModel):
    """Structured decision returned by the Reviewer."""

    status: Literal["approved", "rejected"] = Field(
        description="Whether the draft is approved or rejected."
    )
    feedback: str = Field(
        description="Actionable feedback for the Worker."
    )


def create_model() -> ChatOpenAI:
    """Create the production chat model used by the agents."""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not configured. "
            "Add it to the .env file before running the live workflow."
        )

    return ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY,
        temperature=0,
    )


def _invoke_text_model(
    model: BaseChatModel,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """Invoke a chat model and normalize its text response."""
    response = model.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )

    content = response.content

    if isinstance(content, str):
        text = content.strip()
    else:
        text = str(content).strip()

    if not text:
        raise ValueError("The model returned an empty response.")

    return text


def planner_node(
    state: WorkflowState,
    model: Optional[BaseChatModel] = None,
) -> dict:
    """
    Convert the user's task into an ordered execution plan.
    """
    model = model or create_model()

    task = state["task"].strip()

    if not task:
        raise ValueError("Planner received an empty task.")

    user_prompt = f"""
USER TASK:
{task}

Create the ordered execution plan for the Worker.
Return only the plan, with one actionable step per line.
"""

    plan_text = _invoke_text_model(
        model=model,
        system_prompt=PLANNER_PROMPT,
        user_prompt=user_prompt,
    )

    plan = [
        line.strip()
        for line in plan_text.splitlines()
        if line.strip()
    ]

    if not plan:
        raise ValueError("Planner produced an empty plan.")

    return {
        "plan": plan,
    }


def worker_node(
    state: WorkflowState,
    model: Optional[BaseChatModel] = None,
) -> dict:
    """
    Execute the plan and produce or revise the report draft.
    """
    model = model or create_model()

    task = state["task"].strip()
    plan = state.get("plan", [])
    previous_draft = state.get("draft", "").strip()
    review_feedback = state.get("review_feedback", "").strip()

    if not task:
        raise ValueError("Worker received an empty task.")

    if not plan:
        raise ValueError("Worker cannot operate without a plan.")

    plan_text = "\n".join(
        f"{index}. {step}"
        for index, step in enumerate(plan, start=1)
    )

    revision_context = (
        f"""
CURRENT DRAFT:
{previous_draft}

REVIEWER FEEDBACK:
{review_feedback}

Revise the current draft so that the reviewer's feedback is addressed.
"""
        if previous_draft and review_feedback
        else """
There is no previous draft to revise. Produce the initial draft.
"""
    )

    user_prompt = f"""
USER TASK:
{task}

PLANNER'S EXECUTION PLAN:
{plan_text}

{revision_context}

Produce the complete requested report.
Return only the report itself.
"""

    draft = _invoke_text_model(
        model=model,
        system_prompt=WORKER_PROMPT,
        user_prompt=user_prompt,
    )

    return {
        "draft": draft,
        "iteration": state.get("iteration", 0) + 1,
    }


def reviewer_node(
    state: WorkflowState,
    model: Optional[BaseChatModel] = None,
) -> dict:
    """
    Evaluate the Worker's draft and update review state.
    """
    model = model or create_model()

    task = state["task"].strip()
    plan = state.get("plan", [])
    draft = state.get("draft", "").strip()

    if not task:
        raise ValueError("Reviewer received an empty task.")

    if not plan:
        raise ValueError("Reviewer cannot operate without a plan.")

    if not draft:
        raise ValueError("Reviewer cannot evaluate an empty draft.")

    plan_text = "\n".join(
        f"{index}. {step}"
        for index, step in enumerate(plan, start=1)
    )

    user_prompt = f"""
USER TASK:
{task}

PLANNER'S EXECUTION PLAN:
{plan_text}

WORKER'S DRAFT:
{draft}

Evaluate the draft against the task and plan.

Return:
- status: approved or rejected
- feedback: concise actionable feedback
"""

    structured_model = model.with_structured_output(ReviewResult)

    review = structured_model.invoke(
        [
            SystemMessage(content=REVIEWER_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    if review.status == "rejected":
        rejection_count = state.get("rejection_count", 0) + 1
    else:
        rejection_count = 0

    history = list(state.get("review_history", []))

    history.append(
        {
            "iteration": state.get("iteration", 0),
            "status": review.status,
            "feedback": review.feedback,
        }
    )

    return {
        "review_status": review.status,
        "review_feedback": review.feedback,
        "rejection_count": rejection_count,
        "review_history": history,
    }