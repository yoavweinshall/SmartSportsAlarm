from __future__ import annotations

from .base import BaseMatch
from .basketball import BasketballMatch, NCAABasketBallMatch


class MatchFactory:
    """
    Creates the appropriate match model based on 365scores `sportId`.
    """
    NCAA_COMPETITION_IDS = {7630, 109}

    SPORT_ID_TO_CLASS: dict[int, type[BaseMatch]] = {
        2: BasketballMatch,
    }

    @classmethod
    def get_match_instance(cls, data: dict) -> BaseMatch:
        sport_id = int(data.get("sport_id"))
        competition_id = int(data.get("competition_id"))

        if sport_id == 2:  # NCAA Basketball games are built from halves and not quarters
            if competition_id in cls.NCAA_COMPETITION_IDS:
                return NCAABasketBallMatch.model_validate(data)
            else:
                return BasketballMatch.model_validate(data)

        match_cls = cls.SPORT_ID_TO_CLASS.get(sport_id) if sport_id is not None else None
        if match_cls is None:
            raise ValueError(f"Unsupported or missing sportId: {sport_id!r}")
        return match_cls.model_validate(data)

