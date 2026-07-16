# ARGUS Frontend

Landing page for the ARGUS Industrial Safety Intelligence Platform.

## Development

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Backend integration

The landing page proxies API requests through `/api/backend/*` to the FastAPI backend (default `http://localhost:8000`).

Start the backend stack first:

```bash
cd ../backend
docker compose up -d
```

Live data appears in:

- **Reliability** — `/health`, `/readiness`
- **Risk Engine** — `/risk/current`
- **Geo Intelligence** — `/geo/layout`

When the backend is unavailable, sections fall back to sample data with a **Sample data** badge.

## Environment

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_SITE_URL` | Canonical site URL for SEO |
| `NEXT_PUBLIC_API_BASE_URL` | Browser API base (default `/api/backend`) |
| `API_BASE_URL` | Server-side proxy target |

## Scripts

- `npm run dev` — development server
- `npm run build` — production build
- `npm run start` — production server
- `npm run lint` — ESLint
