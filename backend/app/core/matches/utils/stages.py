"""
Util module to handle game stages
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum


class CommonMatchStage(str, Enum):
    SCHEDULED = "Scheduled"
    DELAYED = "Delayed"
    POSTPONED = "Postponed"
    CANCELLED = "Cancelled"
    FINISHED = "Finished"
    UNKNOWN = "Unknown"


UNPLAYED_STAGES = [
    CommonMatchStage.SCHEDULED.value,
    CommonMatchStage.DELAYED.value,
    CommonMatchStage.POSTPONED.value,
    CommonMatchStage.CANCELLED.value,
    CommonMatchStage.UNKNOWN.value,
]


class BaseStage(ABC):
    """
    Abstract base class for stages of the game
    """

    @abstractmethod
    def is_climax_period(self) -> bool:
        """
        return if this stage is final period of the game
        """

    @abstractmethod
    def stages_to_go(self) -> int:
        """
        return how many stages to go after this one
        """

    @property
    @abstractmethod
    def value(self) -> str: ...


class QuarterGameStage(str, Enum, BaseStage):
    # Common stages (must match CommonMatchStage member names)
    SCHEDULED = "Scheduled"
    DELAYED = "Delayed"
    POSTPONED = "Postponed"
    CANCELLED = "Cancelled"
    FINISHED = "Finished"

    # Quarter-based game stages (basketball, american football, etc.)
    Q1 = "Q1"
    Q2 = "Q2"
    HALFTIME = "Halftime"
    Q3 = "Q3"
    Q4 = "Q4"
    OVERTIME = "OT"  # canonical value; OT1/OT2/... normalize here

    UNKNOWN = "Unknown"

    def is_climax_period(self) -> bool:
        return self in {QuarterGameStage.Q4, QuarterGameStage.OVERTIME}

    def stages_to_go(self) -> int:
        return {
            QuarterGameStage.Q1: 3,
            QuarterGameStage.Q2: 2,
            QuarterGameStage.HALFTIME: 2,
            QuarterGameStage.Q3: 1,
            QuarterGameStage.Q4: 0,
        }[self]


class HalfGameStage(str, Enum, BaseStage):
    # Common stages (must match CommonMatchStage member names)
    SCHEDULED = "Scheduled"
    DELAYED = "Delayed"
    POSTPONED = "Postponed"
    CANCELLED = "Cancelled"
    FINISHED = "Finished"

    # Half-based game stages (NCAA basketball, some competitions)
    FIRST_HALF = "1st Half"
    HALF_TIME = "Halftime"
    SECOND_HALF = "2nd Half"
    OVERTIME = "OT"  # canonical value; OT1/OT2/... normalize here

    UNKNOWN = "Unknown"

    def is_climax_period(self) -> bool:
        return self in [HalfGameStage.OVERTIME, HalfGameStage.SECOND_HALF]

    def stages_to_go(self) -> int:
        return {
            HalfGameStage.FIRST_HALF: 1,
            HalfGameStage.HALF_TIME: 0,
            HalfGameStage.SECOND_HALF: 0,
        }[self]
