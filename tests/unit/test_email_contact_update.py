from protocols.email.contact_update.email_contact_update_v1 import run


def test_create_when_contact_missing_and_update_suggested():
    out = run({
        "contact": {},
        "context": {
            "sender": "victor@cliente.com",
            "known_sender": False,
            "relation_detected": True,
            "context_level": "expanded",
            "tone_hint": "formal",
            "last_3_topics": ["Backend", "RFID"],
            "contact_update_suggested": True,
        },
        "email": {"status": "pending"},
        "policy": {"max_topics": 3},
    })
    assert out["action"] == "create"
    assert out["update_payload"]["tone_profile"] == "formal"


def test_minimal_when_cc_only():
    out = run({
        "contact": {"email": "x@x.com", "last_topics": ["Old"]},
        "context": {
            "sender": "x@x.com",
            "known_sender": True,
            "relation_detected": True,
            "context_level": "expanded",
            "tone_hint": "neutral",
            "last_3_topics": ["A", "B"],
            "contact_update_suggested": True,
        },
        "email": {"status": "pending", "is_cc_only": True},
    })
    assert out["action"] == "minimal_update"
    assert "pending_state" in out["update_payload"]


def test_skip_when_not_suggested():
    out = run({
        "context": {
            "sender": "new@x.com",
            "known_sender": False,
            "relation_detected": False,
            "context_level": "none",
            "contact_update_suggested": False,
        },
        "email": {"status": "pending"}
    })
    assert out["action"] == "skip"
    assert out["update_payload"] == {}
