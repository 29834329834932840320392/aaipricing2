# End-to-End Testing Guide

Complete walkthrough to test the entire Ancira Intelligence Dashboard stack.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- OpenAI API key

---

## Step 1: Database Setup

### Install PostgreSQL (if not installed)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql@14
brew services start postgresql@14
```

### Create Database
```bash
# Switch to postgres user
sudo -u postgres psql

# In psql:
CREATE DATABASE ancira_intel;
CREATE USER ancira_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ancira_intel TO ancira_user;
\q
```

---

## Step 2: Redis Setup

### Install Redis
```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# macOS
brew install redis
brew services start redis

# Or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Verify Redis is running
```bash
redis-cli ping
# Should return: PONG
```

---

## Step 3: Backend Setup

### Navigate to backend directory
```bash
cd backend
```

### Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Install Playwright browsers
```bash
playwright install chromium
```

### Configure environment
```bash
cp .env.example .env
```

**Edit `.env` with your settings:**
```bash
# Use your favorite editor
nano .env  # or vim, code, etc.
```

**Required changes in `.env`:**
```env
# Database
DATABASE_URL=postgresql://ancira_user:your_secure_password@localhost:5432/ancira_intel

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Security - CHANGE THESE!
SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters-long
ENCRYPTION_KEY=<generate-with-command-below>

# Scraping
SCRAPE_VDP_LIMIT=3  # Keep at 3 for testing

# Admin (will be created on first run)
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=ChangeMe123!
```

**Generate encryption key:**
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy the output to ENCRYPTION_KEY in .env
```

### Run database migrations
```bash
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> <revision>, Initial schema
```

### Start backend server
```bash
# In backend directory
python app/main.py

# Or with uvicorn:
uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify backend is running:**
```bash
# In a new terminal
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

## Step 4: Start Celery Worker

**Open a new terminal**, navigate to backend, activate venv:
```bash
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info
```

Expected output:
```
[tasks]
  . app.tasks.scrape_task.scrape_dealer_task
  . app.tasks.scrape_task.scrape_competitor_task

[2024-XX-XX HH:MM:SS,SSS: INFO/MainProcess] Connected to redis://localhost:6379/0
[2024-XX-XX HH:MM:SS,SSS: INFO/MainProcess] celery@hostname ready.
```

**Keep this terminal open** - you'll see scraping activity here.

---

## Step 5: Frontend Setup

**Open a new terminal:**

### Navigate to frontend directory
```bash
cd frontend
```

### Install dependencies
```bash
npm install
```

Expected: Installation of ~300 packages (takes 1-2 minutes)

### Start development server
```bash
npm run dev
```

Expected output:
```
  VITE v5.1.0  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

**Open browser**: http://localhost:3000

---

## Step 6: Initial Configuration via API

**Open a new terminal** for API calls.

### 1. Login to get JWT token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ChangeMe123!"}'
```

**Copy the `access_token` from the response.** Set it as an environment variable:
```bash
export TOKEN="<paste-your-access-token-here>"
```

### 2. Configure OpenAI API key
```bash
curl -X PUT http://localhost:8000/api/admin/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "openai_api_key": "sk-YOUR-ACTUAL-OPENAI-API-KEY-HERE",
    "openai_model": "gpt-5.4-mini-2026-03-17"
  }'
```

Expected response:
```json
{
  "id": 1,
  "openai_model": "gpt-5.4-mini-2026-03-17",
  "has_api_key": true,
  "updated_at": "2024-..."
}
```

### 3. Create Dealer Inspire platform
```bash
curl -X POST http://localhost:8000/api/platforms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dealer Inspire",
    "description": "Dealer Inspire platform for Ancira Nissan SA"
  }'
```

Expected response:
```json
{
  "id": 1,
  "name": "Dealer Inspire",
  "description": "Dealer Inspire platform for Ancira Nissan SA",
  "created_at": "...",
  "updated_at": "..."
}
```

### 4. Create Ancira Nissan SA dealer
```bash
curl -X POST http://localhost:8000/api/dealers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ancira Nissan SA",
    "url": "https://www.anciranissansa.com/dealer-inspire-inventory/inventory_sitemap",
    "platform_id": 1
  }'
```

Expected response:
```json
{
  "id": 1,
  "name": "Ancira Nissan SA",
  "url": "https://www.anciranissansa.com/dealer-inspire-inventory/inventory_sitemap",
  "platform_id": 1,
  "is_active": true,
  "platform": {...},
  "competitors": [],
  "last_scraped_at": null,
  "created_at": "...",
  "updated_at": "..."
}
```

---

## Step 7: Trigger Your First Scrape! 🚀

### Option A: Via API (see results immediately)
```bash
curl -X POST "http://localhost:8000/api/scrape/dealer/1?include_competitors=false" \
  -H "Authorization: Bearer $TOKEN"
```

You should see a job created:
```json
[
  {
    "id": 1,
    "task_id": "abc123-...",
    "dealer_id": 1,
    "status": "pending",
    "total_vdps": 0,
    "processed_vdps": 0,
    ...
  }
]
```

**Copy the job `id` (probably 1).**

### Monitor scrape progress
```bash
# Check job status (repeat this command every few seconds)
curl http://localhost:8000/api/scrape/status/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Watch the Celery worker terminal** - you'll see:
```
[2024-...] Task app.tasks.scrape_task.scrape_dealer_task[abc-123] received
[2024-...] Starting scrape task for dealer 1, job 1
[2024-...] Fetching Dealer Inspire sitemap: https://www.anciranissansa.com/...
[2024-...] Found 3 new Nissan VDP URLs in sitemap
[2024-...] Scraping Dealer Inspire VDP: https://www.anciranissansa.com/inventory/new-2026-nissan-rogue-...
[2024-...] AI enhanced vehicle: 2026 Nissan Rogue - MSRP: $35000.00, Sale: $33500.00
[2024-...] Scrape task completed for dealer 1: 3 vehicles
```

### View scraped vehicles
```bash
curl http://localhost:8000/api/vehicles/dealer/1 \
  -H "Authorization: Bearer $TOKEN"
```

Expected response:
```json
[
  {
    "id": 1,
    "dealer_id": 1,
    "vin": "5N1BT3AA1TC768626",
    "year": 2026,
    "make": "Nissan",
    "model": "Rogue",
    "trim": "S",
    "msrp": "35000.00",
    "sale_price": "33500.00",
    "vdp_url": "https://www.anciranissansa.com/inventory/new-2026-nissan-rogue-...",
    "scraped_at": "2024-..."
  },
  ...
]
```

### Option B: Via Frontend (visual experience)
*Note: Frontend dashboard is placeholder only - API testing recommended for now.*

---

## Step 8: Verify Everything Works ✅

### Checklist

- [ ] PostgreSQL database created and accessible
- [ ] Redis running and responding to PING
- [ ] Backend API running on http://localhost:8000
- [ ] Backend health endpoint returns `{"status":"healthy"}`
- [ ] Celery worker connected and ready
- [ ] Frontend dev server running on http://localhost:3000
- [ ] Can login with admin/ChangeMe123!
- [ ] OpenAI API key configured (has_api_key: true)
- [ ] Dealer Inspire platform created (id: 1)
- [ ] Ancira Nissan SA dealer created (id: 1)
- [ ] Scrape job triggered successfully
- [ ] Celery worker shows scraping activity
- [ ] Job status changes: pending → running → completed
- [ ] Vehicles API returns 3 scraped vehicles
- [ ] Each vehicle has VIN, year, make, model, trim, MSRP, sale_price

---

## Troubleshooting

### Backend won't start
**Error**: `sqlalchemy.exc.OperationalError: could not connect to server`
- **Fix**: Verify PostgreSQL is running and credentials in `.env` are correct
- Test: `psql -U ancira_user -d ancira_intel -h localhost`

### Celery worker won't connect
**Error**: `Error 111 connecting to localhost:6379. Connection refused`
- **Fix**: Start Redis: `sudo systemctl start redis` or `brew services start redis`
- Test: `redis-cli ping` should return PONG

### Scraping fails with SSL error
**Error**: `certificate is not yet valid` or `403 Forbidden`
- **Fix**: This is normal - Playwright will handle it. If it persists, the site may block scrapers. Try:
  ```bash
  # In .env, set:
  PLAYWRIGHT_HEADLESS=False
  ```
  This runs browser in headed mode (visible) to see what's happening.

### OpenAI extraction fails
**Error**: `AI extraction error: Invalid API key`
- **Fix**: Verify your OpenAI API key is correct and has credits
- Test: `curl https://api.openai.com/v1/models -H "Authorization: Bearer sk-YOUR-KEY"`

### No vehicles found after scrape
**Check Celery worker output for errors**
- Look for "Found X new Nissan VDP URLs in sitemap"
- If X is 0, the sitemap may not have new Nissan vehicles
- Try a different dealer URL

### Frontend can't connect to backend
**Error**: Network error or CORS error
- **Fix**: Verify backend is running on port 8000
- Verify Vite proxy in `frontend/vite.config.js` is correct
- Restart frontend dev server

---

## Success Criteria

You've successfully completed the end-to-end test when:

1. ✅ Backend API is running and healthy
2. ✅ Celery worker is connected and processing tasks
3. ✅ Frontend loads and you can login
4. ✅ OpenAI API key is configured
5. ✅ Dealer Inspire platform exists
6. ✅ Ancira Nissan SA dealer exists
7. ✅ Scrape job completes successfully
8. ✅ **3 vehicles are scraped and stored in database**
9. ✅ **Each vehicle has pricing data (MSRP and Sale Price)**
10. ✅ **VINs are extracted correctly (17 characters)**

---

## What's Next?

Once the end-to-end test passes, we can:

1. **Build Admin Panel** - Full CRUD interfaces for users, settings, platforms, dealers
2. **Build Dashboard** - Vehicle comparison table with fuzzy matching
3. **Add Real-Time Progress** - WebSocket or polling for live scrape updates
4. **Deploy to Production** - NGINX, systemd, SSL setup
5. **Add More Platforms** - DealerOn, Dealer.com, CDK, etc.

---

## Quick Reference Commands

### Start All Services
```bash
# Terminal 1 - PostgreSQL (if not running as service)
sudo systemctl start postgresql

# Terminal 2 - Redis (if not running as service)
sudo systemctl start redis

# Terminal 3 - Backend
cd backend && source venv/bin/activate
python app/main.py

# Terminal 4 - Celery Worker
cd backend && source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 5 - Frontend
cd frontend
npm run dev
```

### Stop All Services
```bash
# Ctrl+C in each terminal, then:
deactivate  # Exit Python venv (in backend terminals)
```

---

**Good luck with your test!** 🚀 Report back with results and any errors you encounter.
