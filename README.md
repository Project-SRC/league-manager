# League Manager - Project SRC - FastAPI

[![codecov](https://codecov.io/gh/Project-SRC/league-manager/branch/develop/graph/badge.svg)](https://codecov.io/gh/Project-SRC/league-manager)

The League Manager API manages all leagues for the Project SRC stack.

## Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (package manager)
- [Supabase](https://supabase.com/) (local or cloud)

## Tech Stack

| Component    | Technology |
|--------------|------------|
| Framework    | FastAPI    |
| Package Mgr  | uv         |
| Database     | Supabase   |
| Linter       | ruff       |
| Logging      | structlog  |

## Configuration

Configuration is done through environment variables in `.env`:

| Variable                      | Description                                      |
| ----------------------------- | ------------------------------------------------ |
| `MOCK`                        | Run with mocked data (true/false)                |
| `TEST`                        | Run in test mode (true/false)                    |
| `VERSION`                     | API version                                      |
| `SUPABASE_URL`                | Supabase project URL                             |
| `SUPABASE_KEY`                | Supabase anon key                                |
| `SECRET_KEY`                  | JWT encryption key                               |
| `ALGORITHM`                   | JWT algorithm (default: HS256)                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time                            |

### Supabase Setup

1. Create a Supabase project
2. Copy the URL and anon key to `.env`:

   ```bash
   # .env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   ```

For local development with Supabase CLI:

```bash
supabase start
# Use the provided URL (typically http://127.0.0.1:54321)
```

## Installation

```bash
# Install dependencies
uv sync

# Install dev dependencies
uv sync --group dev
```

## Development

### Running the API

```bash
uv run python src/main.py
```

The API will be available at `http://localhost:8000`

### Code Quality

```bash
# Run linter
uv run ruff check src/

# Format code
uv run ruff format src/
```

### Testing

```bash
uv run pytest src/
uv run pytest --cov=src/ src/
```

## Database Schema

```text
user ──────┬── driver
           ├── manager
           └── steward

country ────┬── track
            └── team ─────── contract
                                └── driver

league ─────┼── race ─────── participation
            ├── league_team
            ├── league_driver
            └── league_track
```

### Tables

- `user` - Base user accounts
- `driver` - Driver profiles with stats
- `manager` - Team manager profiles
- `steward` - Race steward profiles
- `country` - Country reference data
- `team` - Racing teams
- `track` - Race tracks/circuits
- `league` - Racing leagues/seasons
- `race` - Race events
- `contract` - Driver-team contracts
- `participation` - Race entries
- `league_team` - Teams in a league
- `league_driver` - Drivers in a league
- `league_track` - Tracks in a league

## Docker

```bash
docker build -t league-manager:latest .
docker run -d --name league-manager --env-file .env league-manager:latest
```
