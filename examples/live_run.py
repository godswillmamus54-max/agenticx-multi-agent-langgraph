from app.graph import build_workflow_graph


def main() -> None:
    task = (
        "Explain why explicit shared state is important in a "
        "multi-agent workflow. Give three clear reasons and a "
        "short practical example."
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

    workflow = build_workflow_graph()

    result = workflow.invoke(initial_state)

    print("\n" + "=" * 70)
    print("MULTI-AGENT LANGGRAPH WORKFLOW — LIVE RUN")
    print("=" * 70)

    print("\nUSER TASK:")
    print(result["task"])

    print("\nPLAN:")
    for step in result["plan"]:
        print(f"- {step}")

    print("\nWORKER DRAFT:")
    print(result["draft"])

    print("\nREVIEW STATUS:")
    print(result["review_status"])

    print("\nREVIEW FEEDBACK:")
    print(result["review_feedback"] or "(none)")

    print("\nREJECTION COUNT:")
    print(result["rejection_count"])

    print("\nITERATIONS:")
    print(result["iteration"])

    print("\nREVIEW HISTORY:")
    for review in result["review_history"]:
        print(
            f"- Iteration {review['iteration']}: "
            f"{review['status']} | {review['feedback'] or '(none)'}"
        )

    print("\nFINAL OUTPUT:")
    print(result["final_output"])

    print("\n" + "=" * 70)
    print("LIVE WORKFLOW COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()