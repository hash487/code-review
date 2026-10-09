from pathlib import Path

from integrations.ollama import get_llm
from utils.review_response import validate_review_response


PROMPT_PATH = (
    Path(__file__).parent.parent
    / "prompts"
    / "code_quality.txt"
)


class CodeQualityAgent:
    """Vérifie les exigences de l’issue et la qualité des changements."""

    def __init__(self):
        """Prépare le modèle et charge les consignes de revue de code."""
        self.llm = get_llm()
        self.prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    def review(
        self,
        requirements: str,
        pr_description: str,
        changed_files: list[str],
        diff: str,
    ) -> dict:
        """Repère les erreurs de code en tenant compte du contexte de l’issue."""
        prompt = self.prompt_template.format(
            requirements=requirements,
            pr_description=pr_description,
            changed_files="\n".join(changed_files),
            diff=diff,
        )

        return {
            "reviews": [
                validate_review_response(
                    self.llm.invoke(prompt),
                    expected_type="code_quality",
                )
            ],
        }