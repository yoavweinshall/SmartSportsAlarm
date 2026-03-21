from enum import Enum
from typing import TypeVar, Union, Dict

from collections.abc import Callable

from .baseStageAdapter import BaseStageAdapter
from ...core.matches.utils.stages import HalfGameStage, QuarterGameStage, CommonMatchStage


class Scores365StageAdapter(BaseStageAdapter):

    _FINISHED_STRINGS = {
        "final",
        "finished",
        "ended",
        "game over",
        "full time",
        "ft",
        "just ended"
    }

    _COMMON_EXACT: dict[str, CommonMatchStage] = {
        CommonMatchStage.SCHEDULED.value: CommonMatchStage.SCHEDULED,
        CommonMatchStage.DELAYED.value: CommonMatchStage.DELAYED,
        CommonMatchStage.POSTPONED.value: CommonMatchStage.POSTPONED,
        CommonMatchStage.CANCELLED.value: CommonMatchStage.CANCELLED,
    }

    TStage = TypeVar("TStage", bound=Enum)

    @classmethod
    def __map_common_stage_to_enum(cls, enum_cls: type[TStage], common: CommonMatchStage) -> TStage | None:
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

    @classmethod
    def __normalize_common_stage(cls, status_text: str | None) -> CommonMatchStage:
        if not status_text:
            return CommonMatchStage.UNKNOWN

        s = status_text.strip()
        exact = cls._COMMON_EXACT.get(s)
        if exact is not None:
            return exact

        if s.strip().lower() in cls._FINISHED_STRINGS:
            return CommonMatchStage.FINISHED

        return CommonMatchStage.UNKNOWN

    @staticmethod
    def __normalize_overtime(value: str | None) -> bool:
        if not value:
            return False
        s = value.strip()
        return s == "Overtime" or s.startswith("OT")

    @classmethod
    def __enum_from_value(cls, enum_cls: type[TStage], value: str | None) -> TStage | None:
        if not value:
            return None
        return enum_cls._value2member_map_.get(value.strip())  # type: ignore[attr-defined]

    @classmethod
    def to_internal_half_stage(cls, status_text: str) -> HalfGameStage:
        common_mapped = cls.__map_common_stage_to_enum(HalfGameStage, cls.__normalize_common_stage(status_text))
        if common_mapped is not None:
            return common_mapped

        if cls.__normalize_overtime(status_text):
            return HalfGameStage.OVERTIME

        direct = cls.__enum_from_value(HalfGameStage, status_text)
        if direct is not None:
            return direct
        return HalfGameStage.UNKNOWN

    @classmethod
    def to_internal_quarter_stage(cls, status_text: str) -> QuarterGameStage:
        common_mapped = cls.__map_common_stage_to_enum(QuarterGameStage, cls.__normalize_common_stage(status_text))
        if common_mapped is not None:
            return common_mapped

        if cls.__normalize_overtime(status_text):
            return QuarterGameStage.OVERTIME

        direct = cls.__enum_from_value(QuarterGameStage, status_text)
        if direct is not None:
            return direct
        return QuarterGameStage.UNKNOWN
