from protocols.email.write.email_write_v1 import run
from shared.orchestration.email_response_orchestrator_v1 import orchestrate_email_response


def test_write_can_append_internal_capability_triggers():
    out = run({"name": "Lore", "context": "grid-code", "include_internal_capabilities": True})
    body = out["body"]
    assert "Podes contar conmigo para" in body
    assert "> 1) Hacer una meet" in body
    assert "> 7) Hacer certificados de validacion OCPP" in body
    assert "mailto:laia@grid-code.tech" in body
    assert "subject=" in body
    assert "body=" in body


def test_response_orchestrator_exposes_verified_trigger_catalog():
    out = orchestrate_email_response({
        "instruction": "Responder a Lore con el informe y dejar disponibles las opciones internas",
        "topic": "informe tecnico",
        "contact_name": "Lore",
        "to_email": "lore@grid-code.tech",
        "subject": "Re: Informe tecnico",
        "final_body": "Buenas Lore,\n\nSe estaría compartiendo el informe solicitado.\n\nSaludos,\nLaia",
    })
    assert out["internal_capabilities"]["enabled"] is True
    assert len(out["internal_capabilities"]["items"]) == 7
    assert out["internal_capabilities"]["items"][0]["trigger_id"] == "internal_meet"
    assert out["internal_capabilities"]["items"][6]["trigger_id"] == "ocpp_certificate"
