from pathlib import Path

from shared.learning.email_learning_rail_v1 import append_learning_record


def test_append_learning_record_creates_jsonl(tmp_path: Path):
    out = append_learning_record(
        {
            "priority": "p1",
            "topic": "garantía cargador",
            "request_summary": "cliente pide visita",
            "assist_message": "Me llegó un mail...",
            "dario_input": "decir semana próxima",
            "final_reply": "Buenas...",
            "outcome": "respondio_ok",
            "improvement_note": "mantener cierre breve",
        },
        log_path=tmp_path / "email_learning_log.jsonl",
    )

    assert out["saved"] is True
    assert Path(out["path"]).exists()
    content = Path(out["path"]).read_text(encoding="utf-8")
    assert "garantía cargador" in content
    assert "respondio_ok" in content
