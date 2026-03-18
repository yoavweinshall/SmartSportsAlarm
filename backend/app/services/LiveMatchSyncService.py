import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from ..core.matches.factory import MatchFactory
from ..database import supabase
from . import ScoresApiService

logger = logging.getLogger(__name__)


class LiveMatchSyncService:
    """
    Syncing data of live matches from the api to the DB
    """
    def __init__(self):
        self.api_service = ScoresApiService()

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

        response = await supabase.table("matches") \
            .select("external_api_id, notified") \
            .in_("external_api_id", external_ids) \
            .execute()

        return {
            rec["external_api_id"]: rec.get("notified", False)
            for rec in response.data
        }

    async def _sync_single_match(self, game_data: Dict[str, Any], notified_map: Dict[int, bool]) -> None:
        """
        Update a single game in the DB
        :param game_data: data of the live match we got from the API
        :param notified_map: map of the previous notified status of the games
        """
        try:
            match = MatchFactory.get_match_instance(game_data)
            ext_id = match.external_api_id

            current_climax = match.is_climax()
            previously_notified = notified_map.get(ext_id, False)

            # Trigger alert only on status transition (False -> True)
            if current_climax and not previously_notified:
                self._handle_new_climax(match)

            # Prepare data for DB update
            match.updated_at = datetime.now(timezone.utc)
            match_payload = match.model_dump(exclude_none=True)
            match_payload["notified"] = current_climax

            await supabase.table("matches").upsert(
                match_payload,
                on_conflict="external_api_id"
            ).execute()

        except ValueError:
            # Silently skip unsupported sports
            pass
        except Exception as e:
            logger.error(f"Failed to process game {game_data.get('id')}: {e}")

    async def sync_live_matches(self) -> None:
        """
        Update the status of the live matches
        """
        try:
            # fetch all current live scores
            games_data = await self.api_service.fetch_live_scores()
            if not games_data:
                logger.info("No live scores found")
                return

            # Fetch existing climax states to prevent duplicate alerts
            notified_map = await self._get_db_notified_states(games_data)

            for game in games_data:
                await self._sync_single_match(game, notified_map)

        except Exception as e:
            logger.error(f"Sync service error: {e}")

    def _handle_new_climax(self, match):
        #TODO send alarm to user
        logger.info(f"New climax detected: {match.external_api_id}")