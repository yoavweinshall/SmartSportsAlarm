import httpx
from typing import List, Dict

from backend.app.adapters.matchAdapters.scores365MatchAdapter import Scores365MatchAdapter
from backend.app.core.matches import BaseMatch


class ScoresApiService:

    BASE_URL = "https://webws.365scores.com/web/games/allscores"

    async def fetch_live_scores(self) -> List[BaseMatch]:
        """
        Fetch all current live scores from the api
        """
        params = {
            "onlyLiveGames": True
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            adapter_match = [Scores365MatchAdapter.model_validate(match) for match in response.json().get("games")]
            return [match.to_internal_match() for match in adapter_match]