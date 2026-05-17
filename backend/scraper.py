import hashlib
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ─────────────────────────────────────────────
# Israeli cities → coordinates lookup table
# ─────────────────────────────────────────────
ISRAEL_CITIES = {
    # Hebrew
    "תל אביב":      {"city": "תל אביב",      "lat": 32.0853, "lng": 34.7818},
    "תל אביב יפו":  {"city": "תל אביב",      "lat": 32.0853, "lng": 34.7818},
    "ירושלים":      {"city": "ירושלים",      "lat": 31.7683, "lng": 35.2137},
    "חיפה":         {"city": "חיפה",         "lat": 32.7940, "lng": 34.9896},
    "באר שבע":      {"city": "באר שבע",      "lat": 31.2517, "lng": 34.7915},
    "הרצליה":       {"city": "הרצליה",       "lat": 32.1663, "lng": 34.8437},
    "רעננה":        {"city": "רעננה",        "lat": 32.1836, "lng": 34.8701},
    "פתח תקווה":    {"city": "פתח תקווה",    "lat": 32.0878, "lng": 34.8878},
    "ראשון לציון":  {"city": "ראשון לציון",  "lat": 31.9642, "lng": 34.8007},
    "נתניה":        {"city": "נתניה",        "lat": 32.3226, "lng": 34.8533},
    "אשדוד":        {"city": "אשדוד",        "lat": 31.8040, "lng": 34.6553},
    "רחובות":       {"city": "רחובות",       "lat": 31.8969, "lng": 34.8078},
    "מודיעין":      {"city": "מודיעין",      "lat": 31.8969, "lng": 35.0100},
    "רמת גן":       {"city": "רמת גן",       "lat": 32.0705, "lng": 34.8239},
    "חולון":        {"city": "חולון",        "lat": 32.0116, "lng": 34.7752},
    "כפר סבא":      {"city": "כפר סבא",      "lat": 32.1780, "lng": 34.9063},
    "גבעתיים":      {"city": "גבעתיים",      "lat": 32.0702, "lng": 34.8111},
    "אשקלון":       {"city": "אשקלון",       "lat": 31.6688, "lng": 34.5742},
    "בת ים":        {"city": "בת ים",        "lat": 32.0219, "lng": 34.7509},
    "בני ברק":      {"city": "בני ברק",      "lat": 32.0840, "lng": 34.8340},
    "נס ציונה":     {"city": "נס ציונה",     "lat": 31.9296, "lng": 34.7987},
    "לוד":          {"city": "לוד",          "lat": 31.9508, "lng": 34.8978},
    "חדרה":         {"city": "חדרה",         "lat": 32.4344, "lng": 34.9197},
    "יבנה":         {"city": "יבנה",         "lat": 31.8681, "lng": 34.7433},
    "כפר יונה":     {"city": "כפר יונה",     "lat": 32.3125, "lng": 34.9375},
    "טבריה":        {"city": "טבריה",        "lat": 32.7953, "lng": 35.5315},
    "עכו":          {"city": "עכו",          "lat": 32.9309, "lng": 35.0832},
    "נהריה":        {"city": "נהריה",        "lat": 33.0040, "lng": 35.0950},
    "קרית גת":      {"city": "קרית גת",      "lat": 31.6103, "lng": 34.7642},
    "גבעת שמואל":   {"city": "גבעת שמואל",   "lat": 32.0788, "lng": 34.8378},
    "אור יהודה":    {"city": "אור יהודה",    "lat": 32.0271, "lng": 34.8555},
    "רמלה":         {"city": "רמלה",         "lat": 31.9285, "lng": 34.8693},
    "יהוד":         {"city": "יהוד",         "lat": 32.0322, "lng": 34.8880},
    "יהוד מונוסון": {"city": "יהוד",         "lat": 32.0322, "lng": 34.8880},
    "ראש העין":     {"city": "ראש העין",     "lat": 32.0953, "lng": 34.9558},
    "רמת השרון":    {"city": "רמת השרון",    "lat": 32.1476, "lng": 34.8397},
    "מרחוק":        {"city": "Remote",        "lat": 31.500,  "lng": 34.750},
    # English
    "tel aviv":          {"city": "תל אביב",      "lat": 32.0853, "lng": 34.7818},
    "tel aviv-yafo":     {"city": "תל אביב",      "lat": 32.0853, "lng": 34.7818},
    "jerusalem":         {"city": "ירושלים",      "lat": 31.7683, "lng": 35.2137},
    "haifa":             {"city": "חיפה",         "lat": 32.7940, "lng": 34.9896},
    "beer sheva":        {"city": "באר שבע",      "lat": 31.2517, "lng": 34.7915},
    "beersheba":         {"city": "באר שבע",      "lat": 31.2517, "lng": 34.7915},
    "herzliya":          {"city": "הרצליה",       "lat": 32.1663, "lng": 34.8437},
    "raanana":           {"city": "רעננה",        "lat": 32.1836, "lng": 34.8701},
    "ra'anana":          {"city": "רעננה",        "lat": 32.1836, "lng": 34.8701},
    "petah tikva":       {"city": "פתח תקווה",    "lat": 32.0878, "lng": 34.8878},
    "rishon lezion":     {"city": "ראשון לציון",  "lat": 31.9642, "lng": 34.8007},
    "netanya":           {"city": "נתניה",        "lat": 32.3226, "lng": 34.8533},
    "ashdod":            {"city": "אשדוד",        "lat": 31.8040, "lng": 34.6553},
    "rehovot":           {"city": "רחובות",       "lat": 31.8969, "lng": 34.8078},
    "modiin":            {"city": "מודיעין",      "lat": 31.8969, "lng": 35.0100},
    "modi'in":           {"city": "מודיעין",      "lat": 31.8969, "lng": 35.0100},
    "ramat gan":         {"city": "רמת גן",       "lat": 32.0705, "lng": 34.8239},
    "holon":             {"city": "חולון",        "lat": 32.0116, "lng": 34.7752},
    "kfar saba":         {"city": "כפר סבא",      "lat": 32.1780, "lng": 34.9063},
    "bnei brak":         {"city": "בני ברק",      "lat": 32.0840, "lng": 34.8340},
    "remote":            {"city": "Remote",        "lat": 31.500,  "lng": 34.750},
    "yehud":             {"city": "יהוד",         "lat": 32.0322, "lng": 34.8880},
    "rosh haayin":       {"city": "ראש העין",     "lat": 32.0953, "lng": 34.9558},
    "ramat hasharon":    {"city": "רמת השרון",    "lat": 32.1476, "lng": 34.8397},
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def geocode_location(location_text: str) -> dict:
    if not location_text:
        return {"city": "Unknown", "lat": 31.5, "lng": 34.75}
    loc_lower = location_text.lower().strip()
    for key, data in ISRAEL_CITIES.items():
        if key.lower() in loc_lower:
            return data
    city_name = location_text.split(",")[0].strip()
    return {"city": city_name, "lat": 31.5, "lng": 34.75}


def make_job_id(source: str, identifier: str) -> str:
    return hashlib.md5(f"{source}:{identifier}".encode()).hexdigest()


def detect_experience(text: str) -> str:
    tl = text.lower()
    if any(w in tl for w in ["senior", "sr.", "lead", "principal", "staff", "architect", "בכיר", "מנהל"]):
        return "senior"
    if any(w in tl for w in ["junior", "jr.", "entry", "graduate", "intern", "סטודנט", "זוטר", "ללא ניסיון"]):
        return "junior"
    m = re.search(r'(\d+)\+?\s*(?:years?|שנ[וי]ת?)\s*(?:of\s*)?(?:experience|ניסיון)', tl)
    if m:
        yrs = int(m.group(1))
        return "junior" if yrs <= 2 else "senior" if yrs > 5 else "mid"
    return "mid"


_CATEGORY_MAP = [
    ("gaming",        ["game ", "gaming", "unity", "unreal", "esport", "משחק"]),
    ("fintech",       ["fintech", "banking", "payment", "insurance", "financial", "forex", "trading", "blockchain", "crypto", "wallet", "פינטק", "פיננסי"]),
    ("adtech",        ["adtech", "ad-tech", "advertising", "rtb", "dsp", "ssp", "programmatic", "media buy"]),
    ("cybersecurity", ["security", "cyber", "infosec", "siem", " soc ", "penetration", "pentest", "ciso", "אבטחה", "סייבר"]),
    ("data & ai",     ["data engineer", "data scientist", "data analyst", "analytics", "business intelligence", " bi ", "machine learning", "artificial intelligence", "nlp", "deep learning", "llm", "מדעני נתונים"]),
    ("devops",        ["devops", " sre ", "platform engineer", "infrastructure", "kubernetes", "k8s", "terraform", "cloud engineer", "דבאופס"]),
    ("mobile",        ["mobile", "ios developer", "android developer", "react native", "flutter", "swift developer", "kotlin"]),
    ("frontend",      ["frontend", "front-end", "react developer", "vue developer", "angular developer", "ui developer", "פרונטאנד"]),
    ("backend",       ["backend", "back-end", "server-side", "node.js developer", "python developer", "java developer", "golang", "ruby on rails", "בקאנד"]),
    ("product",       ["product manager", "product owner", "vp product", " cpo", "מנהל מוצר", "product lead"]),
    ("design",        ["ux designer", "ui designer", "ui/ux", "product designer", "interaction design", "מעצב"]),
    ("qa",            ["qa engineer", "quality assurance", "test automation", "automation tester", " qe ", "בדיקות"]),
    ("healthcare",    ["health", "medical", "pharma", "biotech", "medtech", "clinical"]),
    ("ecommerce",     ["ecommerce", "e-commerce", "retail tech", "marketplace"]),
]


def detect_category(title: str, description: str = "") -> str:
    text = (title + " " + description).lower()
    for category, keywords in _CATEGORY_MAP:
        if any(kw in text for kw in keywords):
            return category
    return "other"


def detect_work_model(text: str) -> str:
    tl = text.lower()
    if any(w in tl for w in ["remote", "מרחוק", "work from home", "wfh", "עבודה מהבית"]):
        return "remote"
    if any(w in tl for w in ["hybrid", "היברידי", "גמיש"]):
        return "hybrid"
    return "onsite"


def parse_salary(text: str):
    if not text:
        return None, None
    patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*[-–]\s*(\d{1,3}(?:,\d{3})*)',
        r'₪\s*(\d+(?:[,\.]\d+)?)\s*[-–]\s*₪?\s*(\d+(?:[,\.]\d+)?)',
        r'(\d+)[kK]\s*[-–]\s*(\d+)[kK]',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            try:
                lo = int(m.group(1).replace(",", ""))
                hi = int(m.group(2).replace(",", ""))
                chunk = text[m.start():m.end()].lower()
                if "k" in chunk:
                    lo, hi = lo * 1000, hi * 1000
                # Israeli monthly salaries start around ₪3,000
                if lo >= 3000 and hi >= 3000:
                    return lo, hi
            except Exception:
                pass
    return None, None


def _map_drushim_experience(exp_hebrew: str, full_text: str) -> str:
    if exp_hebrew:
        if "ללא" in exp_hebrew:
            return "junior"
        m = re.search(r'(\d+)', exp_hebrew)
        if m:
            yrs = int(m.group(1))
            if yrs <= 2:
                return "junior"
            if yrs <= 4:
                return "mid"
            return "senior"
    return detect_experience(full_text)


# ─────────────────────────────────────────────
# AllJobs Scraper  (server-side rendered HTML)
# ─────────────────────────────────────────────

class AllJobsScraper:
    BASE_URL   = "https://www.alljobs.co.il"
    SEARCH_URL = "https://www.alljobs.co.il/SearchResultsGuest.aspx"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        # Warm up cookies with homepage visit
        try:
            self.session.get(self.BASE_URL, timeout=10)
        except Exception:
            pass

    def search(self, query: str, max_pages: int = 3) -> list:
        all_jobs = []
        for page in range(1, max_pages + 1):
            try:
                params = {
                    "page": str(page),
                    "position": "",
                    "region": "0",
                    "type": "",
                    "freetxt": query,
                    "engine": "1",
                }
                resp = self.session.get(self.SEARCH_URL, params=params, timeout=20)
                resp.raise_for_status()
                jobs = self._parse_page(resp.text, query)
                if not jobs:
                    break
                all_jobs.extend(jobs)
                time.sleep(random.uniform(1.5, 3.0))
            except Exception as e:
                print(f"[AllJobs] p{page} error: {e}")
                break
        print(f"[AllJobs] '{query}' → {len(all_jobs)} jobs")
        return all_jobs

    def _parse_page(self, html: str, query: str) -> list:
        soup = BeautifulSoup(html, "lxml")
        job_boxes = soup.find_all("div", id=re.compile(r"^job-box\d+$"))
        return [j for box in job_boxes for j in [self._extract(box, query)] if j]

    def _extract(self, box, query: str):
        try:
            job_id_match = re.search(r"\d+", box.get("id", ""))
            if not job_id_match:
                return None
            job_id = job_id_match.group()

            # Title (Hebrew or English layout)
            title_el = box.select_one(".job-content-top-title h2") or box.select_one(".job-content-top-title h3")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                # Try LTR (English) layout
                title_link = box.select_one(".job-content-top-title-ltr a") or box.select_one("[class*='title-ltr'] a")
                if title_link:
                    title = title_link.get_text(strip=True)
            if not title:
                return None

            # Company
            company_el = box.select_one(".job-content-top-title .T14") or box.select_one(".job-content-top-title-ltr .T14")
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            company = company or "Unknown"

            # Location — prefer a specific city link over "מספר מקומות"
            location_text = "Israel"
            for loc_cls in [".job-content-top-location", ".job-content-top-location-ltr"]:
                loc_el = box.select_one(loc_cls)
                if loc_el:
                    city_link = loc_el.select_one("a")
                    if city_link:
                        location_text = city_link.get_text(strip=True)
                    else:
                        raw = loc_el.get_text(separator=" ", strip=True)
                        raw = re.sub(r"מיקום המשרה\s*:?|Location\s*:", "", raw).strip()
                        if raw and "מספר מקומות" not in raw:
                            location_text = raw.split()[0] if raw else "Israel"
                    break

            # URL
            link_el = box.select_one(".job-content-top-title a") or box.select_one(".job-content-top-title-ltr a")
            href = link_el["href"] if link_el and link_el.get("href") else f"/Job/?jobId={job_id}"
            url = href if href.startswith("http") else self.BASE_URL + href

            # Description text
            desc_el = box.find("div", id=re.compile(rf"^job-body-content{job_id}$"))
            card_text = desc_el.get_text(separator=" ", strip=True) if desc_el else box.get_text(" ", strip=True)

            sal_min, sal_max = parse_salary(card_text)
            geo = geocode_location(location_text)

            return {
                "id":            make_job_id("alljobs", job_id),
                "source":        "alljobs",
                "title":         title,
                "company":       company,
                "location_text": location_text,
                "city":          geo["city"],
                "lat":           geo["lat"],
                "lng":           geo["lng"],
                "work_model":    detect_work_model(card_text + " " + title),
                "experience":    detect_experience(title + " " + card_text),
                "category":      detect_category(title, card_text),
                "salary_min":    sal_min,
                "salary_max":    sal_max,
                "description":   card_text[:500],
                "url":           url,
                "posted_at":     datetime.utcnow().isoformat(),
                "scraped_at":    datetime.utcnow().isoformat(),
                "search_query":  query,
            }
        except Exception as e:
            print(f"[AllJobs] extract error: {e}")
            return None


# ─────────────────────────────────────────────
# Drushim Scraper  (internal JSON API)
# ─────────────────────────────────────────────

# Tech-related category IDs on drushim.co.il
DRUSHIM_CATEGORIES = [
    (6,  "הייטק-תוכנה"),   # Software Tech
    (5,  "הייטק-כללי"),    # General Tech
    (28, "אינטרנט"),        # Internet / Web
    (30, "אבטחת מידע"),     # Cyber Security
    (4,  "הייטק-חומרה"),   # Hardware Tech
]


class DrushimScraper:
    BASE_URL = "https://www.drushim.co.il"
    API_URL  = "https://www.drushim.co.il/api/jobs/search"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": HEADERS["User-Agent"],
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.drushim.co.il/",
            "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8",
        })

    def scrape(self, max_pages: int = 3) -> list:
        all_jobs = []
        for catdir, cat_name in DRUSHIM_CATEGORIES:
            jobs = self._scrape_category(catdir, cat_name, max_pages)
            all_jobs.extend(jobs)
            print(f"[Drushim] cat{catdir} ({cat_name}) → {len(jobs)} jobs")
        return all_jobs

    def _scrape_category(self, catdir: int, cat_name: str, max_pages: int) -> list:
        jobs = []
        for page in range(1, max_pages + 1):
            try:
                resp = self.session.get(
                    self.API_URL,
                    params={"catdir": catdir, "page": page},
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()
                result_list = data.get("ResultList", [])
                if not result_list:
                    break
                for item in result_list:
                    job = self._parse_job(item, cat_name)
                    if job:
                        jobs.append(job)
                time.sleep(random.uniform(1.0, 2.0))
            except Exception as e:
                print(f"[Drushim] cat{catdir} p{page} error: {e}")
                break
        return jobs

    def _parse_job(self, item: dict, search_query: str = "") -> dict:
        try:
            code = str(item.get("Code", ""))
            content = item.get("JobContent", {})
            info = item.get("JobInfo", {})
            company_data = item.get("Company", {})

            title = content.get("Name", "").strip()
            link = info.get("Link", "")
            # Skip metadata rows (no actual job path) and very short/invalid titles
            if not title or len(title) < 3 or not link or not re.search(r"/job/\d+", link):
                return None

            company = company_data.get("CompanyDisplayName", "Unknown") or "Unknown"

            # Location: prefer Addresses (exact office) over Regions
            addresses = content.get("Addresses", [])
            if addresses:
                addr = addresses[0]
                city_he = addr.get("City", "")
                city_en = addr.get("CityEnglish", "")
                lat = addr.get("Latitude")
                lng = addr.get("Longitude")
                location_text = city_he or city_en
                geo = geocode_location(city_he or city_en)
                city = geo["city"]
                if lat is None:
                    lat = geo["lat"]
                if lng is None:
                    lng = geo["lng"]
            else:
                regions = content.get("Regions", [])
                location_text = regions[0].get("NameInHebrew", "ישראל") if regions else "ישראל"
                geo = geocode_location(location_text)
                city = geo["city"]
                lat = geo["lat"]
                lng = geo["lng"]

            # Description (strip HTML tags)
            desc = re.sub(r"<[^>]+>", " ", content.get("Description", "") or "").strip()
            req  = re.sub(r"<[^>]+>", " ", content.get("Requirements", "") or "").strip()
            full_text = (desc + " " + req).strip()[:500]

            # Salary
            sal_text = content.get("SalaryRangeText") or ""
            sal_num  = content.get("Salary", 0) or 0
            sal_min, sal_max = parse_salary(sal_text)
            if sal_min is None and sal_num:
                sal_min = sal_max = int(sal_num)

            # Experience
            exp_data   = content.get("Experience") or {}
            exp_hebrew = exp_data.get("NameInHebrew", "") if exp_data else ""
            experience = _map_drushim_experience(exp_hebrew, full_text)

            # URL
            link = info.get("Link", "")
            url  = self.BASE_URL + link if link else ""

            return {
                "id":            make_job_id("drushim", code),
                "source":        "drushim",
                "title":         title,
                "company":       company,
                "location_text": location_text,
                "city":          city,
                "lat":           lat,
                "lng":           lng,
                "work_model":    detect_work_model(full_text + " " + title),
                "experience":    experience,
                "category":      detect_category(title, full_text),
                "salary_min":    sal_min,
                "salary_max":    sal_max,
                "description":   full_text,
                "url":           url,
                "posted_at":     info.get("Date", ""),
                "scraped_at":    datetime.utcnow().isoformat(),
                "search_query":  search_query,
            }
        except Exception as e:
            print(f"[Drushim] parse error: {e}")
            return None


# ─────────────────────────────────────────────
# GotFriends Scraper  (HTML)
# ─────────────────────────────────────────────

class GotFriendsScraper:
    BASE_URL   = "https://www.gotfriends.co.il"
    # Software category has ~11k tech jobs vs the general /jobs/ listing
    JOBS_URL   = "https://www.gotfriends.co.il/jobslobby/software/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        try:
            self.session.get(self.BASE_URL, timeout=10)
        except Exception:
            pass

    def scrape(self, max_pages: int = 30) -> list:
        all_jobs = []
        for page in range(1, max_pages + 1):
            try:
                resp = self.session.get(self.JOBS_URL, params={"page": page}, timeout=20)
                resp.raise_for_status()
                jobs = self._parse(resp.text)
                if not jobs:
                    break
                all_jobs.extend(jobs)
                print(f"[GotFriends] p{page} → {len(jobs)} jobs")
                time.sleep(random.uniform(1.0, 2.0))
            except Exception as e:
                print(f"[GotFriends] p{page} error: {e}")
                break
        return all_jobs

    def _parse(self, html: str) -> list:
        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("div.item")
        return [j for card in cards for j in [self._extract(card)] if j]

    def _extract(self, card):
        try:
            title_el = card.select_one("h2.title") or card.select_one("a.position h2")
            if not title_el:
                return None
            title = title_el.get_text(strip=True)
            if not title or len(title) < 3:
                return None

            link_el = card.select_one("a.position")
            href = link_el["href"] if link_el and link_el.get("href") else ""
            url = href if href.startswith("http") else self.BASE_URL + href

            # Location: first span.info-data inside section.info.meta
            loc_el = card.select_one("section.info span.info-data")
            location_text = loc_el.get_text(strip=True) if loc_el else "Israel"
            # Clean up abbreviated city names (e.g. ת"א → תל אביב)
            if 'ת"א' in location_text or "תל אביב" in location_text or "המרכז" in location_text:
                location_text = "תל אביב"

            geo = geocode_location(location_text)
            full_text = card.get_text(" ", strip=True)
            sal_min, sal_max = parse_salary(full_text)

            return {
                "id":            make_job_id("gotfriends", url),
                "source":        "gotfriends",
                "title":         title,
                "company":       "GotFriends",
                "location_text": location_text,
                "city":          geo["city"],
                "lat":           geo["lat"],
                "lng":           geo["lng"],
                "work_model":    detect_work_model(full_text + " " + title),
                "experience":    detect_experience(title + " " + full_text),
                "category":      detect_category(title, full_text),
                "salary_min":    sal_min,
                "salary_max":    sal_max,
                "description":   full_text[:500],
                "url":           url,
                "posted_at":     datetime.utcnow().isoformat(),
                "scraped_at":    datetime.utcnow().isoformat(),
                "search_query":  "tech",
            }
        except Exception as e:
            print(f"[GotFriends] extract error: {e}")
            return None


# ─────────────────────────────────────────────
# Greenhouse Scraper  (public ATS JSON API)
# Confirmed working for these Israeli companies:
# Taboola, NICE, SimilarWeb, Payoneer, Optimove, Riskified, Lightricks
# ─────────────────────────────────────────────

class GreenhouseScraper:
    API_BASE = "https://boards-api.greenhouse.io/v1/boards"

    COMPANIES = [
        # Confirmed working boards — Israeli tech companies
        ("taboola",     "Taboola"),
        ("nice",        "NICE Systems"),
        ("similarweb",  "SimilarWeb"),
        ("payoneer",    "Payoneer"),
        ("optimove",    "Optimove"),
        ("riskified",   "Riskified"),
        ("lightricks",  "Lightricks"),
        ("appsflyer",   "AppsFlyer"),
        ("orcasecurity","Orca Security"),
        ("claroty",     "Claroty"),
        ("armis",       "Armis"),
        ("axonius",     "Axonius"),
        ("cybereason",  "Cybereason"),
        ("earnix",      "Earnix"),
        ("melio",       "Melio"),
        ("sisense",     "Sisense"),
        ("firebolt",    "Firebolt"),
        ("sygnia",      "Sygnia"),
    ]

    # Exact phrases that confirm an Israeli location
    ISRAEL_PHRASES = [
        "israel", "tel aviv", "תל אביב", "herzliya", "הרצליה",
        "ra'anana", "raanana", "רעננה", "petah tikva", "פתח תקווה",
        "haifa", "חיפה", "jerusalem", "ירושלים",
        "beer sheva", "באר שבע", "beersheba", "rishon lezion",
        "netanya", "נתניה", "rosh haayin", "kfar saba",
        "ramat gan", "רמת גן", "modiin", "rehovot", "holon",
        "remote, israel", "israel - remote", "remote - israel",
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": HEADERS["User-Agent"],
            "Accept": "application/json",
        })

    def scrape(self) -> list:
        all_jobs = []
        for slug, company_name in self.COMPANIES:
            try:
                jobs = self._fetch_company(slug, company_name)
                all_jobs.extend(jobs)
                print(f"[Greenhouse] {company_name} → {len(jobs)} IL jobs")
                time.sleep(random.uniform(0.5, 1.0))
            except Exception as e:
                print(f"[Greenhouse] {company_name} error: {e}")
        return all_jobs

    def _fetch_company(self, slug: str, company_name: str) -> list:
        resp = self.session.get(f"{self.API_BASE}/{slug}/jobs", timeout=15)
        resp.raise_for_status()
        jobs_raw = resp.json().get("jobs", [])
        return [j for raw in jobs_raw for j in [self._parse(raw, company_name)] if j]

    def _is_israel(self, location: str) -> bool:
        loc = location.lower()
        return any(phrase in loc for phrase in self.ISRAEL_PHRASES)

    def _parse(self, job: dict, company_name: str):
        try:
            title = (job.get("title") or "").strip()
            if not title:
                return None

            location_name = (job.get("location") or {}).get("name") or "Israel"
            if not self._is_israel(location_name):
                return None

            geo = geocode_location(location_name)
            url = job.get("absolute_url") or ""
            job_id = str(job.get("id") or url)
            posted_at = job.get("updated_at") or job.get("first_published") or ""

            return {
                "id":            make_job_id("greenhouse", job_id),
                "source":        "greenhouse",
                "title":         title,
                "company":       company_name,
                "location_text": location_name,
                "city":          geo["city"],
                "lat":           geo["lat"],
                "lng":           geo["lng"],
                "work_model":    detect_work_model(title + " " + location_name),
                "experience":    detect_experience(title),
                "category":      detect_category(title),
                "salary_min":    None,
                "salary_max":    None,
                "description":   "",
                "url":           url,
                "posted_at":     posted_at,
                "scraped_at":    datetime.utcnow().isoformat(),
                "search_query":  company_name,
            }
        except Exception as e:
            print(f"[Greenhouse] parse error: {e}")
            return None


# ─────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────

DEFAULT_QUERIES = [
    "Product Manager",
    "Software Engineer",
    "QA Automation",
    "DevOps",
    "Full Stack",
    "Data Engineer",
    "מנהל מוצר",
    "מפתח תוכנה",
]


def run_scrape(queries: list = None) -> dict:
    from database import insert_jobs
    queries = queries or DEFAULT_QUERIES
    all_jobs = []

    # AllJobs: keyword-based scraping
    alljobs = AllJobsScraper()
    for q in queries:
        try:
            all_jobs.extend(alljobs.search(q, max_pages=2))
        except Exception as e:
            print(f"[AllJobs] Error on '{q}': {e}")

    # Drushim: category-based JSON API (no queries needed)
    try:
        drushim = DrushimScraper()
        all_jobs.extend(drushim.scrape(max_pages=3))
    except Exception as e:
        print(f"[Drushim] Error: {e}")

    # GotFriends: HTML scraping (software category, ~11k tech jobs)
    try:
        gotfriends = GotFriendsScraper()
        all_jobs.extend(gotfriends.scrape(max_pages=30))
    except Exception as e:
        print(f"[GotFriends] Error: {e}")

    # Greenhouse: public ATS API for Israeli tech companies
    try:
        greenhouse = GreenhouseScraper()
        all_jobs.extend(greenhouse.scrape())
    except Exception as e:
        print(f"[Greenhouse] Error: {e}")

    inserted = insert_jobs(all_jobs)
    print(f"[Scraper] Done — {len(all_jobs)} scraped, {inserted} inserted/updated")
    return {"total_scraped": len(all_jobs), "inserted": inserted}
