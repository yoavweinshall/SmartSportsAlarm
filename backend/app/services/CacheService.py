import asyncio
import logging

from .DbApiMapService import DbApiMapService
from ..core.matches import BaseMatch
from ..core.teams import BaseTeam
from ..database import get_supabase

logger = logging.getLogger(__name__)


class CacheService:

    _instance = None
    _initialized = False

    @classmethod
    def get_instance(cls):
        """
        Returns the singleton instance of the MappingCacheService.
        Creates it if it doesn't exist yet.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.api_to_internal_team_id: dict[int, int] = {}
            self.supported_competition_ids: dict[int, int] = {}
            self.known_team_comp_links: set[tuple[int, int]] = set()
            self._is_loaded = False
            CacheService._initialized = True

    async def ensure_cache_loaded(self):
        """
        Ensures the cache is populated. Cannot be in __init__ because it requires 'await'.
        """
        try:
            if self._is_loaded:
                return

            self.supported_competition_ids, self.api_to_internal_team_id, self.known_team_comp_links = (
                await asyncio.gather(
                    DbApiMapService.get_competition_mapping(),
                    DbApiMapService.get_team_mapping(),
                    DbApiMapService.get_team_competitions_pairing(),
                )
            )

            self._is_loaded = True
            logger.info(
                f"Sync Cache Ready: {len(self.supported_competition_ids)} competitions, "
                f"{len(self.api_to_internal_team_id)} teams loaded."
            )

        except Exception as e:
            logger.error(f"Critical error during sync cache initialization: {e}")

    async def refresh_cache(self) -> None:
        """
        Forces a cache reload. Useful to call once a day before the
        future matches sync starts, to pick up any new teams or competitions.
        """
        logger.info("Force refreshing Mapping Cache...")
        self._is_loaded = False
        await self.ensure_cache_loaded()

    async def batch_sync_teams(self, games_data: list[BaseMatch]):
        """
        Extracts new teams, performing batch upserts.
        """
        new_teams: dict[int, BaseTeam] = {}
        for game in games_data:
            for side in [game.home_team, game.away_team]:
                if side is None:
                    continue
                api_id = side.external_api_id

                if api_id and api_id not in self.api_to_internal_team_id:
                    side.country_id = None  # dealing with states inside the US is a lot of mess
                    new_teams[api_id] = side.model_dump(mode="json", exclude_none=True)

        if new_teams:
            # Return generated internal IDs for mapping
            res = (
                await get_supabase()
                .table("teams")
                .upsert(list(new_teams.values()), on_conflict="external_api_id")
                .execute()
            )

            for rec in res.data:
                self.api_to_internal_team_id[int(rec["external_api_id"])] = int(rec["id"])

    async def batch_sync_teams_competitions_links(self, games_data: list[BaseMatch]):
        """
        Extracts new links, performing batch upserts.
        """
        links_to_add = []
        for game in games_data:
            comp_api_id = game.competition_id
            internal_competition_id = self.supported_competition_ids.get(comp_api_id)
            for side in [game.home_team, game.away_team]:
                if side is None:
                    continue
                api_team_id = side.external_api_id
                internal_team_id = self.api_to_internal_team_id.get(api_team_id)

                if internal_team_id and (internal_team_id, internal_competition_id) not in self.known_team_comp_links:
                    links_to_add.append({"team_id": internal_team_id, "competition_id": internal_competition_id})

        if links_to_add:
            res = (
                await get_supabase()
                .table("team_competitions")
                .upsert(links_to_add, on_conflict="team_id, competition_id")
                .execute()
            )
            for rec in res.data:
                self.known_team_comp_links.add((rec["team_id"], rec["competition_id"]))
