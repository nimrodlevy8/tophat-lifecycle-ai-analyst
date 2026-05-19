"""Core agent logic — builds prompts, calls Claude, returns analysis."""

from pathlib import Path

import anthropic

from tophat.context_loader import load_context
from tophat.skills import load_skill, detect_skill

CLIENT = anthropic.Anthropic()
MODEL = "claude-sonnet-4-6-20250514"
CONTEXT_DIR = Path(__file__).parent / "context"
SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"


SYSTEM_PROMPT = """\
You are the dedicated Product Analyst for the Lifecycle vertical in Monopoly GO!.
You operate as a self-sufficient analyst embedded between the Lifecycle team and \
the Engagement Engine team.

Lead with the answer, then evidence, then recommendation.
Use business-friendly language. Recommendations should be specific and tied to \
the teams' levers.

When you don't have enough context, ask — don't fabricate.
"""


def ask_agent(question: str, skill: str | None = None) -> str:
    """Process a question through the analyst agent."""
    chosen_skill = skill or detect_skill(question)
    skill_prompt = load_skill(chosen_skill) if chosen_skill else ""
    context = load_context(question)

    messages = [
        {
            "role": "user",
            "content": f"{skill_prompt}\n\n{context}\n\nQuestion: {question}",
        }
    ]

    response = CLIENT.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    return response.content[0].text
