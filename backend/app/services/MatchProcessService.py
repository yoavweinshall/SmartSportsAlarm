import logging
from datetime import datetime, timezone

from .CacheService import CacheService
from ..core.matches import BaseMatch

logger = logging.getLogger(__name__)


class MatchProcessService:

    @staticmethod
    def process_single_match(match: BaseMatch) -> BaseMatch | None:
        """
        Process the state of a game
        :param match: the data of the live match we got from the API
        :return: updated game data
        """
        try:
            match.updated_at = datetime.now(timezone.utc)
            match.home_team_id = CacheService.get_instance().api_to_internal_team_id.get(match.home_team_id)
            match.away_team_id = CacheService.get_instance().api_to_internal_team_id.get(match.away_team_id)
            match.competition_id = CacheService.get_instance().supported_competition_ids.get(match.competition_id)

            return match

        except ValueError as e:
            logger.error(f"Invalid match data: {match}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to process game {match.external_api_id}: {e}")
            return None
