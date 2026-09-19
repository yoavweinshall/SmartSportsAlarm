from typing import ClassVar

from backend.app.core.matches.timeBasedMatches import TimeBasedMatches
from backend.app.core.matches.utils.stages import QuarterGameStage


class FootballMatch(TimeBasedMatches):

    CLIMAX_MAX_SCORE_DIFF: ClassVar[int] = 10
    CLIMAX_MAX_TIME_SECONDS: ClassVar[int] = 10 * 60

    @property
    def stage(self) -> QuarterGameStage:
        return QuarterGameStage(self.match_stage)
