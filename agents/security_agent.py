from pathlib import Path

from integrations.ollama import get_llm
from utils.review_response import validate_review_response


PROMPT_PATH = (
    Path(__file__).parent.parent
    / "prompts"
    / "security_review.txt"
)


class SecurityAgent:
    """Recherche les failles de sécurité introduites par une pull request."""

    def __init__(self):
        """Prépare le modèle et charge les consignes de sécurité."""
        self.llm = get_llm()
        self.prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    def review(
        self,
        changed_files: list[str],
        diff: str,
    ) -> dict:
        """Analyse le diff et renvoie les failles étayées par les changements."""
        prompt = self.prompt_template.format(
            changed_files="\n".join(changed_files),
            diff=diff,
        )

        return validate_review_response(
            self.llm.invoke(prompt),
            expected_type="security",
        )
