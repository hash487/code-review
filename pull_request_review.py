import os

from dotenv import load_dotenv

from agents.code_quality_agent import (
    CodeQualityAgent,
)
from agents.security_agent import (
    SecurityAgent,
)
from integrations.git import (
    get_diff,
)
from integrations.github import (
    GitHubIntegration,
)
from review_formatter import (
    format_review,
)


load_dotenv()


def main():
    """Lance les analyses de la pull request et publie leur résultat."""
    # ----------------------------------------
    # 1. Connexion à GitHub
    # ----------------------------------------

    github = GitHubIntegration()

    pull_number = int(
        os.environ["GITHUB_PR_NUMBER"]
    )

    print(
        f"Reviewing PR #{pull_number}"
    )

    pr = github.get_pull_request(
        pull_number
    )

    print(
        f"PR: {pr.title}"
    )

    # ----------------------------------------
    # 2. Recherche de l’issue liée à la pull request
    # ----------------------------------------

    linked_issues = (
        github.get_linked_issues(
            pull_number
        )
    )

    if not linked_issues:
        raise RuntimeError(
            "No linked GitHub Issue found. "
            "Link an Issue to this PR."
        )

    if len(linked_issues) > 1:
        raise RuntimeError(
            "Multiple linked GitHub Issues "
            "were found. "
            "The first version of this reviewer "
            "expects exactly one linked Issue."
        )

    issue = linked_issues[0]

    issue_number = issue["number"]

    print(
        f"Linked Issue: #{issue_number}"
    )

    issue_body = (
        issue.get("body") or ""
    )

    # ----------------------------------------
    # 3. Récupération des fichiers modifiés et du diff avec contexte
    # ----------------------------------------

    pr_files = (
        github.get_pull_request_files(
            pull_number
        )
    )

    changed_files = [
        file["filename"]
        for file in pr_files
    ]

    # Le diff local inclut 80 lignes de contexte autour de chaque changement,
    # contrairement aux extraits de patch parfois incomplets renvoyés par l’API.
    diff = get_diff(
        pr.base.sha,
        pr.head.sha,
    )

    print(
        f"Changed files: "
        f"{len(changed_files)}"
    )

    # ----------------------------------------
    # 4. Analyses de conformité, de qualité et de sécurité
    # ----------------------------------------

    review_agent = (
        CodeQualityAgent()
    )

    reviews = review_agent.review(
        requirements=issue_body,
        pr_description=pr.body or "",
        changed_files=changed_files,
        diff=diff,
    )

    # L’analyse de sécurité est séparée pour qu’elle se concentre uniquement
    # sur les vulnérabilités, sans répéter les autres constats.
    security_agent = SecurityAgent()
    security_review = security_agent.review(
        changed_files=changed_files,
        diff=diff,
    )
    reviews["reviews"].append(security_review)

    # ----------------------------------------
    # 5. Mise en forme de la revue
    # ----------------------------------------

    review_text = format_review(reviews)

    # ----------------------------------------
    # 6. Publication de la revue sur GitHub
    # ----------------------------------------

    github.post_comment(
        pull_number,
        review_text,
    )

    print(
        "Review posted to GitHub."
    )


if __name__ == "__main__":
    main()