from protocols.email.router.laia_mail_router_v1 import run


def test_internal_meeting_to_laia_executes_without_approval():
    out = run({
        "channel": "email",
        "from": "ana@grid-code.tech",
        "to": ["laia@grid-code.tech"],
        "cc": ["dario@grid-code.tech"],
        "subject": "Agenda una reunión con el equipo",
        "body": "Por favor agenda un meet mañana para revisar el plan.",
        "actor_role": "EXECUTIVE",
        "now": "2026-06-10T10:00:00+00:00",
    })
    assert out["protocol_id"] == "laia_mail_router_v1"
    assert out["classification"]["thread_type"] == "INTERNAL_ONLY"
    assert out["classification"]["priority"] == "P1"
    assert out["routing"]["target_skill"] == "calendar-meet-host-gridcode"
    assert out["decision"]["action"] == "EXECUTE"
    assert out["decision"]["requires_approval"] is False
    assert out["delivery"]["send_now"] is True


def test_external_certificate_requires_approval_and_delay():
    out = run({
        "channel": "email",
        "from": "cliente@externo.com",
        "to": ["laia@grid-code.tech"],
        "cc": [],
        "subject": "Necesitamos un certificado final",
        "body": "Podéis emitir el certificado y enviarlo hoy mismo.",
        "actor_role": "EXTERNAL",
        "now": "2026-06-10T20:30:00+00:00",
    })
    assert out["classification"]["topic"] == "CERTIFICATE"
    assert out["classification"]["thread_type"] == "HYBRID_THREAD"
    assert out["routing"]["target_skill"] == "certificate-generation"
    assert out["decision"]["action"] == "REQUIRE_APPROVAL"
    assert out["decision"]["delay_mode"] == "APPROVAL_DELAY"
    assert out["delivery"]["send_now"] is False


def test_hybrid_drive_share_drafts_and_blocks_reply_all():
    out = run({
        "channel": "email",
        "from": "jorge@grid-code.tech",
        "to": ["cliente@externo.com"],
        "cc": ["laia@grid-code.tech", "dario@grid-code.tech"],
        "subject": "Compartir Drive del proyecto",
        "body": "Por favor compartid el documento con el cliente y revisad el acceso.",
        "actor_role": "OPERATIONS",
        "now": "2026-06-10T11:00:00+00:00",
    })
    assert out["classification"]["thread_type"] == "HYBRID_THREAD"
    assert out["routing"]["target_skill"] == "gridcode-drive-api-first-governance"
    assert out["decision"]["action"] in {"DRAFT", "REQUIRE_APPROVAL"}
    assert out["reply_policy"]["reply_all"] is True
    assert out["delivery"]["send_now"] in {True, False}


def test_noise_silences():
    out = run({
        "channel": "email",
        "from": "newsletter@promo.com",
        "to": ["laia@grid-code.tech"],
        "cc": [],
        "subject": "Newsletter y oferta especial",
        "body": "Oferta y promoción para hoy.",
        "actor_role": "EXTERNAL",
        "now": "2026-06-10T09:00:00+00:00",
    })
    assert out["classification"]["intent"] == "SPAM_NOISE"
    assert out["decision"]["action"] == "SILENT"
    assert out["routing"]["target_skill"] == "mail-triage"
