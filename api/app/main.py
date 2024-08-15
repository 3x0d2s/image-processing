from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.redis_client import redis_client
from app.views import router as views_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_client.close_connection()


app = FastAPI(lifespan=lifespan)

app.include_router(views_router, prefix='/api')
