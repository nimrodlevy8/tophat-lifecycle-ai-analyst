"""Load relevant context files based on the question."""

from pathlib import Path

CONTEXT_DIR = Path(__file__).parent / "context"


def load_context(question: str) -> str:
    """Load context files relevant to the question.

    For now, loads all available context. Future: use embeddings or keyword
    matching to select only relevant files.
    """
    sections = []

    for subdir in ["methodology", "domain", "schemas", "templates"]:
        dir_path = CONTEXT_DIR / subdir
        if not dir_path.exists():
            continue
        for file in sorted(dir_path.glob("*.md")):
            content = file.read_text().strip()
            if content:
                sections.append(f"## {subdir}/{file.name}\n\n{content}")

    if not sections:
        return ""

    return "# Context\n\n" + "\n\n---\n\n".join(sections)
