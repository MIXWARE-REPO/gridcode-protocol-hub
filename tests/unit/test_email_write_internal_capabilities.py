from protocols.email.write.email_write_v1 import run
from shared.orchestration.email_response_orchestrator_v1 import orchestrate_email_response


def test_write_auto_appends_internal_capability_triggers_for_internal_mail():
    out = run({"name": "Lore", "context": "grid-code", "recipient_email": "lore@grid-code.tech"})
    body = out["body"]
    assert "Podes contar conmigo para" in body
    assert "> 1) Meet - mailto:laia@grid-code.tech" in body
    assert "> 7) OCPP - mailto:laia@grid-code.tech" in body
    assert "subject=" in body
    assert "body=" in body
    assert out["internal_capabilities"]["mode"] == "compact"
    assert out["body_html"] is not None
    assert "<a href=" in out["body_html"]


def test_write_can_force_and_select_trigger():
    out = run({
        "name": "Lore",
        "context": "informe tecnico OCPP",
        "recipient_email": "lore@grid-code.tech",
        "selected_trigger": "ocpp_certificate",
    })
    assert out["internal_capabilities"]["selected"]["trigger_id"] == "ocpp_certificate"
    assert out["trigger_selector"]["selected_trigger"] == "ocpp_certificate"
    assert out["internal_capabilities"]["mode"] == "compact"


def test_response_orchestrator_exposes_verified_trigger_catalog_and_selector():
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
    assert out["trigger_selector"]["selected"] is not None
    assert out["trigger_selector"]["selected"]["trigger_id"] in {item["trigger_id"] for item in out["internal_capabilities"]["items"]}
    assert out["internal_capabilities"]["mode"] == "compact"
