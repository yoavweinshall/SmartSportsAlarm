import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import init_supabase
from .services.LiveMatchSyncService import LiveMatchSyncService

# Setup logger for background task visibility
logger = logging.getLogger("uvicorn")


async def run_sync_worker(interval_seconds: int = 60):
    """
    Background worker that runs the sync service in a loop.
    """
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