from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import AsyncClient, acreate_client # Use async imports

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable {name}")
    return value

SUPABASE_URL = _require_env("SUPABASE_URL")
SUPABASE_KEY = _require_env("SUPABASE_KEY")

# Set global variable to None initially
supabase: AsyncClient | None = None

async def init_supabase():
    """Initializes the async Supabase client."""
    global supabase
    if supabase is None:
        supabase = await acreate_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase() -> AsyncClient:
    """Returns the initialized client or raises error if not ready."""
    if supabase is None:
        raise RuntimeError("Supabase client not initialized. Call init_supabase first.")
    return supabase