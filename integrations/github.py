import os

import requests
from github import Github


GRAPHQL_URL = "https://api.github.com/graphql"


class GitHubIntegration:
    """Regroupe les appels GitHub nécessaires à la revue des pull requests."""

    def __init__(self):
        """Se connecte au dépôt GitHub indiqué dans la configuration."""
        token = os.getenv("GITHUB_TOKEN")
        repository = os.getenv("GITHUB_REPOSITORY")

        if not token:
            raise ValueError(
                "GITHUB_TOKEN is not set."
            )

        if not repository:
            raise ValueError(
                "GITHUB_REPOSITORY is not set."
            )

        self.token = token
        self.repository_name = repository

        self.github = Github(token)
        self.repo = self.github.get_repo(
            repository
        )

    def get_pull_request(
        self,
        pull_number: int,
    ):
        """Récupère une pull request à partir de son numéro."""
        return self.repo.get_pull(
            pull_number
        )

    def get_linked_issues(
        self,
        pull_number: int,
    ) -> list[dict]:
        """Récupère les issues que la pull request vise à clôturer."""

        owner, repo = (
            self.repository_name.split(
                "/",
                1,
            )
        )

        query = """
        query(
            $owner: String!,
            $repo: String!,
            $number: Int!
        ) {
            repository(
                owner: $owner,
                name: $repo
            ) {
                pullRequest(
                    number: $number
                ) {
                    closingIssuesReferences(
                        first: 20
                        # Inclut aussi les issues associées sans mot-clé de clôture.
                        excludeUserLinked: false
                    ) {
                        nodes {
                            number
                            title
                            body
                            url
                            state
                        }
                    }
                }
            }
        }
        """

        response = requests.post(
            GRAPHQL_URL,
            headers={
                "Authorization": (
                    f"Bearer {self.token}"
                ),
                "Accept": (
                    "application/vnd.github+json"
                ),
                "Content-Type": (
                    "application/json"
                ),
            },
            json={
                "query": query,
                "variables": {
                    "owner": owner,
                    "repo": repo,
                    "number": pull_number,
                },
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            raise RuntimeError(
                "GitHub GraphQL error: "
                + str(data["errors"])
            )

        pull_request = (
            data["data"]["repository"][
                "pullRequest"
            ]
        )

        if pull_request is None:
            raise RuntimeError(
                f"Pull request #{pull_number} "
                "was not found."
            )

        return (
            pull_request[
                "closingIssuesReferences"
            ]["nodes"]
        )

    def get_issue_body(
        self,
        issue_number: int,
    ) -> str:
        """Récupère le texte d’une issue, ou une chaîne vide s’il est absent."""

        issue = self.repo.get_issue(
            issue_number
        )

        return issue.body or ""

    def get_pull_request_body(
        self,
        pull_number: int,
    ) -> str:
        """Récupère la description de la pull request, ou une chaîne vide."""

        pr = self.get_pull_request(
            pull_number
        )

        return pr.body or ""

    def get_pull_request_files(
        self,
        pull_number: int,
    ) -> list[dict]:
        """Récupère les fichiers modifiés, leurs métadonnées et leurs différences."""

        pr = self.get_pull_request(
            pull_number
        )

        files = pr.get_files()

        results = []

        for file in files:
            results.append(
                {
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch or "",
                }
            )

        return results

    def post_comment(
        self,
        pull_number: int,
        body: str,
    ) -> None:
        """Ajoute un commentaire à la pull request."""

        pr = self.get_pull_request(
            pull_number
        )

        pr.create_issue_comment(
            body
        )