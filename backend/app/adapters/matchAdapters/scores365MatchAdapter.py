from datetime import datetime
from typing import Any

from pydantic import AliasPath, BaseModel, ConfigDict, Field, field_validator

from ..matchAdapters import BaseMatchAdapter
from ..teamAdapters import Scores365TeamAdapter
from ..stageAdapters import Scores365StageAdapter
from ...core.matches import BaseMatch, MatchFactory


class Scores365MatchAdapter(BaseModel, BaseMatchAdapter):

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = Field(default=None, exclude=True)
    sport_id: int | None = Field(default=None, validation_alias="sportId")
    external_api_id: int = Field(validation_alias="id")
    competition_id: int | None = Field(default=None, validation_alias="competitionId")
    home_team_id: int | None = Field(default=None, validation_alias=AliasPath("homeCompetitor", "id"))
    away_team_id: int | None = Field(default=None, validation_alias=AliasPath("awayCompetitor", "id"))

    home_team: Scores365TeamAdapter | None = Field(default=None, validation_alias="homeCompetitor")
    away_team: Scores365TeamAdapter | None = Field(default=None, validation_alias="awayCompetitor")

    start_time: datetime = Field(validation_alias="startTime")
    status_group: int = Field(validation_alias="statusGroup")
    status_text: str | None = Field(default=None, validation_alias="statusText")
    # 365scores provides a numeric `gameTime` and a string `gameTimeDisplay` (e.g. "02:25").
    game_time: str | None = Field(default=None, validation_alias="gameTimeDisplay")

    home_score: int = Field(default=0, validation_alias=AliasPath("homeCompetitor", "score"))
    away_score: int = Field(default=0, validation_alias=AliasPath("awayCompetitor", "score"))
    notified: bool = Field(default=False)

    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata")
    updated_at: datetime | None = None
    created_at: datetime | None = None

    @classmethod
    @field_validator("home_score", "away_score", mode="before")
    def _score_minus_one_to_zero(cls, v: Any) -> Any:
        # 365scores sometimes uses -1 / -1.0 when the score is unknown.
        if v is None:
            return 0
        if v == -1 or v == -1.0:
            return 0
        return v

    def to_internal_match(self) -> BaseMatch:
        self.status_text = Scores365StageAdapter.normalize(self.status_text, self.sport_id).value
        return MatchFactory.get_match_instance(self.model_dump(mode='json', exclude_none=True))