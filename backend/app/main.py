from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.models  # noqa: F401  (registra modelos)
    import sqlalchemy as sa
    from app.db.seed import crear_tablas

    crear_tablas(engine)
    yield


app = FastAPI(
    title="AutoGest API — Minería de Datos (UNIMINUTO Ibagué)",
    version="0.1.0",
    description=(
        "Backend de AutoGest: módulos operativos del taller (RF-01..05), "
        "reglas IQR por tipo de servicio, clima NOAA/open-meteo, grúa (MAR No aplica), "
        "IA preventiva, QR público y cruce con accidentes/tráfico (datos.gov.co)."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["health"])
def health():
    return {
        "app": "AutoGest API",
        "status": "ok",
        "docs": "/docs",
        "seed": "backend/app/db/seed.py --reset",
    }

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}