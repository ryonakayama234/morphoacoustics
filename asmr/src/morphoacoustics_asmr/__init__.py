"""Optional ASMR research catalog; NO physical plugins are adopted or enabled."""
from .catalog import ResearchItem, ResearchUnavailable, list_research, require_adopted

__all__ = ["ResearchItem", "ResearchUnavailable", "list_research", "require_adopted"]
