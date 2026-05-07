from protocols.email.read.email_read_v1 import run as run_read
from protocols.email.interpret.email_interpret_v1 import run as run_interpret
from protocols.email.write.email_write_v1 import run as run_write
from protocols.email.validate.email_validate_v1 import run as run_validate
from shared.learning.email_learning_rail_v1 import append_learning_record


def execute(raw_email: dict, dario_input: str = "", outcome: str = "pending", log_learning: bool = True):
    read_out = run_read({"emails": [raw_email]})
    first = read_out["emails"][0] if read_out["emails"] else {"subject": "", "body": ""}

    interp = run_interpret(
        {
            "subject": first.get("subject", ""),
            "body": first.get("body", ""),
            "to": first.get("to", []),
            "cc": first.get("cc", []),
            "from": first.get("from", ""),
            "from_name": first.get("from_name", ""),
            "is_forward": first.get("is_forward", False),
        }
    )

    draft = run_write({"name": first.get("from_name", ""), "context": "su consulta"})
    valid = run_validate({"body": draft["body"]})

    learning = None
    if log_learning:
        assist_message = interp.get("p1_assist_message") or interp.get("p2_notification") or ""
        learning = append_learning_record(
            {
                "priority": interp.get("priority", "p2"),
                "topic": interp.get("topic", "tema en seguimiento"),
                "request_summary": first.get("subject", "sin resumen"),
                "assist_message": assist_message,
                "dario_input": dario_input,
                "final_reply": draft.get("body", ""),
                "outcome": outcome,
                "improvement_note": "",
            }
        )

    return {
        "read": read_out,
        "interpret": interp,
        "write": draft,
        "validate": valid,
        "learning": learning,
    }
