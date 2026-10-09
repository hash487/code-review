from utils.json_utils import parse_json_response


def validate_review_response(
    response: object,
    expected_type: str,
) -> dict:
    """Vérifie qu’une réponse d’agent respecte le format JSON attendu."""
    review = parse_json_response(response)

    if not isinstance(review, dict):
        raise ValueError("La réponse de revue doit être un objet JSON.")

    if set(review) != {"review_type", "problems"}:
        raise ValueError(
            "La réponse de revue doit contenir exactement "
            "review_type et problems."
        )

    if review.get("review_type") != expected_type:
        raise ValueError(f"Type de revue attendu : {expected_type}.")

    problems = review.get("problems")
    if not isinstance(problems, list):
        raise ValueError(
            "La réponse de revue doit contenir une liste « problems »."
        )

    required_fields = {
        "severity",
        "description",
        "file",
        "line",
        "suggestion",
    }
    # Les agents emploient ces valeurs dans le JSON; le formateur les traduit
    # ensuite pour le commentaire publié.
    allowed_severities = {"critical", "high", "medium", "low"}

    for problem in problems:
        if not isinstance(problem, dict) or set(problem) != required_fields:
            raise ValueError(
                "Chaque problème doit contenir exactement severity, "
                "description, file, line et suggestion."
            )

        if (
            not isinstance(problem["severity"], str)
            or problem["severity"] not in allowed_severities
        ):
            raise ValueError(
                "La sévérité doit être critical, high, medium ou low."
            )

        if (
            not isinstance(problem["description"], str)
            or not problem["description"].strip()
        ):
            raise ValueError(
                "La description du problème doit être un texte non vide."
            )

        if problem["file"] is not None and not isinstance(
            problem["file"], str
        ):
            raise ValueError("Le fichier doit être un texte ou null.")

        if problem["line"] is not None and (
            not isinstance(problem["line"], int)
            or isinstance(problem["line"], bool)
            or problem["line"] < 1
        ):
            raise ValueError("La ligne doit être un entier positif ou null.")

        if (
            not isinstance(problem["suggestion"], str)
            or not problem["suggestion"].strip()
        ):
            raise ValueError("La suggestion doit être un texte non vide.")

    return review
