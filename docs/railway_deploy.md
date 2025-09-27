# Deploying AI Nurse Florence to Railway

This guide aligns the app with Railway's runtime (dynamic `$PORT`) and adds minimal steps to deploy.

## Prereqs
- Railway account and CLI installed
- A Railway project with a PostgreSQL and (optional) Redis plugin set up

## Container image
This repo ships a Dockerfile that:
- Installs dependencies
- Copies the app
- Runs `./run.sh` which binds to `$PORT` (Railway provides this)

No Procfile is required when deploying via Docker.

## Environment variables
Minimum:
- `OPENAI_API_KEY` (optional; app degrades gracefully if absent)
- `DATABASE_URL` (Railway Postgres plugin provides this)
- `REDIS_URL` (optional; fallback cache in-memory)
- `ALLOWED_ORIGINS` (comma-separated, e.g. `https://*.chat.openai.com,https://yourdomain`) 

Recommended flags (match utils/config.py):
- `USE_LIVE_SERVICES=true` for live MyDisease.info / PubMed / ClinicalTrials

Production URL recommendation
- Set `APP_BASE_URL` to your canonical domain so generated links and health responses are correct. Example:
	- `APP_BASE_URL=https://ainurseflorence.com`
- If you prefer the app to construct https URLs from HOST/PORT when `APP_BASE_URL` is not set, set `FORCE_HTTPS=true`.

## Health checks
- Endpoint: `/api/v1/health`
- Expect HTTP 200 JSON with service/route counts

## Steps
1) Push repo to GitHub
2) Create a Railway service from this repo, choose Docker deployment
3) Set env vars under Variables
4) Add Postgres/Redis plugins (optional) and link `DATABASE_URL`/`REDIS_URL`
5) Deploy. Logs should show: `=== AI NURSE FLORENCE STARTUP ===` and `Routers loaded: ...`

## Verify
- Open the Railway-generated URL
- Visit `/docs` for API docs
- Visit `/api/v1/health` to see status

## Notes
- Uvicorn runs via `run.sh` and binds to `$PORT`
- CORS is controlled by `ALLOWED_ORIGINS`
- For ChatGPT Actions, expose `/openapi.json` and allow the Actions domain in CORS
