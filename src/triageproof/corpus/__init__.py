"""triageproof corpus: pack metadata plus 50 authored crash-triage skills.

Skills are authored as plain dicts in ``part1``..``part3`` and loaded once
into the validated :class:`~triageproof.model.Skill` shape.
"""

from __future__ import annotations

from typing import Any

from ..model import skill_from_dict
from .part1 import SKILLS as PART1
from .part2 import SKILLS as PART2
from .part3 import SKILLS as PART3

PACK: dict[str, Any] = {
    "name": "triageproof",
    "version": "1.0.0",
    "category": "bug-bounty-triage",
    "license": "MIT",
    "runtime": "Claude Code, opencode, or any agent runtime that loads SKILL.md files",
    "description": (
        "50 validated skills for making a crash claim survive triage: canonical "
        "signatures, clustering, dedupe against advisories, blocking evidence "
        "gates and tamper-evident bundles, with a CLI that does each of them."
    ),
    "expected_skills": 50,
    "meta_keys": ("phase",),
    "requires_verification": False,
}

SKILLS: list[Any] = [skill_from_dict(raw) for raw in (*PART1, *PART2, *PART3)]
BY_SLUG: dict[str, Any] = {skill.slug: skill for skill in SKILLS}
