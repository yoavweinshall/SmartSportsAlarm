from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .baseTeamAdapter import BaseTeamAdapter
from ...core.teams import BaseTeam


class Scores365TeamAdapter(BaseModel, BaseTeamAdapter):

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int | None = None
    # external_api_id corresponds to the 'id' field in the 365scores JSON
    external_api_id: int = Field(validation_alias="id")

    sport_id: int | None = Field(default=None, validation_alias="sportId")
    country_id: int | None = Field(default=None, validation_alias="countryId")

    name: str = Field(validation_alias="name")
    short_name: str | None = Field(default=None, validation_alias="shortName")
    symbolic_name: str | None = Field(default=None, validation_alias="symbolicName")
    name_for_url: str | None = Field(default=None, validation_alias="nameForURL")

    # 365scores provides team color in the 'color' field
    primary_color: str | None = Field(default=None, validation_alias="color")
    secondary_color: str | None = Field(default=None)

    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata")
    created_at: datetime | None = None

    def _to_internal_team(self) -> BaseTeam:
        return BaseTeam.model_validate(self.model_dump(mode="json", exclude_none=True))
