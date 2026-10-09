import subprocess


class GitError(RuntimeError):
    """Indique qu’une commande Git n’a pas pu être exécutée correctement."""


def get_diff(
    base_sha: str,
    head_sha: str,
    context_lines: int = 80,
) -> str:
    """Calcule le diff local entre deux révisions avec le contexte demandé."""
    result = subprocess.run(
        [
            "git",
            "diff",
            "--no-ext-diff",
            f"--unified={context_lines}",
            base_sha,
            head_sha,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise GitError(
            "Impossible de calculer le diff Git entre "
            f"{base_sha} et {head_sha} : {result.stderr.strip()}"
        )

    return result.stdout
