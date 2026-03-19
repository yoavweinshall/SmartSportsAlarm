from __future__ import annotations

from enum import Enum
from typing import ClassVar, Dict

from pydantic import model_validator

from .base import BaseMatch
from .utils.stages import HalfGameStage, QuarterGameStage, normalize_half_game_stage, normalize_quarter_game_stage
from .utils.time_handle import parse_mmss_to_seconds


class BasketballMatch(BaseMatch):
    STAGE_ADDITIONAL_GAME_TIME: ClassVar[Dict[Enum, int]] = {QuarterGameStage.Q1: 1800,
                                                                         QuarterGameStage.Q2: 1200,
                                                                         QuarterGameStage.Q3: 600,
                                                                         QuarterGameStage.Q4: 0,
                                                                         QuarterGameStage.OVERTIME: 0
                                                                         }
    CLIMAX_MAX_SCORE_DIFF: ClassVar[int] = 8
    CLIMAX_MAX_TIME_SECONDS: ClassVar[int] = 10 * 60

    @model_validator(mode="after")
    def _validate_stage(self):
        stage = normalize_quarter_game_stage(self.status_text)
        # If we have a status_text, force it to be representable as a quarter-based stage.
        if self.status_text and stage == QuarterGameStage.UNKNOWN:
            raise ValueError(f"Unrecognized quarter-based statusText for BasketballMatch: {self.status_text!r}")
        return self

    def stage(self) -> QuarterGameStage:
        return normalize_quarter_game_stage(self.status_text)

    def _is_final_period(self) -> bool:
        stage = self.stage()
        return stage in {QuarterGameStage.Q4, QuarterGameStage.OVERTIME}

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
        return parse_mmss_to_seconds(self.game_time) + self.STAGE_ADDITIONAL_GAME_TIME[self.status_text]

    def is_climax(self) -> bool:
        seconds = self.remaining_time_seconds()
        if seconds is None:
            return False
        return seconds < self.CLIMAX_MAX_TIME_SECONDS and abs(self.home_score - self.away_score) <= self.CLIMAX_MAX_SCORE_DIFF


class NCAABasketBallMatch(BasketballMatch):

    STAGE_ADDITIONAL_GAME_TIME: ClassVar[Dict[HalfGameStage, int]] = {HalfGameStage.FIRST_HALF: 1200,
                                                                      HalfGameStage.HALF_TIME: 1200,
                                                                      HalfGameStage.SECOND_HALF: 0
                                                                      }

    @model_validator(mode="after")
    def _validate_stage(self):
        stage = normalize_half_game_stage(self.status_text)
        if self.status_text and stage == HalfGameStage.UNKNOWN:
            raise ValueError(f"Unrecognized half-based statusText for NCAABasketBallMatch: {self.status_text!r}")
        return self

    def stage(self) -> HalfGameStage:
        return normalize_half_game_stage(self.status_text)

    def _is_final_period(self) -> bool:
        stage = self.stage()
        return stage in {HalfGameStage.SECOND_HALF, HalfGameStage.OVERTIME}

