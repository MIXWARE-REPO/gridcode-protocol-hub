from typing import Dict, Any

PROTOCOL_ID = "email_write_v1"

def run(inputs: Dict[str, Any]) -> Dict[str, Any]:
    name = inputs.get("name", "") or ""
    context = inputs.get("context", "su consulta")
    next_step = inputs.get("next_step", "Se gestionará con la prioridad correspondiente.")

    greeting = f"Buenas {name}," if name else "Buenas,"
    body = (
        f"{greeting}\n\n"
        f"Gracias por el mensaje.\n\n"
        f"En relación con {context}, se estaría revisando la información para darle el tratamiento correspondiente.\n\n"
        f"{next_step}\n\n"
        f"Saludos,\nLaia"
    )
    return {"protocol_id": PROTOCOL_ID, "body": body}
