from protocols.email.contextualize.email_contact_context_v1 import run


def test_new_subject_but_known_sender_expands_context():
    out = run({
        "email": {"from": "victor@cliente.com", "subject": "Nuevo asunto", "cc": ["laia@grid-code.tech"], "status": "pending"},
        "known_contacts": [{"email": "victor@cliente.com"}],
        "contact_history": [
            {"topic": "RFID", "tone": "formal"},
            {"topic": "Firmware", "tone": "formal"},
            {"topic": "Backend", "tone": "formal"},
        ],
        "gridcode_domains": ["grid-code.tech"],
    })
    assert out["known_sender"] is True
    assert out["relation_detected"] is True
    assert out["context_level"] == "expanded"
    assert out["tone_hint"] == "formal"
    assert len(out["last_3_topics"]) == 3


def test_unknown_sender_no_history_none_context():
    out = run({
        "email": {"from": "nuevo@empresa.com", "subject": "Consulta", "cc": [], "status": "pending"},
        "known_contacts": [],
        "contact_history": [],
    })
    assert out["known_sender"] is False
    assert out["relation_detected"] is False
    assert out["context_level"] == "none"
