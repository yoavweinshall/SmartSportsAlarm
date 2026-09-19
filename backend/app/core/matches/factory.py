from __future__ import annotations

from .baseMatch import BaseMatch
from .basketball import BasketballMatch, NCAABasketBallMatch
from .football import FootballMatch


class MatchFactory:
    """
    Creates the appropriate match model based on 365scores `sportId`.
    """

    NCAA_COMPETITION_IDS = {7630, 109}

    @classmethod
    def get_match_instance(cls, data: dict) -> BaseMatch:
        sport_id = int(data.get("sport_id"))
        competition_id = int(data.get("competition_id"))

        if sport_id == 2:  # NCAA Basketball games are built from halves and not quarters
            if competition_id in cls.NCAA_COMPETITION_IDS:
                return NCAABasketBallMatch.model_validate(data)
            else:
                return BasketballMatch.model_validate(data)
        if sport_id == 3:
            return FootballMatch.model_validate(data)

        raise ValueError(f"Unsupported or missing sportId: {sport_id!r}")
