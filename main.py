"""
Hermes Marketplace API — pika e hyrjes.

Niset me:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Pasi serveri është aktiv:
    http://localhost:8000/        → informacion bazë
    http://localhost:8000/docs    → Swagger UI (dokumentim interaktiv)
    http://localhost:8000/redoc   → ReDoc (dokumentim alternativ)
    http://localhost:8000/health  → health check
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.exceptions import AutoServisException, autoservis_exception_handler


# ============ Lifecycle (startup / shutdown) ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ekzekutohet një herë në startup dhe një herë në shutdown.

    Në hapat e ardhshëm (Hapi 5), këtu do shtohet:
        from database.connection import engine, Base
        from database import models  # importon të gjitha modelet ORM
        Base.metadata.create_all(bind=engine)
    """
    print(f"┌─────────────────────────────────────────────────┐")
    print(f"│  {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"│  DB:    {settings.DATABASE_URL}")
    print(f"│  Docs:  http://localhost:8000/docs")
    print(f"│  DEBUG: {settings.DEBUG}")
    print(f"└─────────────────────────────────────────────────┘")
    yield
    print(f"[{settings.APP_NAME}] Mbyllje e pastër.")


# ============ Aplikacioni FastAPI ============
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    # Fsheh seksionin "Schemas" nga Swagger UI (më pak konfuzion për përdoruesin)
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)


# ============ Middleware ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Exception handlers ============
app.add_exception_handler(AutoServisException, autoservis_exception_handler)


# ============ Endpoints bazë ============
@app.get("/", tags=["Sistemi"])
def rrenja():
    """
    Endpoint i thjeshtë rrënjë. Konfirmon që servisi është aktiv dhe
    kthen informacion bazë + linkun e dokumentimit.
    """
    return {
        "aplikacioni": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "pershkrimi": settings.APP_DESCRIPTION,
        "dokumentimi_interaktiv": "/docs",
        "dokumentimi_alternativ": "/redoc",
        "health_check": "/health",
        "status": "aktiv",
    }


@app.get("/health", tags=["Sistemi"])
def shendeti():
    """
    Health check endpoint. Përdoret nga sistemet monitoruese (p.sh. Uptime Kuma)
    për të verifikuar që servisi po përgjigjet.
    """
    return {"status": "ok"}


@app.get("/version", tags=["Sistemi"])
def versioni():
    """
    Kthen versionin aktual të API-së plus veçoritë kryesore.
    Përdore për të verifikuar shpejt cilin version po xhiron.
    """
    return {
        "version": settings.APP_VERSION,
        "vecorite_e_kerkimit": {
            "normalizim_diakritikesh": True,
            "multi_fjale_and": True,
            "mbaresa_shqipe": True,
            "tolerance_gabimesh": True,
            "fushat_e_kerkueshme": [
                "kodi_oem", "emri", "pershkrimi",
                "model_kompatibil", "kategori", "marka"
            ],
        },
        "endpoints_publike": [
            "GET /api/v1/public/kerko-pjese?q=...&limit=N",
            "GET /api/v1/public/oferta-pjeses/{kodi_oem}",
            "POST /api/v1/public/kosto-transporti",
            "POST /api/v1/public/llogarit-fature",
        ],
    }


# ============ Routers ============
from routers import webservice_publik  # noqa: E402

app.include_router(webservice_publik.router, prefix=settings.API_V1_PREFIX)

# Routers shtesë (do shtohen në hapat e ardhshëm):
# Hapi 8 (kërkim ofertash): tashmë te webservice_publik.router
# Hapi 11 (regjistrim blerësish/shitësish): from routers import llogarite_router
# Hapi 12 (CRUD listimet): from routers import listimet_router
# Hapi 13 (faturat me persistim): from routers import faturat_router
