from app.graph import route_after_review


def test_approved_review_finishes():
    state = {
        "review_status": "approved",
        "rejection_count": 0,
    }

    assert route_after_review(state) == "finish"


def test_first_rejection_returns_to_worker():
    state = {
        "review_status": "rejected",
        "rejection_count": 1,
    }

    assert route_after_review(state) == "revise"


def test_second_rejection_escalates():
    state = {
        "review_status": "rejected",
        "rejection_count": 2,
    }

    assert route_after_review(state) == "escalate"


def test_unknown_review_status_escalates():
    state = {
        "review_status": "unexpected",
        "rejection_count": 0,
    }

    assert route_after_review(state) == "escalate"