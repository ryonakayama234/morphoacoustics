"""Read-only research directory, not an ASMR physical simulation service."""
from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
import json


@dataclass(frozen=True, slots=True)
class ResearchItem:
    id: str
    area: str
    state: str
    core_pr: int
    core_issue: int | None
    branch: str
    description: str


class ResearchUnavailable(RuntimeError):
    """An ASMR research candidate is NOT an authorized importable runtime feature."""


def list_research() -> tuple[ResearchItem, ...]:
    """Return the frozen metadata shipped with *this* optional package version.

    This function never imports/retrieves/executes GitHub PR source code.
    """
    path = files("morphoacoustics_asmr").joinpath("research_registry.json")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != "asmr.workspace.research-registry.v1":
        raise ResearchUnavailable("unrecognized ASMR registry schema")
    items = tuple(ResearchItem(**r) for r in raw["items"])
    if any(x.state != "RESEARCH_ONLY" for x in items):
        raise ResearchUnavailable("registry contains an unreviewed feature activation")
    if len({x.id for x in items}) != len(items):
        raise ResearchUnavailable("duplicate feature IDs")
    return items


def require_adopted(feature_id: str) -> None:
    """Fail closed. There is deliberately NO feature provider/loader in v0.0.1."""
    known = {item.id for item in list_research()}
    if feature_id not in known:
        raise ResearchUnavailable(f"unknown ASMR research feature: {feature_id}")
    raise ResearchUnavailable(
        f"ASMR feature {feature_id} is RESEARCH_ONLY; no provider is adopted or installed"
    )
