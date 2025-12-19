# Karigar Backend

Hyperlocal Services Marketplace Backend built with FastAPI, PostgreSQL, and AI Agents.

## Features

- **Authentication & Authorization**: JWT-based auth with refresh tokens
- **AI-Powered Matching**: Intelligent provider matching using OpenAI
- **Smart Scheduling**: Optimal time slot suggestions
- **Dynamic Pricing**: AI-driven pricing recommendations
- **Review Analysis**: Sentiment analysis and fake review detection
- **Personalized Recommendations**: User-based provider recommendations
- **Geospatial Search**: Location-based provider discovery using PostGIS
- **Real-time Notifications**: In-app notification system
- **Redis Caching**: Performance optimization with Redis

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: Neon PostgreSQL with PostGIS
- **Cache**: Redis
- **AI**: OpenAI GPT-4o-mini/GPT-4o
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `OPENAI_API_KEY`: OpenAI API key
- `REDIS_URL`: Redis connection string
- `GOOGLE_MAPS_API_KEY`: Google Maps API key (optional)

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── main.py                 # FastAPI app
├── core/                   # Core utilities
│   ├── config.py          # Configuration
│   ├── security/          # JWT, password hashing
│   ├── agent_communication/  # Agent hub
│   ├── parallel/          # Parallel execution
│   ├── retry/             # Retry logic
│   └── prompt_cache/       # Prompt caching
├── db/                     # Database
│   ├── client.py          # DB connection
│   └── models.py          # SQLAlchemy models
├── domain/                 # Pydantic models
│   └── models.py
├── agents/                 # AI agents
│   ├── base.py
│   ├── matching_agent.py
│   ├── scheduling_agent.py
│   ├── pricing_agent.py
│   ├── review_agent.py
│   └── recommendation_agent.py
├── services/               # Business logic
│   ├── matching.py
│   ├── scheduling.py
│   ├── pricing.py
│   └── recommendations.py
├── api/                    # API endpoints
│   ├── auth.py
│   └── bookings.py
└── utils/                  # Utilities
    ├── geolocation.py
    ├── distance.py
    └── notifications.py
```

## Key Endpoints

### Authentication
- `POST /api/v1/auth/register/customer` - Register customer
- `POST /api/v1/auth/register/provider` - Register provider
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Bookings
- `POST /api/v1/bookings/request` - Create booking request
- `GET /api/v1/bookings/{id}` - Get booking details
- `PATCH /api/v1/bookings/{id}/accept` - Accept booking
- `PATCH /api/v1/bookings/{id}/reject` - Reject booking

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

## Production Deployment

See production guidelines in the main project documentation for:
- Security best practices
- Performance optimization
- Monitoring and logging
- Scaling strategies

## License

Proprietary - Karigar Team

