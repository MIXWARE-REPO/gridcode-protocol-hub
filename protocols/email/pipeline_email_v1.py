from protocols.email.read.email_read_v1 import run as run_read
from protocols.email.interpret.email_interpret_v1 import run as run_interpret
from protocols.email.write.email_write_v1 import run as run_write
from protocols.email.validate.email_validate_v1 import run as run_validate


def execute(raw_email: dict):
    read_out = run_read({"emails": [raw_email]})
    first = read_out["emails"][0] if read_out["emails"] else {"subject":"","body":""}
    interp = run_interpret({"subject": first.get("subject",""), "body": first.get("body","")})
    draft = run_write({"name": "", "context": "su consulta"})
    valid = run_validate({"body": draft["body"]})
    return {"read": read_out, "interpret": interp, "write": draft, "validate": valid}
