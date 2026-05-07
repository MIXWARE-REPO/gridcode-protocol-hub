from shared.orchestration.email_response_orchestrator_v1 import orchestrate_email_response


def test_orchestrator_detects_commitment_and_creates_task():
    payload = {
        "instruction": "contestale que lo recibimos y lo vemos mañana",
        "topic": "garantía cargador",
        "contact_name": "Víctor",
        "to_email": "victor@cliente.com",
        "subject": "Re: Garantía",
        "final_body": "Buenas Víctor,\n\nGracias por el mensaje. Se estaría revisando y se avanzará mañana.\n\nSaludos,\nLaia",
    }
    out = orchestrate_email_response(payload)
    assert out["protocol"] == "email_response_orchestrator_v1"
    assert out["confirmation"]["summary"]["has_commitments"] is True
    assert out["confirmation"]["summary"]["tasks_to_schedule"] >= 1


def test_orchestrator_style_validation_catches_bad_close():
    payload = {
        "instruction": "contestale lo que sea",
        "topic": "tema",
        "contact_name": "Cliente",
        "to_email": "x@x.com",
        "subject": "Re: Tema",
        "final_body": "Hola, te comento rapido",
    }
    out = orchestrate_email_response(payload)
    assert out["style_validation"]["valid"] is False
    assert len(out["style_validation"]["errors"]) >= 1
