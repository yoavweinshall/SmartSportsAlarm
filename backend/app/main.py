import asyncio
import logging
import sys

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.services import DbMatchesService
from .database import init_supabase
from .routers import match_router
from .services.LiveMatchSyncService import LiveMatchSyncService

# Setup logger for background task visibility
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("uvicorn")


async def update_live_matches(interval_seconds: int = 60):
    """
    Background worker that runs the sync service of the live matches in a loop.
    """
    logger.info("Starting sync live matches worker")
    sync_service = LiveMatchSyncService()
    while True:
        try:
            await sync_service.sync_live_matches()
        except Exception as e:
            logger.error(f"Background sync live matches worker encountered an error: {e}")

        # Wait for the next sync cycle
        await asyncio.sleep(interval_seconds)


async def update_none_live_matches_on_db(interval_hours: int = 24):
    """
    Background worker that runs the sync service of the future matches in a loop.
    """
    logger.info("Starting sync future matches worker")
    while True:
        try:
            await DbMatchesService.add_future_matches_to_db()
            await DbMatchesService.remove_old_matches_from_db()
        except Exception as e:
            logger.error(f"Background sync future matches worker encountered an error: {e}")

        # Wait for the next sync cycle
        await asyncio.sleep(interval_hours * 60 * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and start background worker
    await init_supabase()

    # Create the background task
    live_matches_sync_task = asyncio.create_task(update_live_matches(interval_seconds=60))
    future_matches_sync_task = asyncio.create_task(update_none_live_matches_on_db(interval_hours=24))

    yield

    # Shutdown: Cancel the background task gracefully
    live_matches_sync_task.cancel()
    future_matches_sync_task.cancel()
    try:

        await asyncio.gather(live_matches_sync_task, future_matches_sync_task, return_exceptions=True)
    except asyncio.CancelledError:
        logger.info("Background sync worker cancelled successfully")


app = FastAPI(title="SmartSportsAlarm API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(match_router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
