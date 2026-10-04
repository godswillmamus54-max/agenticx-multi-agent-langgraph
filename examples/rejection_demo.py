from app.graph import build_workflow_graph


def demo_planner(state):
    """Deterministic planner for demonstrating rejection handling."""
    return {
        "plan": [
            "Produce the requested draft.",
            "Address reviewer feedback when revisions are requested.",
        ]
    }


def demo_worker(state):
    """Deterministic worker that records each revision attempt."""
    iteration = state.get("iteration", 0) + 1

    if iteration == 1:
        draft = "Initial draft produced by the Worker."
    else:
        draft = (
            f"Revision {iteration - 1} produced by the Worker "
            "after reviewer feedback."
        )

    return {
        "draft": draft,
        "iteration": iteration,
    }


def demo_reviewer(state):
    """
    Deliberately reject the first two reviews.

    This makes the two-consecutive-rejection safeguard
    deterministic and reproducible for demonstration purposes.
    """
    history = list(state.get("review_history", []))
    review_number = len(history) + 1

    if review_number <= 2:
        status = "rejected"
        feedback = (
            f"Demonstration rejection #{review_number}: "
            "the draft requires further improvement."
        )
    else:
        status = "approved"
        feedback = ""

    rejection_count = (
        state.get("rejection_count", 0) + 1
        if status == "rejected"
        else 0
    )

    history.append(
        {
            "iteration": state.get("iteration", 0),
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


def main() -> None:
    initial_state = {
        "task": "Demonstrate the two-rejection escalation safeguard.",
        "plan": [],
        "draft": "",
        "review_status": "",
        "review_feedback": "",
        "rejection_count": 0,
        "iteration": 0,
        "review_history": [],
        "final_output": "",
    }

    workflow = build_workflow_graph(
        planner=demo_planner,
        worker=demo_worker,
        reviewer=demo_reviewer,
    )

    result = workflow.invoke(initial_state)

    print("\n" + "=" * 70)
    print("TWO-REJECTION ESCALATION DEMONSTRATION")
    print("=" * 70)

    print("\nREVIEW HISTORY:")
    for review in result["review_history"]:
        print(
            f"- Review {review['iteration']}: "
            f"{review['status']} | {review['feedback']}"
        )

    print("\nREJECTION COUNT:")
    print(result["rejection_count"])

    print("\nITERATIONS:")
    print(result["iteration"])

    print("\nFINAL OUTPUT:")
    print(result["final_output"])

    print("\n" + "=" * 70)
    print("ESCALATION DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()