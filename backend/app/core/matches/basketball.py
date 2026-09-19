from .timeBasedMatches import TimeBasedMatches
from .utils.stages import HalfGameStage, QuarterGameStage, BaseStage


class BasketballMatch(TimeBasedMatches):

    @property
    def _stage_time(self) -> int:
        return 600

    @property
    def _climax_max_score_diff(self) -> int:
        return 8

    @property
    def _climax_max_time_seconds(self) -> int:
        return 10 * 60

    @property
    def stage(self) -> QuarterGameStage:
        return QuarterGameStage(self.match_stage)


class NCAABasketBallMatch(BasketballMatch):

    @property
    def stage(self) -> HalfGameStage:
        return HalfGameStage(self.match_stage)
