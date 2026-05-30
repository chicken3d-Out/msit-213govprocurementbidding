# Public Sector Procurement & Bidding Platform

A secure Django platform where government agencies post procurement needs and verified vendors submit blind bids.

## Features
- Blind bidding (bids sealed until reveal date)
- NIST-aligned audit logging of all admin actions
- REST API for external transparency portals (masked losing bidder info)
- Mine/All toggle for vendors
- Custom template tags for currency formatting and countdown timers

## Setup (local)
```bash
pip install -r requirements/dev.txt
cp .env.example .env  # fill in values
python manage.py migrate --settings=settings.dev
python manage.py createsuperuser --settings=settings.dev
python manage.py runserver --settings=settings.dev
```

## Deployment (Railway/Render)
Set environment variables:
- `SECRET_KEY`
- `DJANGO_SETTINGS_MODULE=settings.prod`
- `ALLOWED_HOSTS=yourdomain.com`
- `DATABASE_URL=postgres://...`

## Admin credentials (grading)
- Username: `admin`
- Password: set via `createsuperuser`

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/contracts/` | Awarded contracts (public) |
| GET | `/api/v1/contracts/<id>/` | Contract detail |
| GET | `/api/v1/procurements/` | Public procurement listings |

## Audit log location
`logs/audit.log` — tracks bid opens, submissions, contract awards, admin actions.
