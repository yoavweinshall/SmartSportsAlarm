from abc import abstractmethod
from typing import Dict, Callable, Union

from backend.app.core.matches.utils.stages import QuarterGameStage, HalfGameStage, CommonMatchStage


class BaseStageAdapter:

    @classmethod
    @abstractmethod
    def to_internal_quarter_stage(cls, stage: str) -> QuarterGameStage: ...

    @classmethod
    @abstractmethod
    def to_internal_half_stage(cls, stage: str) -> HalfGameStage: ...

    @classmethod
    def _normalize_basketball_stage(cls, status: str) -> Union[CommonMatchStage, HalfGameStage, QuarterGameStage]:
        quarter_normalization = cls.to_internal_quarter_stage(status)
        if quarter_normalization is not QuarterGameStage.UNKNOWN:
            return quarter_normalization
        halves_normalization = cls.to_internal_half_stage(status)
        if halves_normalization is not HalfGameStage.UNKNOWN:
            return halves_normalization
        return CommonMatchStage.UNKNOWN

    @classmethod
    def normalize(cls, status: str, sport_id: int):
        id_to_normalize_func: Dict[int, Callable] = {
            2: cls._normalize_basketball_stage,
        }
        return id_to_normalize_func[sport_id](status)
