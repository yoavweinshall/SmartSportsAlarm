from abc import abstractmethod

from backend.app.core.teams import BaseTeam


class BaseTeamAdapter:

    @abstractmethod
    def _to_internal_team(self) -> BaseTeam:
        ...