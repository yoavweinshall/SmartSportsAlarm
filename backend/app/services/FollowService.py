import logging

from ..database import get_supabase


logger = logging.getLogger(__name__)

class FollowService:
    """
        Service for managing user match follow/unfollow actions.
        """

    @staticmethod
    async def follow_match(user_id: str, match_id: int) -> bool:
        """
        Adds a match to the user's followed list.
        :param user_id: The UUID of the user.
        :param match_id: The ID of the match to follow.
        :return: True if successful, False otherwise.
        """
        try:
            # We use upsert to avoid errors if the user clicks "follow" twice very fast
            response = (
                await get_supabase()
                .table("user_followed_matches")
                .upsert(
                    {"user_id": user_id, "match_id": match_id},
                    on_conflict="user_id, match_id"
                )
                .execute()
            )
            return True
        except Exception as e:
            logger.error(f"Failed to follow match {match_id} for user {user_id}: {e}")
            return False

    @staticmethod
    async def unfollow_match(user_id: str, match_id: int) -> bool:
        """
        Removes a match from the user's followed list.
        :param user_id: The UUID of the user.
        :param match_id: The ID of the match to unfollow.
        :return: True if successful, False otherwise.
        """
        try:
            response = (
                await get_supabase()
                .table("user_followed_matches")
                .delete()
                .eq("user_id", user_id)
                .eq("match_id", match_id)
                .execute()
            )
            return True
        except Exception as e:
            logger.error(f"Failed to unfollow match {match_id} for user {user_id}: {e}")
            return False

    @staticmethod
    async def get_user_followed_matches(user_id: str) -> list[int]:
        """
        Gets a list of all match IDs followed by a specific user.
        :param user_id: The UUID of the user.
        :return: A list of match IDs.
        """
        try:
            response = (
                await get_supabase()
                .table("user_followed_matches")
                .select("match_id")
                .eq("user_id", user_id)
                .execute()
            )
            # Extract just the match IDs from the dictionary list
            return [rec["match_id"] for rec in response.data]
        except Exception as e:
            logger.error(f"Failed to fetch followed matches for user {user_id}: {e}")
            return []