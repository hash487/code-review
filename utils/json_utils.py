import json


def parse_json_response(response) -> dict | list:
    """Convertit la réponse du modèle en format JSON."""
    content = response.content.strip()

    if content.startswith("```json"):
        content = content[7:]

    if content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()
    return json.loads(content)
