from __future__ import annotations

from enum import Enum


class CommonMatchStage(str, Enum):
    SCHEDULED = "Scheduled"
    DELAYED = "Delayed"
    POSTPONED = "Postponed"
    CANCELLED = "Cancelled"
    FINISHED = "Finished"
    UNKNOWN = "Unknown"


class QuarterGameStage(str, Enum):
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


class HalfGameStage(str, Enum):
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
