from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import AsyncClient, acreate_client

# Explicitly find .env in the backend folder (one level up from app/)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        # Debug: print the path we tried to load
        print(f"DEBUG: Looking for .env at {BASE_DIR / '.env'}")
        raise RuntimeError(f"Missing environment variable {name}")
    return value

SUPABASE_URL = _require_env("SUPABASE_URL")
SUPABASE_KEY = _require_env("SUPABASE_KEY")

# Renamed global variable to avoid shadowing the library name
supabase_client: AsyncClient | None = None

async def init_supabase():
    global supabase_client
    if supabase_client is None:
        supabase_client = await acreate_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase() -> AsyncClient:
    if supabase_client is None:
        raise RuntimeError("Supabase client not initialized. Call init_supabase first.")
    return supabase_client