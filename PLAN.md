# 🇮🇱 Israel Jobs Finder — Revised Plan

> **One-liner:** A simple web app that scrapes Israeli job boards, lets you search by role, and shows results on an interactive map + list — filtered by area, salary, and experience.

---

## 🎯 What It Does (Simple Version)

1. You type a job title: `Product Manager`, `Software Engineer`, `Automation QA`
2. The app shows you all matching open positions in Israel
3. Results appear as **pins on a map** (by city) and as a **scrollable list**
4. You can filter by: **area**, **experience level**, **salary range**
5. Data refreshes automatically in the background every few hours

That's it. Clean, simple, useful.

---

## 📡 Data Sources — Israeli Job Boards (All Public, All Free)

| Source | URL | Notes |
|---|---|---|
| **AllJobs** | alljobs.co.il | Israel's #1 job board, huge database |
| **Drushim** | drushim.co.il | Major Israeli job board, strong tech section |
| **Jobmaster** | jobmaster.co.il | Large Israeli job board |
| **Comeet** | comeet.com/jobs | ATS used by many Israeli tech companies (Wix, Monday, etc.) |
| **Glassdoor Israel** | glassdoor.com | Has salary data — great for that filter |

> All of these are **public pages** — no login or account needed. Zero risk.

---

## 🏗️ Architecture (Kept Simple)

```
Scheduler (every 6hrs)
    └── Python Scraper
            └── AllJobs + Drushim + Jobmaster + Comeet
                    └── SQLite Database
                            └── FastAPI Backend
                                    └── React Frontend
                                            ├── Map View (Leaflet + OpenStreetMap)
                                            ├── List View
                                            └── Filters Panel
```

**Three moving parts:**
- 🐍 **Python scraper** — collects jobs, saves to DB
- ⚡ **FastAPI backend** — serves data via simple REST API
- ⚛️ **React frontend** — map + list + filters

---

## 🛠️ Tech Stack — 100% Free

| Layer | Tool | Cost |
|---|---|---|
| **Scraping** | Python + BeautifulSoup + Requests | Free |
| **JS-heavy sites** | Playwright (fallback) | Free |
| **Scheduler** | APScheduler | Free |
| **Database** | SQLite (just a file) | Free |
| **Backend** | FastAPI | Free |
| **Frontend** | React + Vite | Free |
| **Map** | Leaflet.js + OpenStreetMap | Free |
| **Geocoding** | Nominatim (OpenStreetMap) | Free |
| **Hosting** | Run locally on your machine | Free |

---

## 🗺️ Map View — How It Works

- Each job is tagged with a **city** (Tel Aviv, Herzliya, Ra'anana, Haifa, etc.)
- City names are converted to **lat/lng coordinates** using Nominatim (free geocoding)
- Jobs cluster on the map by location — click a pin → see the open positions there
- Filter the map live by role, salary, experience

**Key Israeli tech hubs on the map:**

| City | Tech Scene |
|---|---|
| Tel Aviv | Startups, fintech, everything |
| Herzliya | Big tech companies (Microsoft, Google IL) |
| Ra'anana | Enterprise tech, pharmaceuticals |
| Petah Tikva | Insurance tech, enterprise |
| Be'er Sheva | Cyber Valley, government tech |
| Haifa | Intel, Nvidia, Technion-adjacent |
| Jerusalem | Government, academia |

---

## 🔍 Search & Filter Criteria

### Primary Search
- **Job Title** (free text): `Product Manager`, `Software Engineer`, `QA Automation`, `DevOps`, etc.

### Filters
| Filter | Options |
|---|---|
| **Area / City** | Tel Aviv, Herzliya, Haifa, Beer Sheva, Ra'anana, Remote, All |
| **Experience Level** | Junior (0-2y), Mid (2-5y), Senior (5+y), Lead/Manager |
| **Employment Type** | Full-time, Part-time, Contract, Freelance |
| **Work Model** | On-site, Hybrid, Remote |
| **Salary Range** | Slider: ₪0 – ₪50,000/month (when available) |
| **Posted Within** | Last 24h / Last 7 days / Last 30 days |
| **Source** | AllJobs / Drushim / Jobmaster / Comeet |

---

## 🗄️ Data Model (SQLite)

```sql
CREATE TABLE jobs (
    id            TEXT PRIMARY KEY,  -- hash of source + job_id
    source        TEXT,              -- 'alljobs', 'drushim', etc.
    title         TEXT,
    company       TEXT,
    location_text TEXT,              -- raw text: "Tel Aviv, Israel"
    city          TEXT,              -- normalized: "Tel Aviv"
    lat           REAL,
    lng           REAL,
    work_model    TEXT,              -- 'remote', 'hybrid', 'onsite'
    experience    TEXT,              -- 'junior', 'mid', 'senior'
    salary_min    INTEGER,
    salary_max    INTEGER,
    description   TEXT,
    url           TEXT,
    posted_at     DATETIME,
    scraped_at    DATETIME
);
```

---

## 📦 Build Phases

### Phase 1 — Scraper + DB (Days 1–3)
- [ ] Set up Python project structure
- [ ] Write scraper for **AllJobs** (biggest, starts here)
- [ ] Write scraper for **Drushim**
- [ ] Parse: title, company, location, salary, experience, URL
- [ ] Save to SQLite, deduplicate by job ID
- [ ] APScheduler to run every 6 hours

### Phase 2 — Backend API (Day 4)
- [ ] FastAPI with these endpoints:
  - `GET /jobs?title=PM&city=Tel+Aviv&experience=senior` → filtered job list
  - `GET /jobs/map` → jobs with lat/lng for map pins
  - `GET /cities` → list of available cities
- [ ] Geocode cities on first insert (Nominatim, cache results)

### Phase 3 — Frontend (Days 5–7)
- [ ] React + Vite app
- [ ] **Search bar** — type role, hit enter
- [ ] **Filters panel** — area, experience, salary, work model, date
- [ ] **Map view** — Leaflet + OpenStreetMap, clustered pins per city
- [ ] **List view** — cards with job title, company, location, salary, tags
- [ ] Toggle between Map / List
- [ ] Click job → opens original posting in new tab

### Phase 4 — Polish (Day 8)
- [ ] Add Comeet + Jobmaster scrapers
- [ ] Auto-refresh badge ("Updated 2 hours ago")
- [ ] Mobile-responsive layout
- [ ] Dark mode 🌙

---

## 📅 Timeline

| Day | What's Done |
|---|---|
| 1–2 | AllJobs + Drushim scrapers working, data in SQLite |
| 3 | Scheduler live, geocoding working |
| 4 | FastAPI backend with all endpoints |
| 5–6 | React frontend: search + list view |
| 7 | Map view with Leaflet |
| 8 | Filters, polish, mobile |

---

## ✅ What You'll Have at the End

A **personal job intelligence tool** that:
- Runs on your laptop
- Refreshes Israeli job listings every 6 hours automatically
- Lets you search `Product Manager` and instantly see:
  - 📍 A map of Israel with job pins by city
  - 📋 A list sorted by recency with salary/experience tags
  - 🔧 Filters to narrow down exactly what you want
- Zero cost, zero LinkedIn risk, zero complexity

---

## 🚦 Ready to Build?

Just confirm:
1. **Which role do you want to test with first?** (PM / Software Engineer / QA?)
2. **Preferred city/area?** Or show all Israel?
3. **Should we start coding today?** 🚀
