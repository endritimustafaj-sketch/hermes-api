"""
SQLAlchemy engine + session factory për Hermes API.

Përdorimi te routers/services:
    from database.connection import get_db
    from fastapi import Depends
    from sqlalchemy.orm import Session

    @router.get("/blerese/{id}")
    def merr_bleresin(id: int, db: Session = Depends(get_db)):
        return db.query(Blerese).filter(Blerese.id == id).first()

Konfigurimi DATABASE_URL kontrollohet te core/config.py.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

from core.config import settings


# ============ Konfigurimi i engine-it ============
# SQLite kërkon connect_args të veçanta për të punuar me FastAPI multithread.
# MySQL/PostgreSQL nuk kanë nevojë për këtë argument.
_connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    echo=settings.DEBUG,         # logon çdo SQL që ekzekutohet kur DEBUG=True
    pool_pre_ping=True,          # verifikon lidhjen para çdo query (rezistencë ndaj timeout)
)


# ============ Aktivizimi i FK constraints për SQLite ============
# SQLite ka FK constraints të çaktivizuara nga default. Pa këtë event,
# DDL-ja jonë do të krijohej por FK-të nuk do të zbatoheshin në runtime.
if settings.DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _aktivizo_fk_per_sqlite(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()


# ============ Session factory ============
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class që do trashëgohet nga të gjitha modelet ORM (te Hapi 5)
Base = declarative_base()


# ============ Dependency për FastAPI ============
def get_db():
    """
    Hap një sesion DB për çdo request HTTP, e mbyll automatikisht në fund
    (edhe nëse ndodh ndonjë gabim brenda endpoint-it).

    Përdorimi:
        @router.get("/...")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
