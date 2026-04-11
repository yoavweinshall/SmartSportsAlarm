import logging

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
    user_id: Optional[str] = Depends(get_current_user_id),
) -> dict[str, list[dict[str, Any]]]:
    """
    Fetch matches dynamically based on query parameters.
    Builds the Supabase query step-by-step to avoid fetching unnecessary data.
    """
    try:
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

        response = await query.order("start_time", desc=False).execute()
        return {"matches": response.data}

    except Exception as e:
        logger.error(f"fetching matches: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching matches")


@match_router.post("/{match_id}/follow")
async def change_follow_status(match_id: int, user_id: Optional[int] = Depends(get_current_user_id)) -> None:
    await get_supabase().table("user_followed_matches").upsert({"user_id": user_id, "match_id": match_id}).execute()


@match_router.delete("/{match_id}/follow")
async def change_follow_status(match_id: int, user_id: Optional[int] = Depends(get_current_user_id)) -> None:
    await get_supabase().table("user_followed_matches").delete().eq("user_id", user_id).eq(
        "match_id", match_id
    ).execute()
