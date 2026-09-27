"""
FastAPI application entrypoint. Wires up routers, CORS, and the MQTT
background listener via lifespan hooks.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, users, routes, vehicles
from app.mqtt.client import mqtt_ingestor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MQTT ingestor...")
    mqtt_ingestor.start()
    yield
    logger.info("Stopping MQTT ingestor...")
    mqtt_ingestor.stop()


app = FastAPI(
    title="GPS Vehicle Tracking API",
    description="Backend for the GPS-based vehicle tracking assessment project.",
    version="1.0.0",
    lifespan=lifespan,
)

# In production, restrict this to the Flutter app's actual origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(routes.router)
app.include_router(vehicles.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "gps-vehicle-tracking-api"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
