"""
SQLAlchemy ORM models për Hermes API.

Çdo klasë këtu korrespondon me një tabelë te DDL (hermes_db.sql).
Modelet japin një API Python të tipuar për pyetje, insert, update, delete —
pa nevojë për SQL të shkruar me dorë.

Shembull përdorimi:
    from database.connection import SessionLocal
    from database.models import Pjese, Listim, Shites

    db = SessionLocal()
    pjesa = db.query(Pjese).filter_by(kodi_oem="BOSCH-0986452060").first()
    for o in sorted(pjesa.listimet, key=lambda x: x.cmimi):
        print(f"{o.shites.emer_kompanie}: {o.cmimi} EUR")
    db.close()
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


# =============================================================================
# 1. LOOKUP TABLES
# =============================================================================

class NivelDiscount(Base):
    """Nivelet e discount-it për blerësit: Welcome, Standard, Silver, Gold, Platinum."""
    __tablename__ = "nivelet_discount"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emer: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    perqindja: Mapped[float] = mapped_column(Float, nullable=False)
    totali_min_blerjeve: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    bleresit: Mapped[list["Blerese"]] = relationship(back_populates="nivel_discount")

    def __repr__(self) -> str:
        return f"<NivelDiscount {self.emer} ({self.perqindja}%)>"


class ZonaTransportit(Base):
    """Zonat e transportit me tarifa fikse + €/km + €/kg (Strukturë A)."""
    __tablename__ = "zonat_transportit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emer: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    distanca_min_km: Mapped[float] = mapped_column(Float, nullable=False)
    distanca_max_km: Mapped[float] = mapped_column(Float, nullable=False)
    tarifa_fikse: Mapped[float] = mapped_column(Float, nullable=False)
    tarifa_per_km: Mapped[float] = mapped_column(Float, nullable=False)
    tarifa_per_kg: Mapped[float] = mapped_column(Float, nullable=False)

    faturat: Mapped[list["Fatura"]] = relationship(back_populates="zona_transportit")

    def __repr__(self) -> str:
        return f"<ZonaTransportit {self.emer} ({self.distanca_min_km}-{self.distanca_max_km}km)>"


class Kategori(Base):
    """Kategoritë e pjesëve (Filtra, Frena, Motor, etj.)."""
    __tablename__ = "kategorite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emer: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    pershkrim: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    pjeset: Mapped[list["Pjese"]] = relationship(back_populates="kategori")

    def __repr__(self) -> str:
        return f"<Kategori {self.emer}>"


class Marka(Base):
    """Marka prodhuesish të pjesëve (Bosch, Mahle, NGK, etj.)."""
    __tablename__ = "markat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emer: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    vendi_origjines: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    pjeset: Mapped[list["Pjese"]] = relationship(back_populates="marka")

    def __repr__(self) -> str:
        return f"<Marka {self.emer}>"


class Magazina(Base):
    """Magazina qendrore i platformës (1 rresht, lat/lng = origjina e dërgesave)."""
    __tablename__ = "magazina"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emer: Mapped[str] = mapped_column(String, nullable=False)
    adresa: Mapped[str] = mapped_column(String, nullable=False)
    qyteti: Mapped[str] = mapped_column(String, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    eshte_aktiv: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:
        return f"<Magazina {self.emer} @ ({self.lat}, {self.lng})>"


# =============================================================================
# 2. LLOGARITË: BLERËSIT + SHITËSIT
# =============================================================================

class Blerese(Base):
    """Llogaritë e blerësve — individë ose biznes me NIPT."""
    __tablename__ = "bleresit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emer: Mapped[str] = mapped_column(String, nullable=False)
    mbiemer: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    fjalekalimi_hash: Mapped[str] = mapped_column(String, nullable=False)
    telefon: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    nipt: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    adresa: Mapped[str] = mapped_column(String, nullable=False)
    qyteti: Mapped[str] = mapped_column(String, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    nivel_discount_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("nivelet_discount.id"), default=1, nullable=False
    )
    totali_blerjeve: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    krijuar_me: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    nivel_discount: Mapped["NivelDiscount"] = relationship(back_populates="bleresit")
    faturat: Mapped[list["Fatura"]] = relationship(back_populates="blerese")
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="blerese")

    def __repr__(self) -> str:
        return f"<Blerese {self.id}: {self.emer} {self.mbiemer}>"


class Shites(Base):
    """Llogaritë e shitësve — kompani me NIPT, magazinë me lat/lng."""
    __tablename__ = "shitesit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emer_kompanie: Mapped[str] = mapped_column(String, nullable=False)
    nipt: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    fjalekalimi_hash: Mapped[str] = mapped_column(String, nullable=False)
    telefon: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    adresa_magazines: Mapped[str] = mapped_column(String, nullable=False)
    qyteti: Mapped[str] = mapped_column(String, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    eshte_verifikuar: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    komision_perqindja: Mapped[float] = mapped_column(Float, default=7.0, nullable=False)
    krijuar_me: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    listimet: Mapped[list["Listim"]] = relationship(back_populates="shites")
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="shites")

    def __repr__(self) -> str:
        return f"<Shites {self.id}: {self.emer_kompanie}>"


# =============================================================================
# 3. KATALOGU: PJESET + LISTIMET
# =============================================================================

class Pjese(Base):
    """Pjesët e këmbimit — katalog master, pa çmim/stok (te LISTIMET)."""
    __tablename__ = "pjeset"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kodi_oem: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    emri: Mapped[str] = mapped_column(String, nullable=False)
    kategori_id: Mapped[int] = mapped_column(Integer, ForeignKey("kategorite.id"), nullable=False)
    marka_id: Mapped[int] = mapped_column(Integer, ForeignKey("markat.id"), nullable=False)
    pesha_kg: Mapped[float] = mapped_column(Float, nullable=False)
    pershkrimi: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model_kompatibil: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    krijuar_me: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    kategori: Mapped["Kategori"] = relationship(back_populates="pjeset")
    marka: Mapped["Marka"] = relationship(back_populates="pjeset")
    listimet: Mapped[list["Listim"]] = relationship(back_populates="pjese")

    def __repr__(self) -> str:
        return f"<Pjese {self.kodi_oem}: {self.emri}>"


class Listim(Base):
    """Ofertat për çift shitës-pjesë: çmim + stok + status."""
    __tablename__ = "listimet"
    __table_args__ = (
        UniqueConstraint("shites_id", "pjese_id", name="uq_listim_shites_pjese"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shites_id: Mapped[int] = mapped_column(Integer, ForeignKey("shitesit.id"), nullable=False)
    pjese_id: Mapped[int] = mapped_column(Integer, ForeignKey("pjeset.id"), nullable=False)
    cmimi: Mapped[float] = mapped_column(Float, nullable=False)
    stoku: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    aktive: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    krijuar_me: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    shites: Mapped["Shites"] = relationship(back_populates="listimet")
    pjese: Mapped["Pjese"] = relationship(back_populates="listimet")
    fatura_detajet: Mapped[list["FaturaDetaj"]] = relationship(back_populates="listim")

    def __repr__(self) -> str:
        return f"<Listim shites={self.shites_id} pjese={self.pjese_id} cmimi={self.cmimi}>"


# =============================================================================
# 4. TRANSAKSIONET: FATURAT + DETAJET + PAGESAT
# =============================================================================

class Fatura(Base):
    """Faturat — 1 për çdo blerje (multi-shitës përmbledhur në një faturë të vetme)."""
    __tablename__ = "faturat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blerese_id: Mapped[int] = mapped_column(Integer, ForeignKey("bleresit.id"), nullable=False)
    zona_transportit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("zonat_transportit.id"), nullable=False
    )
    # Statuset: E_RE | NE_MAGAZINE | NE_TRANSPORT | DORZUAR | ANULUAR
    status: Mapped[str] = mapped_column(String, default="E_RE", nullable=False)
    nentotali: Mapped[float] = mapped_column(Float, nullable=False)
    discount_perqindja: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    discount_shuma: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    pesha_totale_kg: Mapped[float] = mapped_column(Float, nullable=False)
    distanca_km: Mapped[float] = mapped_column(Float, nullable=False)  # magazina → blerës
    kosto_transporti: Mapped[float] = mapped_column(Float, nullable=False)
    totali: Mapped[float] = mapped_column(Float, nullable=False)
    adresa_dergesa: Mapped[str] = mapped_column(String, nullable=False)
    lat_dergesa: Mapped[float] = mapped_column(Float, nullable=False)
    lng_dergesa: Mapped[float] = mapped_column(Float, nullable=False)
    krijuar_me: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    blerese: Mapped["Blerese"] = relationship(back_populates="faturat")
    zona_transportit: Mapped["ZonaTransportit"] = relationship(back_populates="faturat")
    detajet: Mapped[list["FaturaDetaj"]] = relationship(
        back_populates="fatura", cascade="all, delete-orphan"
    )
    pagesa: Mapped[Optional["Pagese"]] = relationship(
        back_populates="fatura", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Fatura {self.id} blerese={self.blerese_id} total={self.totali}>"


class FaturaDetaj(Base):
    """Rreshtat e faturës — referojnë LISTIMIN (shitësi del nga listimi)."""
    __tablename__ = "fatura_detajet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fatura_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("faturat.id", ondelete="CASCADE"), nullable=False
    )
    listim_id: Mapped[int] = mapped_column(Integer, ForeignKey("listimet.id"), nullable=False)
    sasia: Mapped[int] = mapped_column(Integer, nullable=False)
    cmimi_njesi: Mapped[float] = mapped_column(Float, nullable=False)
    pesha_njesi_kg: Mapped[float] = mapped_column(Float, nullable=False)
    total_rreshti: Mapped[float] = mapped_column(Float, nullable=False)

    fatura: Mapped["Fatura"] = relationship(back_populates="detajet")
    listim: Mapped["Listim"] = relationship(back_populates="fatura_detajet")

    def __repr__(self) -> str:
        return f"<FaturaDetaj fatura={self.fatura_id} listim={self.listim_id} x{self.sasia}>"


class Pagese(Base):
    """Pagesat — 1 për çdo faturë."""
    __tablename__ = "pagesat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fatura_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("faturat.id", ondelete="CASCADE"),
        unique=True, nullable=False,
    )
    shuma: Mapped[float] = mapped_column(Float, nullable=False)
    # Vlerat: CASH | KARTE | TRANSFER
    menyra_pageses: Mapped[str] = mapped_column(String, nullable=False)
    # Statuset: PA_PAGUAR | PAGUAR | RIMBURSUAR
    status: Mapped[str] = mapped_column(String, default="PA_PAGUAR", nullable=False)
    krijuar_me: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    fatura: Mapped["Fatura"] = relationship(back_populates="pagesa")

    def __repr__(self) -> str:
        return f"<Pagese fatura={self.fatura_id} {self.shuma} ({self.status})>"


# =============================================================================
# 5. AUTH
# =============================================================================

class ApiKey(Base):
    """API keys për webservice publik — njëra per blerës XOR shitës."""
    __tablename__ = "api_keys"
    __table_args__ = (
        CheckConstraint(
            "(blerese_id IS NOT NULL AND shites_id IS NULL) "
            "OR (blerese_id IS NULL AND shites_id IS NOT NULL)",
            name="ck_api_key_xor_owner",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blerese_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("bleresit.id"), nullable=True
    )
    shites_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("shitesit.id"), nullable=True
    )
    api_key: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    aktive: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    krijuar_me: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    blerese: Mapped[Optional["Blerese"]] = relationship(back_populates="api_keys")
    shites: Mapped[Optional["Shites"]] = relationship(back_populates="api_keys")

    def __repr__(self) -> str:
        if self.blerese_id:
            return f"<ApiKey blerese={self.blerese_id} aktive={self.aktive}>"
        return f"<ApiKey shites={self.shites_id} aktive={self.aktive}>"
