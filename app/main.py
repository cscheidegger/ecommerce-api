
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import settings
from app.routes import products, services, orders, users, auth, instagram
from app.routes.quotes import router as quotes_router

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix=settings.API_V1_STR)
app.include_router(services.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(quotes_router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(instagram.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to the Proteus.lab API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
