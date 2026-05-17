from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
import database
import scraper as sc

# ── Scheduler ──────────────────────────────────────────────────────────────
scheduler = BackgroundScheduler()


def scheduled_scrape():
    print("[Scheduler] Running periodic scrape...")
    sc.run_scrape()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    database.init_db()
    # Run an initial scrape on first boot (non-blocking)
    import threading
    t = threading.Thread(target=sc.run_scrape, daemon=True)
    t.start()
    # Schedule every 6 hours
    scheduler.add_job(scheduled_scrape, "interval", hours=6)
    scheduler.start()
    yield
    # Shutdown
    scheduler.shutdown(wait=False)


# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(title="Israel Jobs Finder API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/api/jobs")
def search_jobs(
    title:      str = Query(None),
    city:       str = Query(None),
    cities:     str = Query(None),  # comma-separated list for multi-select
    experience: str = Query(None),
    work_model: str = Query(None),
    source:     str = Query(None),
    days:       int = Query(None),
    salary_min: int = Query(None),
    limit:      int = Query(200),
    offset:     int = Query(0),
):
    cities_list = [c.strip() for c in cities.split(",") if c.strip()] if cities else None
    jobs = database.get_jobs(
        title=title, city=city, cities=cities_list, experience=experience,
        work_model=work_model, source=source, days=days,
        salary_min=salary_min, limit=limit, offset=offset,
    )
    return {"count": len(jobs), "jobs": jobs}


@app.get("/api/cities")
def list_cities():
    return database.get_cities()


@app.get("/api/stats")
def stats():
    return database.get_stats()


@app.post("/api/scrape")
def trigger_scrape(
    background_tasks: BackgroundTasks,
    queries: list[str] = Query(None),
):
    """Manually trigger a scrape (runs in background)."""
    background_tasks.add_task(sc.run_scrape, queries)
    return {"status": "Scrape started in background"}
