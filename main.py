import os
from dotenv import load_dotenv

import uvicorn
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from src.routes import contacts, auth

load_dotenv()
app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    redis_base = await redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=6379,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis_base)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
