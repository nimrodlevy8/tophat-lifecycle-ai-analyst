"""Skill detection and loading."""

from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"

SKILL_KEYWORDS = {
    "ab-test": ["ab test", "a/b test", "experiment", "variant", "control group", "significance"],
    "alert": ["alert", "anomaly", "spike", "drop", "unusual", "monitoring"],
    "deep-dive": ["deep dive", "investigate", "why did", "root cause", "breakdown"],
    "research": ["what if", "hypothesis", "opportunity", "sizing", "explore"],
    "measure": ["kpi", "metric", "measurement", "instrument", "success criteria", "framework"],
    "adhoc": [],  # default fallback
}


def detect_skill(question: str) -> str | None:
    """Detect which skill to use based on the question content."""
    q = question.lower()

    for skill, keywords in SKILL_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            return skill

    return "adhoc"


def load_skill(skill_name: str) -> str:
    """Load a skill prompt file."""
    skill_file = SKILLS_DIR / f"{skill_name}.md"
    if skill_file.exists():
        return f"# Skill: {skill_name}\n\n{skill_file.read_text().strip()}"
    return ""
