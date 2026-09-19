from backend.app.core.matches.timeBasedMatches import TimeBasedMatches
from backend.app.core.matches.utils.stages import QuarterGameStage


class FootballMatch(TimeBasedMatches):

    @property
    def stage(self) -> QuarterGameStage:
        return QuarterGameStage(self.match_stage)

    @property
    def _stage_time(self) -> int:
        return 900

    @property
    def _climax_max_score_diff(self) -> int:
        return 8

    @property
    def _climax_max_time_seconds(self) -> int:
        return 10 * 60