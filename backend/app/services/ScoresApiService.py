import httpx

from backend.app.adapters.matchAdapters.scores365MatchAdapter import Scores365MatchAdapter
from backend.app.core.matches import BaseMatch


class ScoresApiService:

    BASE_URL = "https://webws.365scores.com/web/games/allscores"

    async def fetch_matches(self, **kwargs) -> list[BaseMatch]:
        """
        Fetch all current live scores from the api
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=kwargs)
            response.raise_for_status()
            supported_matches = [match for match in response.json().get("games")]
            adapter_match = [Scores365MatchAdapter.model_validate(match) for match in supported_matches]
            return [match.to_internal_match() for match in adapter_match]