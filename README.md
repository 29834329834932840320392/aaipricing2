# Ancira Competitive Intelligence Dashboard

Production-grade web application for competitive pricing and inventory analysis across Ancira Auto Group dealerships.

## Overview

This system scrapes new car inventory from Ancira dealerships and their competitors, then provides a clean comparison dashboard. Built with a **platform-based scraping architecture** - scrapers are organized by website platform (Dealer Inspire, DealerOn, etc.) rather than individual dealers.

## Architecture

### Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Queue**: Celery + Redis (for background scraping)
- **Scraping**: Playwright (headless Chromium)
- **AI**: OpenAI GPT-5.4-mini for intelligent data extraction
- **Frontend**: React + Vite + Tailwind CSS (to be implemented)
- **Deployment**: Ubuntu VPS + NGINX + systemd

### Key Design Decisions

1. **Platform-Based Scrapers**: Each website platform (e.g., "Dealer Inspire") has its own scraper module. Adding support for a new platform = adding a new module, not modifying core logic.

2. **Stateless JWT Auth**: Fast, scalable authentication with access tokens (30 min) and refresh tokens (7 days).

3. **Encrypted Secrets**: OpenAI API keys encrypted at rest using Fernet (AES-128).

4. **Fuzzy Matching**: Vehicle comparison uses tight (90%+) similarity matching on Year/Make/Model/Trim.

5. **Fresh Data Only**: Dashboard displays vehicles scraped within the last 24 hours by default (configurable).

## Project Structure

```
aaipricing2/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── api/             # FastAPI route modules
│   │   ├── auth/            # Authentication & encryption
│   │   ├── scrapers/        # Platform-specific scrapers (TODO)
│   │   ├── tasks/           # Celery background tasks (TODO)
│   │   ├── utils/           # Utilities
│   │   ├── config.py        # Application settings
│   │   ├── database.py      # Database connection
│   │   └── main.py          # FastAPI application
│   ├── alembic/             # Database migrations
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # React app (TODO)
├── nginx/                   # NGINX config (TODO)
├── systemd/                 # Systemd service files (TODO)
└── docs/                    # Documentation
```

## Database Schema

### Core Models

- **User**: Authentication (username/password + WebAuthn support)
- **SystemSettings**: Global settings (OpenAI API key, model selection)
- **WebsitePlatform**: Dealer website platforms (Dealer Inspire, DealerOn, etc.)
- **Dealer**: Ancira dealerships
- **Competitor**: Competitor dealerships (up to 5 per Ancira dealer)
- **Vehicle**: Scraped inventory data
- **ScrapeJob**: Background scraping job tracking

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (for frontend)

### Backend Setup

1. **Clone repository**
   ```bash
   cd /path/to/project
   ```

2. **Create virtual environment**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and secrets
   ```

   **Generate encryption key**:
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   # Copy this value to ENCRYPTION_KEY in .env
   ```

6. **Create database**
   ```bash
   createdb ancira_intel
   ```

7. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

8. **Start development server**
   ```bash
   python app/main.py
   # Or with uvicorn:
   uvicorn app.main:app --reload --port 8000
   ```

9. **Access API docs**
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Initial Login

On first startup, an admin user is created:
- **Username**: `admin` (configurable in .env)
- **Password**: `ChangeMe123!` (configurable in .env)

**⚠️ Change this immediately in production!**

## API Overview

### Authentication
- `POST /api/auth/login` - User login (returns JWT)
- `POST /api/auth/logout` - User logout

### Admin Panel
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create user
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/settings` - Get system settings
- `PUT /api/admin/settings` - Update settings (OpenAI key/model)

### Website Platforms
- `GET /api/platforms` - List platforms
- `POST /api/platforms` - Create platform (admin only)
- `DELETE /api/platforms/{id}` - Delete platform (admin only)

### Dealers & Competitors
- `GET /api/dealers` - List Ancira dealers
- `POST /api/dealers` - Create dealer (admin only)
- `GET /api/dealers/{id}` - Get dealer details
- `PUT /api/dealers/{id}` - Update dealer (admin only)
- `DELETE /api/dealers/{id}` - Delete dealer (admin only)
- `POST /api/dealers/{id}/competitors` - Add competitor (admin only, max 5)
- `DELETE /api/dealers/competitors/{id}` - Remove competitor (admin only)

### Vehicles (Dashboard)
- `GET /api/vehicles/dealer/{id}` - Get dealer vehicles (fresh data)
- `GET /api/vehicles/competitor/{id}` - Get competitor vehicles
- `GET /api/vehicles/stats/dealer/{id}` - Get dealer stats

### Scraping
- `POST /api/scrape/dealer/{id}` - Trigger scrape for dealer + competitors
- `GET /api/scrape/status/{job_id}` - Get scrape job status
- `GET /api/scrape/dealer/{id}/recent` - Get recent scrape jobs

## User Roles

### Admin
- Full access to all features
- User management
- System settings (API keys, models)
- Platform management
- Dealer/competitor configuration

### User
- View dashboards
- Trigger data refreshes
- Cannot modify system configuration
- Can reset own password

## Next Steps (TODO)

### Phase 1: Scraping Infrastructure (IN PROGRESS)
- [ ] Implement base scraper class
- [ ] Build platform router
- [ ] Create Dealer Inspire scraper
- [ ] Integrate OpenAI for data extraction
- [ ] Set up Celery workers
- [ ] Add WebSocket/SSE for real-time progress updates

### Phase 2: Frontend
- [ ] React app scaffold
- [ ] Authentication UI (login, password reset)
- [ ] Admin panel (user mgmt, settings, platforms, dealers)
- [ ] Dashboard (vehicle comparison with fuzzy matching)
- [ ] Real-time scrape progress UI

### Phase 3: Production Deployment
- [ ] NGINX configuration
- [ ] Systemd service files
- [ ] Let's Encrypt SSL setup
- [ ] Log rotation
- [ ] Monitoring (uptime, error tracking)

### Phase 4: Enhancements
- [ ] WebAuthn/Passkey support
- [ ] Additional platform scrapers (DealerOn, Dealer.com, etc.)
- [ ] Historical price tracking
- [ ] Email notifications
- [ ] Scheduled auto-refresh (cron)
- [ ] Remove 10-VDP test limit

## Development Notes

### Database Migrations

**Create a new migration**:
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations**:
```bash
alembic upgrade head
```

**Rollback one migration**:
```bash
alembic downgrade -1
```

### Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
black app/

# Lint code
ruff check app/
```

## Scraping Architecture

### Platform-Based Design

Scrapers are organized by **website platform**, not individual dealers. This makes the system scalable:

1. Identify dealer's platform (stored in `Dealer.platform_id`)
2. Route to appropriate platform scraper
3. Platform scraper handles sitemap parsing + VDP extraction
4. OpenAI assists with data extraction from HTML

### Adding a New Platform

See `docs/PLATFORMS.md` (to be created) for detailed instructions.

### 10-VDP Test Limit

**TEMPORARY TESTING LIMIT**: Currently capped at 10 VDPs per dealer per scrape.

To remove for production:
1. Set `SCRAPE_VDP_LIMIT=10000` in `.env` (or higher)
2. Search codebase for `TODO: Remove 10-VDP limit` comments

## Security

- **Secrets**: All secrets in environment variables, never hardcoded
- **API Keys**: Encrypted at rest with Fernet (AES-128)
- **Passwords**: Hashed with bcrypt (cost factor 12)
- **JWT**: HS256 algorithm, 30-min expiration
- **HTTPS**: Required in production (NGINX + Let's Encrypt)
- **Rate Limiting**: Implement on login endpoint (TODO)

## License

Proprietary - Ancira Auto Group

## Support

For issues or questions, contact the development team.

---

**Status**: 🟡 Backend foundation complete. Scraping infrastructure and frontend in progress.
