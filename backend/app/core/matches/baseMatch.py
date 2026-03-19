from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import AliasPath, BaseModel, ConfigDict, Field, field_validator


class BaseMatch(BaseModel, ABC):
    """
    Base match model.

    Field names match `public.matches` table columns (schema.sql).
    Validation aliases map 365scores JSON into these columns.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    external_api_id: int = Field(validation_alias="id")
    competition_id: int | None = Field(default=None, validation_alias="competitionId")
    home_team_id: int | None = Field(default=None, validation_alias=AliasPath("homeCompetitor", "id"))
    away_team_id: int | None = Field(default=None, validation_alias=AliasPath("awayCompetitor", "id"))

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

    @field_validator("home_score", "away_score", mode="before")
    @classmethod
    def _score_minus_one_to_zero(cls, v: Any) -> Any:
        # 365scores sometimes uses -1 / -1.0 when score is unknown.
        if v is None:
            return 0
        if v == -1 or v == -1.0:
            return 0
        return v

    @abstractmethod
    def is_climax(self) -> bool: ...

