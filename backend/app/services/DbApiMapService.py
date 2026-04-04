from ..database import get_supabase


class DbApiMapService:

    @staticmethod
    async def get_competition_mapping() -> dict[int, int]:
        """
        Get the mapping between internal competition IDs to API competition IDs.
        """
        comp_res = await get_supabase().table("competitions").select("id", "external_api_id").execute()
        return {int(rec["external_api_id"]): int(rec["id"]) for rec in comp_res.data}

    @staticmethod
    async def get_team_mapping() -> dict[int, int]:
        """
        Get the mapping between internal team IDs to API team IDs.
        """
        team_res = await get_supabase().table("teams").select("id, external_api_id").execute()
        return {int(rec["external_api_id"]): int(rec["id"]) for rec in team_res.data}

    @staticmethod
    async def get_team_competitions_pairing() -> set[tuple[int, int]]:
        """
        Get the pairing between team IDs and competition the team takes part in
        """
        link_res = await get_supabase().table("team_competitions").select("team_id, competition_id").execute()
        return {(int(rec["team_id"]), int(rec["competition_id"])) for rec in link_res.data}
