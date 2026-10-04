# Multi-Agent Research Workflow Architecture

## Workflow

```text
                    ┌───────────────┐
                    │     START     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    PLANNER    │
                    │               │
                    │ Creates an    │
                    │ ordered plan  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │     WORKER    │
                    │               │
                    │ Executes plan │
                    │ / revises     │
                    │ draft         │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   REVIEWER    │
                    │               │
                    │ Evaluates     │
                    │ draft         │
                    └───────┬───────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
              APPROVED             REJECTED
                  │                   │
                  ▼                   ▼
           ┌─────────────┐      rejection_count
           │   FINISH    │           < 2
           └──────┬──────┘              │
                  │                     ▼
                  │              ┌───────────────┐
                  │              │     WORKER    │
                  │              │    REVISES    │
                  │              └───────┬───────┘
                  │                      │
                  │                      ▼
                  │                ┌───────────────┐
                  │                │    REVIEWER    │
                  │                └───────┬───────┘
                  │                        │
                  │                  rejection_count
                  │                       >= 2
                  │                        │
                  │                        ▼
                  │                 ┌───────────────┐
                  │                 │    ESCALATE   │
                  │                 └───────┬───────┘
                  │                        │
                  ▼                        ▼
             ┌─────────────────────────────────┐
             │               END               │
             └─────────────────────────────────┘
 
          Agent Responsibilities
Planner
Converts the original task into an ordered execution plan.
Worker
Executes the plan and produces the requested draft. When rejected, it uses Reviewer feedback to revise the draft.
Reviewer
Evaluates the draft against the original task and Planner's execution plan.
The Reviewer returns a structured decision:
- approved
- rejected
Router
The Reviewer result determines the next graph transition.
APPROVED
    ↓
FINISH
    ↓
END

REJECTED + rejection_count < 2
    ↓
WORKER
    ↓
REVIEWER

REJECTED + rejection_count >= 2
    ↓
ESCALATE
    ↓
END

Two-Rejection Safeguard
The workflow intentionally limits consecutive Reviewer rejections to two.
Example:
Worker
  ↓
Reviewer → REJECTED #1
  ↓
Worker revision
  ↓
Reviewer → REJECTED #2
  ↓
Escalate
  ↓
END

This prevents an unrestricted Worker ↔ Reviewer loop.
Shared State
All agents operate through the shared WorkflowState.
class WorkflowState(TypedDict):
    task: str
    plan: list[str]
    draft: str
    review_status: str
    review_feedback: str
    rejection_count: int
    iteration: int
    review_history: list[dict]
    final_output: str


Test Coverage
The compiled graph has been tested against:
1. Approval
2. Rejection followed by approval
3. Two consecutive rejections
4. Infinite-loop prevention
Current result:
8 passed
