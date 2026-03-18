from fastapi import FastAPI

from .database import get_supabase

app = FastAPI(title="SmartSportsAlarm API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/supabase/health")
def supabase_health():
    _ = get_supabase()
    return {"status": "ok"}
