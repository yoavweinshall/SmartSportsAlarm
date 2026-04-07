import logging
from datetime import datetime, timedelta
from typing import Any

from .MatchProcessService import MatchProcessService
from ..core.matches import BaseMatch
from ..database import get_supabase
from .ScoresApiService import ScoresApiService
from .CacheService import CacheService

logger = logging.getLogger(__name__)


class DbMatchesService:

    @staticmethod
    async def add_future_matches_to_db():
        """
        Get all the future matches from the API and insert them into the database.
        """
        await CacheService.get_instance().ensure_cache_loaded()
        start_date = datetime.today()
        end_date = start_date + timedelta(days=30)
        supported_competitions_id = [
            str(competition_id)
            for competition_id in CacheService.get_instance().supported_competition_ids.keys()
        ]
        future_matches = await ScoresApiService.fetch_matches(
            startDate=f"{str(start_date.day).rjust(2,'0')}/{str(start_date.month).rjust(2,'0')}/{start_date.year}",
            endDate=f"{str(end_date.day).rjust(2,'0')}/{str(end_date.month).rjust(2,'0')}/{end_date.year}",
            competitions=",".join(supported_competitions_id),
        )

        # Batch sync teams and their competition links
        await CacheService.get_instance().batch_sync_teams(future_matches)
        await CacheService.get_instance().batch_sync_teams_competitions_links(
            future_matches
        )
        await DbMatchesService._write_to_db(future_matches)

    @staticmethod
    async def remove_old_matches_from_db() -> None:
        """
        Delete Finished matches that were last updated 2 days ago from db
        """
        target_delete_date = datetime.today() - timedelta(days=2)
        await get_supabase().table("matches").delete("match_id").eq(
            "status_text", "Finished"
        ).eq("updated_at", target_delete_date.isoformat()).execute()

    @staticmethod
    async def _get_existing_matches() -> dict[int, dict[str, Any]]:
        """
        Get a list of all existing matches in our DB
        :return: a dictionary mapping matches ID to match status and start time
        """
        matches_in_db = (
            await get_supabase()
            .table("matches")
            .select("external_api_id", "status_text", "start_time")
            .execute()
        )
        return {
            rec["external_api_id"]: {
                "status_text": rec["status_text"],
                "start_time": rec["start_time"],
            }
            for rec in matches_in_db.data
        }

    @staticmethod
    def _need_update(new_match: BaseMatch, existing_match_data: dict[str, Any] | None) -> bool:
        """
        Checks if the status of a future game has been changed (rescheduled, canceled, etc...)
        :param new_match: The current data about the match
        :param existing_match_data: The data about the match as stored in the database
        :return: if there is a difference between the data stored to the current one
        """
        if not new_match.is_future_match():
            return False
        if existing_match_data is None:
            return True
        return (
            new_match.status_text == existing_match_data["status_text"]
            and new_match.start_time == existing_match_data["start_time"]
        )

    @classmethod
    async def _write_to_db(cls, future_matches: list[BaseMatch]) -> None:
        """
        Write a list of future matches to db
        :param future_matches: list of future matches
        """
        matches_in_db = await DbMatchesService._get_existing_matches()
        matches_to_update = [
            MatchProcessService.process_single_match(match).model_dump(
                mode="json", exclude_none=True
            )
            for match in future_matches
            if cls._need_update(match, matches_in_db.get(match.external_api_id))
        ]
        await get_supabase().table("matches").upsert(
            matches_to_update, on_conflict="external_api_id"
        ).execute()
