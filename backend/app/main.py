from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_supabase # Import the init function

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs on startup
    await init_supabase()
    yield
    # Add cleanup logic here if needed (e.g., closing connections)

app = FastAPI(
    title="SmartSportsAlarm API",
    lifespan=lifespan
)

@app.get("/health")
def health():
    return {"status": "ok"}