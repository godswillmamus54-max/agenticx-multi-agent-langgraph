from app.graph import build_workflow_graph


def make_initial_state():
    """Return a complete deterministic workflow state for integration tests."""
    return {
        "task": "Create a concise research report.",
        "plan": [],
        "draft": "",
        "review_status": "",
        "review_feedback": "",
        "rejection_count": 0,
        "iteration": 0,
        "review_history": [],
        "final_output": "",
    }


def test_compiled_graph_approval_path():
    """Planner → Worker → Reviewer(approved) → Finish."""

    def fake_planner(state):
        return {
            "plan": [
                "Understand the task",
                "Produce the requested report",
            ]
        }

    def fake_worker(state):
        return {
            "draft": "Approved research report.",
            "iteration": state["iteration"] + 1,
        }

    def fake_reviewer(state):
        return {
            "review_status": "approved",
            "review_feedback": "",
            "rejection_count": 0,
            "review_history": [
                {
                    "iteration": state["iteration"],
                    "status": "approved",
                    "feedback": "",
                }
            ],
        }

    graph = build_workflow_graph(
        planner=fake_planner,
        worker=fake_worker,
        reviewer=fake_reviewer,
    )

    result = graph.invoke(make_initial_state())

    assert result["review_status"] == "approved"
    assert result["final_output"] == "Approved research report."
    assert result["rejection_count"] == 0
    assert len(result["review_history"]) == 1


def test_compiled_graph_reject_then_approve():
    """Planner → Worker → Reject → Worker → Approve → Finish."""

    def fake_planner(state):
        return {
            "plan": [
                "Understand the task",
                "Produce the requested report",
            ]
        }

    def fake_worker(state):
        iteration = state["iteration"] + 1

        if iteration == 1:
            return {
                "draft": "First draft requiring revision.",
                "iteration": iteration,
            }

        return {
            "draft": "Revised and approved research report.",
            "iteration": iteration,
        }

    def fake_reviewer(state):
        history = list(state["review_history"])

        if len(history) == 0:
            status = "rejected"
            feedback = "Add the missing research details."
            rejection_count = 1
        else:
            status = "approved"
            feedback = ""
            rejection_count = 0

        history.append(
            {
                "iteration": state["iteration"],
                "status": status,
                "feedback": feedback,
            }
        )

        return {
            "review_status": status,
            "review_feedback": feedback,
            "rejection_count": rejection_count,
            "review_history": history,
        }

    graph = build_workflow_graph(
        planner=fake_planner,
        worker=fake_worker,
        reviewer=fake_reviewer,
    )

    result = graph.invoke(make_initial_state())

    assert result["review_status"] == "approved"
    assert result["final_output"] == "Revised and approved research report."
    assert result["rejection_count"] == 0
    assert len(result["review_history"]) == 2
    assert result["review_history"][0]["status"] == "rejected"
    assert result["review_history"][1]["status"] == "approved"


def test_compiled_graph_two_rejections_escalate():
    """Planner → Worker → Reject → Worker → Reject → Escalate → End."""

    def fake_planner(state):
        return {
            "plan": [
                "Understand the task",
                "Produce the requested report",
            ]
        }

    def fake_worker(state):
        return {
            "draft": f"Draft iteration {state['iteration'] + 1}.",
            "iteration": state["iteration"] + 1,
        }

    def fake_reviewer(state):
        history = list(state["review_history"])
        rejection_count = state["rejection_count"] + 1

        history.append(
            {
                "iteration": state["iteration"],
                "status": "rejected",
                "feedback": "The draft still requires improvement.",
            }
        )

        return {
            "review_status": "rejected",
            "review_feedback": "The draft still requires improvement.",
            "rejection_count": rejection_count,
            "review_history": history,
        }

    graph = build_workflow_graph(
        planner=fake_planner,
        worker=fake_worker,
        reviewer=fake_reviewer,
    )

    result = graph.invoke(make_initial_state())

    assert result["review_status"] == "rejected"
    assert result["rejection_count"] == 2
    assert len(result["review_history"]) == 2
    assert result["final_output"].startswith("REVIEW FAILED")
    assert "two consecutive reviewer rejections" in result["final_output"]


def test_compiled_graph_does_not_loop_after_two_rejections():
    """Two consecutive rejections must terminate through escalation."""

    call_counts = {
        "planner": 0,
        "worker": 0,
        "reviewer": 0,
    }

    def fake_planner(state):
        call_counts["planner"] += 1
        return {
            "plan": ["Produce the requested report"],
        }

    def fake_worker(state):
        call_counts["worker"] += 1
        return {
            "draft": "Rejected draft.",
            "iteration": state["iteration"] + 1,
        }

    def fake_reviewer(state):
        call_counts["reviewer"] += 1

        history = list(state["review_history"])
        rejection_count = state["rejection_count"] + 1

        history.append(
            {
                "iteration": state["iteration"],
                "status": "rejected",
                "feedback": "Needs improvement.",
            }
        )

        return {
            "review_status": "rejected",
            "review_feedback": "Needs improvement.",
            "rejection_count": rejection_count,
            "review_history": history,
        }

    graph = build_workflow_graph(
        planner=fake_planner,
        worker=fake_worker,
        reviewer=fake_reviewer,
    )

    result = graph.invoke(make_initial_state())

    assert call_counts["planner"] == 1
    assert call_counts["worker"] == 2
    assert call_counts["reviewer"] == 2

    assert result["rejection_count"] == 2
    assert len(result["review_history"]) == 2
    assert result["final_output"].startswith("REVIEW FAILED")