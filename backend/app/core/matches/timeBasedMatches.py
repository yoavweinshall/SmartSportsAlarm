from abc import ABC

from backend.app.core.matches import BaseMatch
from backend.app.core.matches.utils.stages import UNPLAYED_STAGES, CommonMatchStage
from backend.app.core.matches.utils.time_handle import parse_mmss_to_seconds


class TimeBasedMatches(BaseMatch, ABC):

    def remaining_time_seconds(self) -> int | None:
        """
        Remaining time on the game clock for any stage that exposes a clock string.

        - Returns `None` for non-clock stages (Scheduled/Delayed/Postponed/Canceled).
        - Returns `0` for FINISHED.
        - Otherwise parses `mm:ss` from `game_time` (mapped from 365scores `gameTimeDisplay`).
        """

        if self.stage.value in UNPLAYED_STAGES:
            return None
        if self.stage.value == CommonMatchStage.FINISHED.value:
            return 0
        return parse_mmss_to_seconds(self.game_time) + self._stage_time * self.stage.stages_to_go()

    def is_climax(self) -> bool:
        seconds = self.remaining_time_seconds()
        if seconds is None:
            return False
        return (
            seconds < self._climax_max_time_seconds
            and abs(self.home_score - self.away_score) <= self._climax_max_score_diff
        )
