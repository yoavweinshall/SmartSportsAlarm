from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.core.matches.utils.stages import BaseStage
from backend.app.core.teams import BaseTeam


class BaseMatch(BaseModel, ABC):
    """
    Base match model.

    Field names match `public.matches` table columns (schema.sql).
    Validation aliases map 365scores JSON into these columns.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = Field(default=None, exclude=True)
    external_api_id: int = Field(validation_alias="external_api_id")
    competition_id: int | None = Field(default=None, validation_alias="competition_id")
    home_team_id: int | None = Field(default=None, validation_alias="home_team_id")
    away_team_id: int | None = Field(default=None, validation_alias="away_team_id")

    home_team: BaseTeam = Field(None, alias="home_team", exclude=True)
    away_team: BaseTeam = Field(None, alias="away_team", exclude=True)

    start_time: datetime = Field(validation_alias="start_time")
    stage_group: int = Field(validation_alias="stage_group")
    match_stage: str | None = Field(default=None, validation_alias="match_stage")
    # 365scores provides a numeric `gameTime` and a string `gameTimeDisplay` (e.g. "02:25").
    game_time: str | None = Field(default=None, validation_alias="game_time")

    home_score: int = Field(default=0, validation_alias="home_score")
    away_score: int = Field(default=0, validation_alias="away_score")
    notified: bool = Field(default=False)

    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata")
    updated_at: datetime | None = None
    created_at: datetime | None = None

    @property
    @abstractmethod
    def _stage_time(self): ...

    @property
    @abstractmethod
    def _climax_max_score_diff(self) -> int: ...

    @property
    @abstractmethod
    def _climax_max_time_seconds(self) -> int: ...

    @property
    @abstractmethod
    def stage(self) -> BaseStage: ...

    @abstractmethod
    def is_climax(self) -> bool: ...

    def _is_climax_time(self) -> bool:
        return self.stage.is_climax_period()

    def is_future_match(self) -> bool:
        return self.stage_group == 2
