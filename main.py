from dotenv import load_dotenv

import uvicorn
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware

from src.routes import contacts, auth, users
from src.conf.config import settings

load_dotenv()
app = FastAPI()

ORIGINS = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")


async def startup_event():
    """
    This function is called during the startup of the FastAPI application. It creates a Redis connection using the settings from the application configuration, and then initializes the FastAPILimiter with the Redis connection.

    The FastAPILimiter is used to implement rate limiting for the API endpoints, to prevent abuse and ensure fair usage of the application.
    """
    redis_base = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        # password=settings.redis_password,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis_base)


app.add_event_handler("startup", startup_event)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
