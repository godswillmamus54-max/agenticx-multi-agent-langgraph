
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from app.graph import build_workflow_graph

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application
app = FastAPI(
    title="AgenticX Multi-Agent Research API",
    description="Planner, Worker and Reviewer workflow powered by LangGraph.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Compile the existing workflow once
workflow = build_workflow_graph()


class TaskRequest(BaseModel):
    task: str = Field(
        min_length=1,
        max_length=10000,
        description="The task to be processed by the multi-agent system.",
    )


@app.get("/")
def home():
    return {
        "application": "AgenticX Multi-Agent Research Workflow",
        "status": "running",
        "documentation": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "workflow": "initialized",
    }


@app.post("/run")
def run_task(request: TaskRequest):
    task = request.task.strip()

    if not task:
        raise HTTPException(
            status_code=422,
            detail="Task cannot be empty or whitespace.",
        )

    initial_state = {
        "task": task,
        "plan": [],
        "draft": "",
        "review_status": "",
        "review_feedback": "",
        "rejection_count": 0,
        "iteration": 0,
        "review_history": [],
        "final_output": "",
    }

    try:
        logger.info("Starting workflow execution")

        result = workflow.invoke(initial_state)

        logger.info("Workflow execution completed")

        return {
            "status": "completed",
            "task": task,
            "plan": result.get("plan", []),
            "final_output": result.get("final_output", ""),
            "review_status": result.get("review_status", ""),
            "rejection_count": result.get("rejection_count", 0),
            "iterations": result.get("iteration", 0),
            "review_history": result.get("review_history", []),
        }

    except Exception:
        logger.exception("Workflow execution failed")

        raise HTTPException(
            status_code=502,
            detail="The multi-agent workflow could not complete the task. Check server logs.",
        )
