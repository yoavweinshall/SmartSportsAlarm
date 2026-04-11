import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Any

from ..database import get_supabase

logger = logging.getLogger(__name__)
security = HTTPBearer()
match_router = APIRouter(prefix="/matches", tags=["matches"])


async def get_current_user_id(res: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    token = res.credentials
    try:
        # Send the token to Supabase for verification
        user_res = await get_supabase().auth.get_user(token)

        if not user_res or not user_res.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return user_res.user.id
    except Exception as e:
        print(f"Auth error: {str(e)}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@match_router.get("/")
async def get_matches(
    is_live: bool = Query(False, description="Filter only live matches"),
    competition_id: Optional[int] = Query(None, description="Filter by specific competition"),
    team_id: Optional[int] = Query(None, description="Filter by specific team (home or away)"),
    followed_only: bool = Query(False, description="Filter only matches followed by the user"),
    cursor: Optional[datetime] = Query(None, description="Pagination cursor (ISO datetime). Defaults to start of today."),
    direction: str = Query("forward", description="Pagination direction: 'forward' or 'backward'"),
    limit: int = Query(50, description="Maximum number of matches to return", ge=1, le=200),
    user_id: Optional[str] = Depends(get_current_user_id),
) -> dict[str, list[dict[str, Any]]]:
    """
    Fetch matches using cursor-based pagination.
    :param is_live: Filter only live matches
    :param competition_id: Filter by competition ID
    :param team_id: Filter by team ID
    :param followed_only: Filter only matches followed by the user
    :param cursor: Pagination cursor (ISO datetime). Defaults to start of today.
    :param direction: Pagination direction: 'forward' or 'backward'. Defaults to 'forward'
    :param limit: Maximum number of matches to return
    :param user_id: Filter by user ID
    :return: Paginated matches
    """
    try:
        # Default cursor to midnight of the current local day when none is provided
        effective_cursor = cursor or datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cursor_str = effective_cursor.isoformat()

        query = (
            get_supabase()
            .table("matches")
            .select(
                "*, "
                "home_team:teams!home_team_id(id, name, short_name, primary_color), "
                "away_team:teams!away_team_id(id, name, short_name, primary_color), "
                "competition:competitions(id, name, color)"
            )
        )
        if is_live:  # Adds a filter of only live matches in the DB
            query = query.eq("stage_group", 3)
        if competition_id:  # Adds a filter of only specific competition
            query = query.eq("competition_id", competition_id)
        if team_id:  # Adds a filter of only specific Team
            query = query.or_(f"home_team_id.eq.{team_id},away_team_id.eq.{team_id}")
        if followed_only:  # Handle the case we asked only games we're already following
            if not user_id:
                raise HTTPException(status_code=401, detail="Authentication required")
            follows_res = (
                await get_supabase().table("user_followed_matches").select("match_id").eq("user_id", user_id).execute()
            )

            followed_ids = [row["match_id"] for row in follows_res.data]
            if not followed_ids:
                return {"matches": []}
            query = query.in_("id", followed_ids)

        if direction == "backward":
            # Fetch everything strictly before the cursor in DESC order so LIMIT cuts the closest matches
            query = query.lt("start_time", cursor_str).order("start_time", desc=True).limit(limit)
        else:
            # Forward: include the cursor timestamp itself (covers the default midnight boundary)
            query = query.gte("start_time", cursor_str).order("start_time", desc=False).limit(limit)

        response = await query.execute()
        matches = response.data

        if direction == "backward":
            # Reverse DESC results so the response is always in chronological (ASC) order
            matches = list(reversed(matches))

        return {"matches": matches}

    except Exception as e:
        logger.error(f"fetching matches: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching matches")


@match_router.post("/{match_id}/follow")
async def change_follow_status(match_id: int, user_id: Optional[int] = Depends(get_current_user_id)) -> None:
    """
    Add a match to the matches user is following
    :param match_id: Match ID
    :param user_id: User ID
    """
    await get_supabase().table("user_followed_matches").upsert({"user_id": user_id, "match_id": match_id}).execute()


@match_router.delete("/{match_id}/follow")
async def change_follow_status(match_id: int, user_id: Optional[int] = Depends(get_current_user_id)) -> None:
    """
    Remove a match from the matches user is following
    :param match_id: Match ID
    :param user_id: User ID
    """
    await get_supabase().table("user_followed_matches").delete().eq("user_id", user_id).eq(
        "match_id", match_id
    ).execute()
