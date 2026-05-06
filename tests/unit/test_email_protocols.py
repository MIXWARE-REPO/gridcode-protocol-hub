from protocols.email.read.email_read_v1 import run as run_read
from protocols.email.interpret.email_interpret_v1 import run as run_interpret
from protocols.email.write.email_write_v1 import run as run_write
from protocols.email.validate.email_validate_v1 import run as run_validate


def test_read_normalizes_count():
    out = run_read({"emails":[{"id":1,"from":"x","subject":"s","body":"b","timestamp":"t"}]})
    assert out["count"] == 1
    assert out["emails"][0]["id"] == "1"


def test_interpret_ticket():
    out = run_interpret({"subject":"GC-EV-20260506-0001","body":"No carga"})
    assert out["category"] == "ticket"


def test_write_and_validate_ok():
    w = run_write({"name":"Carlos","context":"el cargador"})
    v = run_validate({"body": w["body"]})
    assert v["valid"] is True


def test_validate_rejects_compact_and_banned():
    bad = "Hola/te comento{json}\nSaludos,\nLaia"
    v = run_validate({"body": bad})
    assert v["valid"] is False
    assert len(v["errors"]) >= 1
