from __future__ import annotations

from .base import BaseMatch
from .basketball import BasketballMatch


class MatchFactory:
    """
    Creates the appropriate match model based on 365scores `sportId`.
    """

    SPORT_ID_TO_CLASS: dict[int, type[BaseMatch]] = {
        2: BasketballMatch,
    }

    @classmethod
    def get_match_instance(cls, data: dict) -> BaseMatch:
        sport_id = data.get("sportId")
        match_cls = cls.SPORT_ID_TO_CLASS.get(int(sport_id)) if sport_id is not None else None
        if match_cls is None:
            raise ValueError(f"Unsupported or missing sportId: {sport_id!r}")
        return match_cls.model_validate(data)

