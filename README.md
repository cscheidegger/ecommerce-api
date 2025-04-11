
# Proteus.lab API

Backend RESTful API for Proteus.lab e-commerce, built with FastAPI.

## Features

- RESTful API endpoints for products, services, orders, quotes, and users
- JWT authentication for secure access
- File upload for 3D models
- Price calculation based on model volume
- PostgreSQL integration
- Automatic API documentation with Swagger UI
- Instagram Integration for portfolio display

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI application initialization
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database connection and session
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── middleware/        # Custom middleware
├── migrations/            # Alembic migration scripts
├── tests/                 # Test suite
├── alembic.ini            # Alembic configuration
├── requirements.txt       # Python dependencies
└── Dockerfile             # Docker configuration
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables (create a .env file):
   ```
   DATABASE_URL=postgresql://user:password@localhost/proteuslab
   SECRET_KEY=your_secret_key
   ```
5. Run the application:
   ```
   uvicorn app.main:app --reload
   ```
6. Access API documentation at http://localhost:8000/docs

### Using Docker

1. Build the Docker image:
   ```
   docker build -t proteuslab-api .
   ```
2. Run the container:
   ```
   docker run -p 8000:8000 --env-file .env proteuslab-api
   ```

## API Endpoints

- GET/POST/PUT/DELETE `/api/products`: Manage 3D model products
- GET/POST/PUT/DELETE `/api/services`: Manage printing services
- GET/POST/PUT/DELETE `/api/orders`: Process customer orders
- GET/POST/PUT/DELETE `/api/quotes`: Handle customized quotes
- GET/POST/PUT/DELETE `/api/users`: Manage user accounts
- GET `/api/instagram/posts`: Retrieve recent Instagram posts for the portfolio

## Instagram API Integration

The backend includes a service to fetch and display posts from the Proteus.lab Instagram account. This integration provides:

1. **Recent Instagram Posts**: Automatically fetches the latest posts from the @proteus.lab Instagram account.
2. **Caching Mechanism**: Uses Redis to cache Instagram data, reducing API calls and improving performance.
3. **Categorization**: Processes and categorizes images by projects or themes.

### Technical Details

- **API Endpoint**: `/api/instagram/posts` - Returns recent posts with metadata
- **Refresh Interval**: Set to 3600 seconds (1 hour) by default
- **Implementation**: Located in the `scripts/instagram-service` directory
- **Communication**: The service runs as a separate container and calls the FastAPI backend

### Instagram Service Configuration

The Instagram service can be configured through environment variables:
```
INSTAGRAM_REFRESH_INTERVAL=3600  # Post refresh interval in seconds
API_URL=http://api:8000/api      # URL of the main API
```

## Authentication

The API uses JWT tokens for authentication. To access protected endpoints:

1. Register a user or login to get a JWT token
2. Include the token in the Authorization header: `Authorization: Bearer {token}`

## Testing

Run tests with pytest:
```
pytest
```

## Database Migrations

Manage database schema with Alembic:
```
alembic revision --autogenerate -m "Description"
alembic upgrade head
```
