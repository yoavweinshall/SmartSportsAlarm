from enum import Enum
from typing import ClassVar

from .baseMatch import BaseMatch
from .utils.stages import HalfGameStage, QuarterGameStage
from .utils.time_handle import parse_mmss_to_seconds


class BasketballMatch(BaseMatch):
    STAGE_ADDITIONAL_GAME_TIME: ClassVar[dict[Enum, int]] = {
        QuarterGameStage.Q1: 1800,
        QuarterGameStage.Q2: 1200,
        QuarterGameStage.HALFTIME: 1200,
        QuarterGameStage.Q3: 600,
        QuarterGameStage.Q4: 0,
        QuarterGameStage.OVERTIME: 0,
    }
    CLIMAX_MAX_SCORE_DIFF: ClassVar[int] = 8
    CLIMAX_MAX_TIME_SECONDS: ClassVar[int] = 10 * 60

    @property
    def stage(self) -> QuarterGameStage:
        return QuarterGameStage(self.match_stage)

    def _is_final_period(self) -> bool:
        return self.stage in {QuarterGameStage.Q4, QuarterGameStage.OVERTIME}

    def remaining_time_seconds(self) -> int | None:
        """
        Remaining time on the game clock for any stage that exposes a clock string.

        - Returns `None` for non-clock stages (Scheduled/Delayed/Postponed/Cancelled).
        - Returns `0` for FINISHED.
        - Otherwise parses `mm:ss` from `game_time` (mapped from 365scores `gameTimeDisplay`).
        """

        if self.stage in {
            QuarterGameStage.SCHEDULED,
            QuarterGameStage.DELAYED,
            QuarterGameStage.POSTPONED,
            QuarterGameStage.CANCELLED,
        }:
            return None
        if self.stage == QuarterGameStage.FINISHED:
            return 0
        return parse_mmss_to_seconds(self.game_time) + self.STAGE_ADDITIONAL_GAME_TIME[self.stage]

    def is_climax(self) -> bool:
        seconds = self.remaining_time_seconds()
        if seconds is None:
            return False
        return (
            seconds < self.CLIMAX_MAX_TIME_SECONDS
            and abs(self.home_score - self.away_score) <= self.CLIMAX_MAX_SCORE_DIFF
        )


class NCAABasketBallMatch(BasketballMatch):

    STAGE_ADDITIONAL_GAME_TIME: ClassVar[dict[HalfGameStage, int]] = {
        HalfGameStage.FIRST_HALF: 1200,
        HalfGameStage.HALF_TIME: 1200,
        HalfGameStage.SECOND_HALF: 0,
        HalfGameStage.OVERTIME: 0,
    }

    @property
    def stage(self) -> HalfGameStage:
        return HalfGameStage(self.match_stage)

    def _is_final_period(self) -> bool:
        return self.stage in {HalfGameStage.SECOND_HALF, HalfGameStage.OVERTIME}
