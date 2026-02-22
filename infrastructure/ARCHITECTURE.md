# DessertAble Infrastructure Overview

**Document Created:** 2026-01-24
**Last Updated:** 2026-01-24

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Browser   │  │   Mobile    │  │   Desktop   │  │    Curl/    │        │
│  │   (Chrome,  │  │   Browser   │  │   Browser   │  │    API      │        │
│  │   Firefox)  │  │  (Safari)   │  │   (Edge)    │  │   Client    │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                    │
                                    ▼ HTTP/HTTPS
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION LAYER                                  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         Flask Application                              │  │
│  │                      (Application Factory Pattern)                     │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │                      main_bp (Blueprint)                         │  │  │
│  │  │                                                                  │  │  │
│  │  │  Routes: / | /search | /login | /register | /logout             │  │  │
│  │  │          /favorites | /favorites/add | /favorites/remove        │  │  │
│  │  │          /history | /admin                                      │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                        │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │  │
│  │  │   Flask-Login   │  │ Jinja2 Templates│  │  Static Files   │       │  │
│  │  │  (Auth Manager) │  │   (HTML Views)  │  │   (CSS/JS/IMG)  │       │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SERVICE LAYER                                     │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      RestaurantService                                 │  │
│  │  • Core business logic & orchestration                                │  │
│  │  • Composite scoring algorithm (60% base, 15% cuisine,                │  │
│  │    20% newness, 5% proximity)                                         │  │
│  │  • Progressive filter relaxation (5 passes)                           │  │
│  └──────────────────────────────┬────────────────────────────────────────┘  │
│                                 │                                            │
│         ┌───────────────────────┼───────────────────────┐                   │
│         │                       │                       │                   │
│         ▼                       ▼                       ▼                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   PlacesAPI     │    │ DeepSeekService │    │    Database     │         │
│  │                 │    │                 │    │                 │         │
│  │ • Geocoding     │    │ • AI-powered    │    │ • User CRUD     │         │
│  │ • Nearby search │    │   descriptions  │    │ • Search history│         │
│  │ • Place details │    │ • Review        │    │ • Favorites     │         │
│  │ • Distance calc │    │   summarization │    │ • Restaurant    │         │
│  │ • 60s caching   │    │ • Graceful      │    │   caching       │         │
│  │                 │    │   degradation   │    │                 │         │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘         │
│           │                      │                      │                   │
└───────────┼──────────────────────┼──────────────────────┼───────────────────┘
            │                      │                      │
            ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SERVICES                                  │
│                                                                              │
│  ┌─────────────────────────┐    ┌─────────────────────────┐                 │
│  │   Google Places API     │    │      DeepSeek API       │                 │
│  │                         │    │                         │                 │
│  │  • Geocoding service    │    │  • LLM text generation  │                 │
│  │  • Places search        │    │  • OpenAI-compatible    │                 │
│  │  • Place details        │    │    endpoint             │                 │
│  │  • Reviews & ratings    │    │  • Optional service     │                 │
│  │                         │    │                         │                 │
│  │  [REQUIRED]             │    │  [OPTIONAL]             │                 │
│  └─────────────────────────┘    └─────────────────────────┘                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                        │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    SQLite Database                                     │  │
│  │                  (data/restaurants.db)                                 │  │
│  │                                                                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │    users     │  │   searches   │  │  restaurants │  │  favorites │ │  │
│  │  │              │  │              │  │              │  │            │ │  │
│  │  │ • id (PK)    │  │ • id (PK)    │  │ • id (PK)    │  │ • id (PK)  │ │  │
│  │  │ • username   │  │ • address    │  │ • place_id   │  │ • user_id  │ │  │
│  │  │ • email      │  │ • latitude   │  │ • name       │  │ • place_id │ │  │
│  │  │ • password   │  │ • longitude  │  │ • rating     │  │ • notes    │ │  │
│  │  │   (hashed)   │  │ • timestamp  │  │ • search_id  │  │ • added_at │ │  │
│  │  │ • created_at │  │ • user_id    │  │ • address    │  │            │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │  │
│  │                                                                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         USER SEARCH REQUEST FLOW                             │
└──────────────────────────────────────────────────────────────────────────────┘

     User                                                           External
    Request                                                          APIs
       │                                                               │
       ▼                                                               │
  ┌─────────┐                                                          │
  │ Browser │                                                          │
  └────┬────┘                                                          │
       │ POST /search                                                  │
       │ {address, sort_by, cuisine}                                   │
       ▼                                                               │
  ┌─────────────────┐                                                  │
  │   Flask Route   │                                                  │
  │  (routes.py)    │                                                  │
  └────────┬────────┘                                                  │
           │                                                           │
           ▼                                                           │
  ┌─────────────────────┐     geocode()      ┌───────────────────┐    │
  │    PlacesAPI        │◄──────────────────►│  Google Maps API  │◄───┤
  │  (places_api.py)    │    search()        │                   │    │
  └─────────┬───────────┘    details()       └───────────────────┘    │
            │                                                          │
            │ raw place data                                           │
            ▼                                                          │
  ┌─────────────────────┐                                              │
  │  RestaurantService  │                                              │
  │ (restaurant_svc.py) │                                              │
  │                     │                                              │
  │ • apply_filters()   │                                              │
  │ • calc_score()      │                                              │
  │ • sort & rank       │                                              │
  └─────────┬───────────┘                                              │
            │                                                          │
            │ top 20 candidates                                        │
            ▼                                                          │
  ┌─────────────────────┐   generate()       ┌───────────────────┐    │
  │  DeepSeekService    │◄──────────────────►│   DeepSeek API    │◄───┘
  │ (deepseek_svc.py)   │   (optional)       │   (LLM Service)   │
  └─────────┬───────────┘                    └───────────────────┘
            │
            │ enriched restaurants
            ▼
  ┌─────────────────────┐
  │     Database        │
  │   (database.py)     │
  │                     │
  │ • save_search()     │
  │ • save_restaurants()│
  └─────────┬───────────┘
            │
            │ top 3 results
            ▼
  ┌─────────────────────┐
  │  Jinja2 Template    │
  │  (results.html)     │
  └─────────┬───────────┘
            │
            │ HTML Response
            ▼
       ┌─────────┐
       │ Browser │
       └─────────┘
```

---

## Component Inventory

### Application Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Application Factory | `app/__init__.py` | Creates Flask app instance with config |
| Routes | `app/routes.py` | HTTP endpoint handlers |
| Database Manager | `app/models/database.py` | SQLite operations |
| User Model | `app/models/user.py` | User authentication entity |
| Restaurant Model | `app/models/restaurant.py` | Restaurant data entity |
| PlacesAPI Service | `app/services/places_api.py` | Google API wrapper |
| DeepSeek Service | `app/services/deepseek_service.py` | AI integration |
| Restaurant Service | `app/services/restaurant_service.py` | Business logic |
| Template Filters | `app/utils/filters.py` | Jinja2 custom filters |

### Configuration

| Environment | Class | Use Case |
|-------------|-------|----------|
| development | `DevelopmentConfig` | Local development with DEBUG=True |
| production | `ProductionConfig` | Deployed application |
| testing | `TestingConfig` | Pytest test runs |

### External Dependencies

| Service | Required | Purpose |
|---------|----------|---------|
| Google Places API | **Yes** | Core search functionality |
| DeepSeek API | No | AI-generated descriptions |

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PRODUCTION DEPLOYMENT                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐     HTTPS      ┌──────────────────────────────────────────────┐
│   Users     │◄──────────────►│           Cloud Platform                      │
└─────────────┘                │  (Render / Railway / Fly.io / AWS)           │
                               │                                               │
                               │  ┌─────────────────────────────────────────┐ │
                               │  │              Gunicorn                    │ │
                               │  │         (WSGI HTTP Server)              │ │
                               │  │          4 worker processes             │ │
                               │  │                                         │ │
                               │  │  ┌───────────────────────────────────┐ │ │
                               │  │  │         Flask Application          │ │ │
                               │  │  │                                    │ │ │
                               │  │  │  ┌──────────┐    ┌─────────────┐  │ │ │
                               │  │  │  │ Services │    │  Database   │  │ │ │
                               │  │  │  └──────────┘    │  (SQLite/   │  │ │ │
                               │  │  │                  │  PostgreSQL)│  │ │ │
                               │  │  │                  └─────────────┘  │ │ │
                               │  │  └───────────────────────────────────┘ │ │
                               │  └─────────────────────────────────────────┘ │
                               │                                               │
                               │  Environment Variables:                       │
                               │  • SECRET_KEY (secure random)                │
                               │  • GOOGLE_PLACES_API_KEY                     │
                               │  • DEEPSEEK_API_KEY (optional)               │
                               │  • FLASK_ENV=production                      │
                               └──────────────────────────────────────────────┘
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SECURITY LAYERS                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ Transport Security                                                           │
│ ├── HTTPS (TLS 1.2+) - Enforced by cloud platform                          │
│ └── HTTP → HTTPS redirect                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Session Security                                                             │
│ ├── SECRET_KEY for session signing                                          │
│ ├── SESSION_COOKIE_HTTPONLY = True (no JS access)                           │
│ ├── SESSION_COOKIE_SAMESITE = 'Lax' (CSRF protection)                       │
│ └── 7-day session lifetime                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Authentication                                                               │
│ ├── Flask-Login session management                                          │
│ ├── Password hashing (PBKDF2 via werkzeug)                                  │
│ └── @login_required decorator on protected routes                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Data Security                                                                │
│ ├── Parameterized SQL queries (no string interpolation)                     │
│ ├── API keys stored in environment variables                                │
│ └── .env files excluded from version control                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack Summary

| Layer | Technology | Version |
|-------|------------|---------|
| Runtime | Python | 3.8+ |
| Web Framework | Flask | 2.x |
| WSGI Server | Gunicorn | 20.x (production) |
| Database | SQLite | 3.x |
| Authentication | Flask-Login | 0.6.x |
| External APIs | Google Places, DeepSeek | v1 |
| Testing | pytest | 7.x |

---

*This document provides a high-level overview of the DessertAble infrastructure. For detailed implementation guidance, refer to [CLAUDE.md](../CLAUDE.md).*
