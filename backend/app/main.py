import asyncio
import logging
import sys
from typing import Any

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.app.core.matches import BaseMatch
from .database import init_supabase
from .services.LiveMatchSyncService import LiveMatchSyncService

# Setup logger for background task visibility
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("uvicorn")


async def run_sync_worker(interval_seconds: int = 60):
    """
    Background worker that runs the sync service in a loop.
    """
    logger.info("Starting sync worker")
    sync_service = LiveMatchSyncService()
    while True:
        try:
            await sync_service.sync_live_matches()
        except Exception as e:
            logger.error(f"Background sync worker encountered an error: {e}")

        # Wait for the next sync cycle
        await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and start background worker
    await init_supabase()

    # Create the background task
    sync_task = asyncio.create_task(run_sync_worker(interval_seconds=60))

    yield

    # Shutdown: Cancel the background task gracefully
    sync_task.cancel()
    try:
        await sync_task
    except asyncio.CancelledError:
        logger.info("Background sync worker cancelled successfully")


app = FastAPI(
    title="SmartSportsAlarm API",
    lifespan=lifespan
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/matches")
async def get_matches(user_id: int,
                      my_only: bool = False,
                      live: bool = None,
                      competition_id: int = None,
                      team_id: int = None,
                      from_date: int = None,
                      to_date: int = None,
                      ) -> list[dict[str, Any]]:
    if not (my_only and competition_id and team_id):
        # TODO set time range as today only



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)