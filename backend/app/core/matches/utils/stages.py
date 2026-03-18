from __future__ import annotations

from enum import Enum
from typing import TypeVar


class StageEnum(str, Enum):
    """
    Base enum with shared normalization helpers.
    Subclasses should implement `from_status_text`.
    """

    @classmethod
    def from_status_text(cls, status_text: str | None):  # pragma: no cover
        raise NotImplementedError


class CommonMatchStage(str, Enum):
    SCHEDULED = "Scheduled"
    DELAYED = "Delayed"
    POSTPONED = "Postponed"
    CANCELLED = "Cancelled"
    FINISHED = "Finished"
    UNKNOWN = "Unknown"


_FINISHED_STRINGS = {
    "final",
    "finished",
    "ended",
    "game over",
    "full time",
    "ft",
}

_COMMON_EXACT: dict[str, CommonMatchStage] = {
    CommonMatchStage.SCHEDULED.value: CommonMatchStage.SCHEDULED,
    CommonMatchStage.DELAYED.value: CommonMatchStage.DELAYED,
    CommonMatchStage.POSTPONED.value: CommonMatchStage.POSTPONED,
    CommonMatchStage.CANCELLED.value: CommonMatchStage.CANCELLED,
}


def normalize_common_stage(status_text: str | None) -> CommonMatchStage:
    if not status_text:
        return CommonMatchStage.UNKNOWN

    s = status_text.strip()
    exact = _COMMON_EXACT.get(s)
    if exact is not None:
        return exact

    if s.strip().lower() in _FINISHED_STRINGS:
        return CommonMatchStage.FINISHED

    return CommonMatchStage.UNKNOWN


TStage = TypeVar("TStage", bound=Enum)


def map_common_stage_to_enum(enum_cls: type[TStage], common: CommonMatchStage) -> TStage | None:
    """
    Map a CommonMatchStage to a sport-specific Enum by *name* (SCHEDULED/DELAYED/...).
    Returns None if common is UNKNOWN or enum_cls doesn't have the member.
    """

    if common == CommonMatchStage.UNKNOWN:
        return None
    try:
        return enum_cls[common.name]
    except KeyError:
        return None


def _enum_from_value(enum_cls: type[TStage], value: str | None) -> TStage | None:
    if not value:
        return None
    return enum_cls._value2member_map_.get(value.strip())  # type: ignore[attr-defined]


def _normalize_overtime(value: str | None) -> bool:
    if not value:
        return False
    s = value.strip()
    return s == "Overtime" or s.startswith("OT")


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
    HALF_TIME = "Half Time"
    SECOND_HALF = "2nd Half"
    OVERTIME = "OT"  # canonical value; OT1/OT2/... normalize here

    UNKNOWN = "Unknown"


def normalize_quarter_game_stage(status_text: str | None) -> QuarterGameStage:
    common_mapped = map_common_stage_to_enum(QuarterGameStage, normalize_common_stage(status_text))
    if common_mapped is not None:
        return common_mapped

    if _normalize_overtime(status_text):
        return QuarterGameStage.OVERTIME

    direct = _enum_from_value(QuarterGameStage, status_text)
    if direct is not None:
        return direct
    return QuarterGameStage.UNKNOWN


def normalize_half_game_stage(status_text: str | None) -> HalfGameStage:
    common_mapped = map_common_stage_to_enum(HalfGameStage, normalize_common_stage(status_text))
    if common_mapped is not None:
        return common_mapped

    if _normalize_overtime(status_text):
        return HalfGameStage.OVERTIME

    direct = _enum_from_value(HalfGameStage, status_text)
    if direct is not None:
        return direct
    return HalfGameStage.UNKNOWN

