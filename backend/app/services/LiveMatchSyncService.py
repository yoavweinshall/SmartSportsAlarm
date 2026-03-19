import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Set, Tuple
from ..core.matches.factory import MatchFactory
from ..core.teams.baseTeam import BaseTeam
from ..database import get_supabase
from .ScoresApiService import ScoresApiService

logger = logging.getLogger(__name__)


class LiveMatchSyncService:
    """
    Syncing data of live matches from the api to the DB
    """

    def __init__(self):
        self.api_service = ScoresApiService()

        self._api_to_internal_team_id: Dict[int, int] = {}
        self._supported_competition_ids: Dict[int, int] = {}
        self._known_team_comp_links: Set[Tuple[int, int]] = set()
        self._cache_initialized = False

    async def _ensure_cache_loaded(self):
        """
        Ensures the cache is populated. Cannot be in __init__ because it requires 'await'.
        """
        try:
            if self._cache_initialized:
                return

            comp_res = await get_supabase().table("competitions").select("id", "external_api_id").execute()
            self._supported_competition_ids = {int(rec["external_api_id"]): int(rec["id"]) for rec in comp_res.data}

            team_res = await get_supabase().table("teams").select("id, external_api_id").execute()
            self._api_to_internal_team_id = {int(rec["external_api_id"]): int(rec["id"]) for rec in team_res.data}

            link_res = await get_supabase().table("team_competitions").select("team_id, competition_id").execute()
            self._known_team_comp_links = {(int(rec["team_id"]), int(rec["competition_id"])) for rec in link_res.data}

            self._cache_initialized = True
            logger.info(
                f"Sync Cache Ready: {len(self._supported_competition_ids)} competitions, "
                f"{len(self._api_to_internal_team_id)} teams loaded.")

        except Exception as e:
            logger.error(f"Critical error during sync cache initialization: {e}")

    @staticmethod
    async def _get_db_notified_states(games_data: List[Dict[str, Any]]) -> Dict[int, bool]:
        """
        Get the status of the games that are on the DB
        :param games_data: data of the live matches we got from the API
        :return: Last notification status of the live matches
        """
        external_ids = [g.get("id") for g in games_data if g.get("id")]
        if not external_ids:
            return {}

        response = await get_supabase().table("matches") \
            .select("external_api_id, notified") \
            .in_("external_api_id", external_ids) \
            .execute()

        return {
            rec["external_api_id"]: rec.get("notified", False)
            for rec in response.data
        }

    async def _batch_sync_teams(self, games_data: List[Dict[str, Any]]):
        """
        Extracts new teams, performing batch upserts.
        """
        new_teams: Dict[int, BaseTeam] = {}
        for game in games_data:
            for side in ["homeCompetitor", "awayCompetitor"]:
                comp = game.get(side, {})
                api_id = comp.get("id")

                if api_id and api_id not in self._api_to_internal_team_id:
                    team = BaseTeam.model_validate(comp)
                    team.country_id =  None  # dealing with states inside the US is a lot of mess
                    new_teams[api_id] = team.model_dump(mode='json', exclude_none=True)

        if new_teams:
            # Return generated internal IDs for mapping
            res = await get_supabase().table("teams").upsert(
                list(new_teams.values()),
                on_conflict="external_api_id"
            ).execute()

            for rec in res.data:
                self._api_to_internal_team_id[rec["external_api_id"]] = rec["id"]

    async def _batch_sync_teams_competitions_links(self, games_data: List[Dict[str, Any]]):
        """
        Extracts new links, performing batch upserts.
        """
        links_to_add = []
        for game in games_data:
            comp_api_id = int(game.get("competitionId", 0))
            internal_competition_id = self._supported_competition_ids.get(comp_api_id)
            for side in ["homeCompetitor", "awayCompetitor"]:
                api_team_id = game.get(side, {}).get("id")
                internal_team_id = self._api_to_internal_team_id.get(api_team_id)

                if internal_team_id and (internal_team_id, internal_competition_id) not in self._known_team_comp_links:
                    links_to_add.append({
                        "team_id": internal_team_id,
                        "competition_id": internal_competition_id
                    })

        if links_to_add:
            res = await get_supabase().table("team_competitions").upsert(
                links_to_add,
                on_conflict="team_id, competition_id"
            ).execute()
            for rec in res.data:
                self._known_team_comp_links.add((rec["team_id"], rec["competition_id"]))

    def _process_single_match(self, game_data: Dict[str, Any], notified_map: Dict[int, bool]) -> Dict[str, Any] | None:
        """
        Process the state of 1 game
        :param game_data: data of the live match we got from the API
        :param notified_map: map of the previous notified status of the games
        :return: updated game data
        """
        try:
            match = MatchFactory.get_match_instance(game_data)
            ext_id = match.external_api_id

            current_climax = match.is_climax()
            previously_notified = notified_map.get(ext_id, False)

            if current_climax and not previously_notified:
                self._handle_new_climax(match)

            match.updated_at = datetime.now(timezone.utc)
            match.home_team_id = self._api_to_internal_team_id.get(match.home_team_id)
            match.away_team_id = self._api_to_internal_team_id.get(match.away_team_id)
            match.competition_id = self._api_to_internal_team_id.get(match.competition_id)
            match.notified = current_climax
            match_payload = match.model_dump(mode='json', exclude_none=True)

            return match_payload

        except ValueError as e:
            return logger.error(f"Invalid match data: {game_data}: {e}")
        except Exception as e:
            logger.error(f"Failed to process game {game_data.get('id')}: {e}")
            return None

    async def sync_live_matches(self) -> None:
        """
        Update the status of the live matches
        """
        await self._ensure_cache_loaded()

        try:
            games_data = await self.api_service.fetch_live_scores()

            supported_games = [
                g for g in games_data
                if int(g.get("competitionId", 0)) in self._supported_competition_ids
            ]

            if not supported_games:
                logger.info("No live scores found")
                return

            # Batch sync teams and their competition links
            await self._batch_sync_teams(supported_games)
            await self._batch_sync_teams_competitions_links(supported_games)

            # Optimization: use only supported games for notified states
            notified_map = await self._get_db_notified_states(supported_games)


            processed_games = [self._process_single_match(game, notified_map) for game in supported_games]
            await get_supabase().table("matches").upsert(
                processed_games,
                on_conflict="external_api_id"
            ).execute()

        except Exception as e:
            logger.error(f"Sync service error: {e}")

    def _handle_new_climax(self, match):
        # TODO send alarm to user
        logger.info(f"New climax detected: {match.external_api_id}")