from protocols.email.read.email_read_v1 import run as run_read
from protocols.email.interpret.email_interpret_v1 import run as run_interpret
from protocols.email.write.email_write_v1 import run as run_write
from protocols.email.validate.email_validate_v1 import run as run_validate


def test_read_normalizes_count():
    out = run_read({"emails":[{"id":1,"from":"x","from_name":"X","to":["laia@grid-code.tech"],"cc":["dario@grid-code.tech"],"subject":"s","body":"b","timestamp":"t","is_forward":True}]})
    assert out["count"] == 1
    assert out["emails"][0]["id"] == "1"
    assert out["emails"][0]["to"] == ["laia@grid-code.tech"]
    assert out["emails"][0]["is_forward"] is True


def test_interpret_ticket_direct_to_laia_is_p1_and_reply_required():
    out = run_interpret({
        "subject": "GC-EV-20260506-0001",
        "body": "No carga",
        "to": ["laia@grid-code.tech"],
        "cc": ["dario@grid-code.tech"],
    })
    assert out["category"] == "ticket"
    assert out["priority"] == "p1"
    assert out["requires_reply"] is True
    assert out["action"] == "reply_required"


def test_interpret_laia_in_cc_is_p2_watch_notify():
    out = run_interpret({
        "subject": "Consulta comercial",
        "body": "Presupuesto para nuevo punto",
        "to": ["operaciones@grid-code.tech"],
        "cc": ["laia@grid-code.tech", "dario@grid-code.tech"],
    })
    assert out["category"] == "ticket"
    assert out["priority"] == "p2"
    assert out["requires_reply"] is False
    assert out["action"] == "notify_dario_watch"


def test_write_and_validate_ok():
    w = run_write({"name":"Carlos","context":"el cargador"})
    v = run_validate({"body": w["body"]})
    assert v["valid"] is True


def test_validate_rejects_compact_and_banned():
    bad = "Hola/te comento{json}\nSaludos,\nLaia"
    v = run_validate({"body": bad})
    assert v["valid"] is False
    assert len(v["errors"]) >= 1
