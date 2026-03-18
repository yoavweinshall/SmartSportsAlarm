import httpx
from typing import Any


class ScoresApiService:

    BASE_URL = "https://webws.365scores.com/web/games/allscores"

    async def fetch_live_scores(self) -> Any:
        """
        Fetch all current live scores from the api
        """
        params = {
            "onlyLiveGames": True
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json().get("games")