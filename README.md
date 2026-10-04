# Multi-Agent Research Workflow with LangGraph

A stateful multi-agent workflow that coordinates a Planner, Worker, and Reviewer using LangGraph.

The workflow demonstrates explicit shared state, conditional routing, reviewer-driven revision, bounded retries, structured review decisions, and terminal escalation after two consecutive reviewer rejections.

This project was developed as the **Multi-Agent Workflow with LangGraph** project for the **AgenticX AI Labs AI Agents & Automation internship**.

---

## Overview

This project implements a multi-agent workflow where specialized agents collaborate through a shared LangGraph state.

The workflow follows:

```text
START
  |
  v
PLANNER
  |
  v
WORKER
  |
  v
REVIEWER
  |
  +--------------------+
  |                    |
  | APPROVED            | REJECTED
  v                    v
FINISH          rejection_count < 2
  |                    |
  v                    v
 END                  WORKER
                       |
                       v
                    REVIEWER
                       |
                       +--------------------+
                       |                    |
                       | APPROVED           | REJECTED
                       v                    v
                    FINISH            rejection_count >= 2
                                            |
                                            v
                                         ESCALATE
                                            |
                                            v
                                           END
The workflow is intentionally bounded so that repeated reviewer rejection cannot create an infinite agent loop.

Project Goals
The project demonstrates:
- Multi-agent coordination with LangGraph
- A Planner → Worker → Reviewer architecture
- Explicit shared workflow state
- Conditional graph routing
- Reviewer-driven revision
- Structured reviewer decisions
- Bounded rejection handling
- Terminal escalation
- Deterministic integration testing
- LLM-backed production nodes
- Reproducible workflow demonstrations
Architecture
Planner
The Planner receives the original user task and converts it into an ordered execution plan.
Responsibilities:
- Understand the requested outcome
- Break the task into actionable steps
- Produce a plan for the Worker
- Avoid writing the final answer
The Planner does not execute the task itself.
Worker
The Worker executes the Planner's plan and produces the requested draft.
Responsibilities:
- Follow the Planner's execution plan
- Address the original task
- Produce the actual requested output
- Revise the draft when Reviewer feedback is provided
- Preserve useful parts of an existing draft when appropriate
When the Reviewer rejects a draft, the Worker receives the feedback and produces a revised version.
Reviewer
The Reviewer evaluates the Worker's draft against:
1. The original user task
2. The Planner's execution plan
The Reviewer checks:
- Completeness
- Relevance
- Alignment with the plan
- Logical quality
- Missing requirements
The Reviewer returns a structured decision:
approved

or:
rejected

When rejecting a draft, the Reviewer provides actionable feedback for the Worker.
The Reviewer does not rewrite the draft.
Shared State
The workflow uses an explicit WorkflowState schema.
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


State Fields
Field	Purpose
task	Original user request
plan	Ordered execution plan produced by Planner
draft	Worker's current output
review_status	Current Reviewer decision
review_feedback	Feedback supplied to the Worker
rejection_count	Number of consecutive rejections
iteration	Worker execution iteration
review_history	Record of previous review decisions
final_output	Terminal workflow result


The state is shared between nodes and controls the workflow's routing behavior.
Conditional Routing
After every Reviewer execution, the workflow evaluates the review state.
Approved
If:
review_status == "approved"


the workflow routes to:
FINISH → END

The approved Worker draft becomes the final output.
First Rejection
If:
review_status == "rejected"
rejection_count == 1


the workflow routes back to:
WORKER → REVIEWER

The Worker receives the Reviewer feedback and revises the draft.
Second Consecutive Rejection
If:
review_status == "rejected"
rejection_count >= 2


the workflow routes to:
ESCALATE → END

The workflow terminates rather than continuing indefinitely.
Two-Rejection Safeguard
A key reliability feature is the bounded review loop.
The intended behavior is:
Worker
  |
  v
Reviewer → REJECT
  |
  v
Worker revises
  |
  v
Reviewer → REJECT
  |
  v
ESCALATE
  |
  v
END

This provides a deterministic upper bound on Reviewer-driven revisions.
The workflow preserves the review history so the final state records the decisions that caused escalation.
Error and Safety Behavior
The workflow is designed to fail closed rather than loop indefinitely.
For example, an unexpected review status is treated as a terminal escalation condition.
The routing logic supports three explicit outcomes:
finish
revise
escalate

No other routing destination is accepted.
The Reviewer also uses structured output so that the workflow receives an explicit approval/rejection decision rather than relying on free-form text parsing.
Testing
The project contains deterministic tests that exercise both routing logic and the compiled LangGraph.
Run the complete test suite with:
python -m pytest -q

Current Test Result
8 passed

Tested Scenarios
1. Approval Path
Planner
  ↓
Worker
  ↓
Reviewer → APPROVED
  ↓
Finish
  ↓
END

2. Rejection Followed by Approval
Planner
  ↓
Worker
  ↓
Reviewer → REJECTED
  ↓
Worker revision
  ↓
Reviewer → APPROVED
  ↓
Finish
  ↓
END

3. Two Consecutive Rejections
Planner
  ↓
Worker
  ↓
Reviewer → REJECTED
  ↓
Worker revision
  ↓
Reviewer → REJECTED
  ↓
Escalate
  ↓
END

4. Infinite-Loop Prevention
The integration tests verify that after two consecutive rejections:
- Planner runs once
- Worker runs twice
- Reviewer runs twice
- The workflow terminates
- Escalation is produced
Runnable Demonstrations
The repository includes two runnable demonstrations.
Live LLM Workflow
examples/live_run.py executes the production LLM-backed workflow.
It demonstrates:
Planner → Worker → Reviewer → Approval → Final Output

Run:
$env:PYTHONPATH = (Get-Location).Path
python examples\live_run.py

The live demonstration prints:
- User task
- Planner-generated execution plan
- Worker draft
- Reviewer decision
- Reviewer feedback
- Rejection count
- Iteration count
- Review history
- Final output
A successful live run produced:
REVIEW STATUS:
approved

REJECTION COUNT:
0

ITERATIONS:
1

Two-Rejection Escalation Demonstration
examples/rejection_demo.py provides a deterministic demonstration of the bounded rejection safeguard.
It intentionally produces:
Reviewer #1 → REJECTED
        ↓
Worker revision
        ↓
Reviewer #2 → REJECTED
        ↓
ESCALATE
        ↓
END

Run:
$env:PYTHONPATH = (Get-Location).Path
python examples\rejection_demo.py

The demonstration produces:
Review 1: rejected
Review 2: rejected

REJECTION COUNT:
2

ITERATIONS:
2

FINAL OUTPUT:
REVIEW FAILED

The workflow reached two consecutive reviewer rejections
without producing an approved draft.

Review decisions recorded: 2

This demonstration is deterministic and does not require an additional LLM API call.
Project Structure
agenticx-multi-agent-langgraph/
│
├── app/
│   ├── __init__.py
│   ├── state.py
│   ├── prompts.py
│   ├── config.py
│   ├── nodes.py
│   └── graph.py
│
├── tests/
│   ├── test_routing.py
│   └── test_graph.py
│
├── examples/
│   ├── live_run.py
│   └── rejection_demo.py
│
├── docs/
│   └── architecture.md
│
├── .env.example
├── .gitignore
└── README.md

Technology Stack
- Python 3.11+
- LangGraph
- LangChain
- LangChain OpenAI integration
- Pydantic
- python-dotenv
- Pytest
Installation
Clone the Repository
git clone https://github.com/godswillmamus54-max/agenticx-multi-agent-langgraph.git
cd agenticx-multi-agent-langgraph

Create a Virtual Environment
python -m venv venv

Activate on Windows
.\venv\Scripts\Activate.ps1

Install Dependencies
pip install langgraph langchain langchain-openai python-dotenv pydantic pytest

Environment Configuration
Create a .env file in the project root:
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4o-mini

Never commit the .env file.
A safe template is provided in:
.env.example

The repository's .gitignore excludes .env.
Running the Tests
Run:
python -m pytest -q

Expected result:
8 passed

The tests use deterministic fake Planner, Worker, and Reviewer nodes for integration testing. This allows the graph's control flow to be verified without depending on unpredictable LLM responses.
Running the Live Workflow
The production graph uses the LLM-backed Planner, Worker, and Reviewer nodes.
After configuring the required environment variables, the compiled graph can be created with:
from app.graph import build_workflow_graph

graph = build_workflow_graph()


The production graph uses the real agent nodes by default.
The graph can also accept alternative node implementations for deterministic testing:
graph = build_workflow_graph(
    planner=test_planner,
    worker=test_worker,
    reviewer=test_reviewer,
)


This separation allows the workflow architecture to be tested independently from the external LLM service.
Design Decisions
Why LangGraph?
LangGraph provides explicit graph-based control flow and shared state, making the multi-agent workflow easier to reason about than an unconstrained chain of LLM calls.
Why Separate Planner, Worker, and Reviewer Roles?
Each agent has a focused responsibility:
Planner  → decides what should be done
Worker   → performs the planned work
Reviewer → evaluates the result

This separation makes the workflow easier to inspect, test, and extend.
Why Use Structured Reviewer Output?
The Reviewer controls graph routing, so its decision needs to be machine-readable.
The project uses a structured Pydantic model containing:
status
feedback

The allowed status values are:
approved
rejected

Why Limit Rejections?
Without a bounded retry policy, a Reviewer → Worker loop could continue indefinitely.
The two-rejection limit provides a deterministic termination condition.
Reliability Properties
The workflow provides:
- Explicit state
- Explicit agent responsibilities
- Explicit routing destinations
- Structured review decisions
- Bounded revision attempts
- Review history
- Terminal escalation
- Deterministic integration tests
- Reproducible demonstrations

These properties make the workflow easier to inspect and reason about than an unrestricted agent loop.
Future Improvements

Potential future improvements include:
- Persistent workflow checkpoints
- Human approval before escalation
- More specialized Worker agents
- Tool-using Workers
- Retrieval-augmented research
- Evaluation metrics for Reviewer quality
- LangSmith tracing
- API deployment with FastAPI
- Additional failure-mode tests

Project Status
Current implementation:
Core architecture        ✅
Explicit state           ✅
Planner                  ✅
Worker                   ✅
Reviewer                 ✅
Conditional routing      ✅
Revision loop            ✅
Two-rejection safeguard  ✅
Integration tests        ✅
8/8 tests passing        ✅
Documentation            ✅
Architecture diagram     ✅
Live LLM demo            ✅
GitHub publication       ✅
Internship submission    ⏳

Internship Task
This project was developed as the Multi-Agent Workflow with LangGraph project for the AgenticX AI Labs AI Agents & Automation internship.
The implementation demonstrates:
- Planner → Worker → Reviewer coordination
- Explicit shared state
- Conditional graph routing
- Reviewer rejection handling
- Two consecutive reviewer rejection handling
- Deterministic workflow testing
- LLM-backed production execution
- Bounded agent-loop behavior
- Runnable workflow demonstrations

Author
Ogheneochuko Godswill
AI Automation Engineer
AI Agents • Automation • LangGraph • APIs • Python
GitHub:
https://github.com/godswillmamus54-max

License
This project was created as an internship project and demonstration of multi-agent workflow engineering.