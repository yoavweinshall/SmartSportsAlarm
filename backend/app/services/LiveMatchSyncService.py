import logging
from typing import Any

from .CacheService import CacheService
from .MatchProcessService import MatchProcessService
from ..core.matches import BaseMatch
from ..database import get_supabase
from .ScoresApiService import ScoresApiService

logger = logging.getLogger(__name__)


class LiveMatchSyncService:
    """
    Syncing data of live matches from the api to the DB
    """

    @staticmethod
    async def _get_db_notified_states(games_data: list[BaseMatch]) -> dict[int, bool]:
        """
        Get the status of the games that are on the DB
        :param games_data: data of the live matches we got from the API
        :return: Last notification status of the live matches
        """
        external_ids = [g.external_api_id for g in games_data if g.external_api_id]
        if not external_ids:
            return {}

        response = (
            await get_supabase()
            .table("matches")
            .select("external_api_id, notified")
            .in_("external_api_id", external_ids)
            .execute()
        )

        return {rec["external_api_id"]: rec.get("notified", False) for rec in response.data}

    @classmethod
    def _process_single_match(cls, match: BaseMatch, notified_map: dict[int, bool]) -> dict[str, Any] | None:
        """
        Process the state of 1 game
        :param match: data of the live match we got from the API
        :param notified_map: map of the previous notified status of the games
        :return: updated game data
        """
        match = MatchProcessService.process_single_match(match)

        ext_id = match.external_api_id
        current_climax = match.is_climax()
        previously_notified = notified_map.get(ext_id, False)

        if current_climax and not previously_notified:
            cls._handle_new_climax(match)

        match.notified = current_climax
        match_payload = match.model_dump(mode="json", exclude_none=True)

        return match_payload

    @classmethod
    async def sync_live_matches(cls) -> None:
        """
        Update the status of the live matches
        """
        await CacheService.get_instance().ensure_cache_loaded()
        try:
            supported_games = await ScoresApiService.fetch_matches(
                onlyLiveGames=True,
                competitions=",".join(
                    [
                        str(competition_id)
                        for competition_id in CacheService.get_instance().supported_competition_ids.keys()
                    ]
                ),
            )

            if not supported_games:
                logger.info("No live scores found")
                return

            # Optimization: use only supported games for notified states
            notified_map = await cls._get_db_notified_states(supported_games)

            processed_games = [cls._process_single_match(game, notified_map) for game in supported_games]
            await get_supabase().table("matches").upsert(processed_games, on_conflict="external_api_id").execute()

        except Exception as e:
            logger.error(f"Sync service error: {e}")

    @classmethod
    def _handle_new_climax(cls, match):
        # TODO send alarm to user
        logger.info(f"New climax detected: {match.external_api_id}")
