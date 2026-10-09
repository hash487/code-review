def format_review(review) -> str:
    """Rédige le commentaire final à partir des résultats des agents."""
    if not isinstance(review, dict) or not isinstance(
        review.get("reviews"), list
    ):
        raise ValueError(
            "La revue finale doit contenir une liste « reviews »."
        )

    category_names = {
        "code_quality": "Qualité du code",
        "security": "Sécurité",
    }
    severity_names = {
        "critical": "Critique",
        "high": "Élevée",
        "medium": "Moyenne",
        "low": "Faible",
    }

    # Les catégories sont affichées dans cet ordre, même si les agents répondent
    # dans un ordre différent.
    review_by_type = {}
    for agent_review in review["reviews"]:
        if not isinstance(agent_review, dict):
            raise ValueError("Chaque réponse d’agent doit être un objet JSON.")

        review_type = agent_review.get("review_type")
        if review_type not in category_names:
            raise ValueError(f"Type de revue inconnu : {review_type}.")

        if review_type in review_by_type:
            raise ValueError(f"Type de revue répété : {review_type}.")

        problems = agent_review.get("problems")
        if not isinstance(problems, list):
            raise ValueError(
                f"La catégorie {review_type} doit contenir une liste problems."
            )

        review_by_type[review_type] = problems

    expected_types = set(category_names)
    if set(review_by_type) != expected_types:
        raise ValueError("La revue doit contenir les deux catégories attendues.")

    has_problems = any(review_by_type.values())
    lines = [
        "## 🤖 Revue finale du code",
        "",
        (
            "❌ Des problèmes ont été relevés."
            if has_problems
            else "✅ Aucun problème n’a été relevé."
        ),
        "",
    ]

    for index, (review_type, category_name) in enumerate(
        category_names.items()
    ):
        if index:
            lines.extend(["---", ""])

        lines.extend([f"### {category_name}", ""])
        problems = review_by_type[review_type]

        # Affiche aussi les catégories sans problème pour confirmer qu’elles ont
        # bien été examinées.
        if not problems:
            lines.extend(["Aucun problème relevé.", ""])
            continue

        for index, problem in enumerate(problems, start=1):
            location = problem["file"] or "Fichier non déterminé"
            if problem["line"] is not None:
                location += f", ligne {problem['line']}"

            lines.extend(
                [
                    (
                        f"#### {index}. "
                        f"{severity_names[problem['severity']]}"
                    ),
                    "",
                    f"**Emplacement :** `{location}`",
                    "",
                    problem["description"],
                    "",
                    f"**Suggestion :** {problem['suggestion']}",
                    "",
                ]
            )

    return "\n".join(lines)