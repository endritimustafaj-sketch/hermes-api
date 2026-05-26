"""
Pydantic schemas për PJESËT (katalogu master).
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============ Request ============

class PjeseKrijim(BaseModel):
    """Input për POST /pjeset — shton një pjesë të re në katalog (admin)."""
    model_config = ConfigDict(protected_namespaces=())

    kodi_oem: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Kodi OEM unik (p.sh. BOSCH-0986452060)",
        examples=["BOSCH-0986452060"],
    )
    emri: str = Field(..., min_length=1, max_length=100, examples=["Filtër vaji premium"])
    kategori_id: int = Field(..., gt=0)
    marka_id: int = Field(..., gt=0)
    pesha_kg: float = Field(
        ...,
        gt=0,
        description="Pesha në kg — duhet > 0 (përdoret për llogaritjen e transportit)",
        examples=[0.350],
    )
    pershkrimi: Optional[str] = Field(None, max_length=500)
    model_kompatibil: Optional[str] = Field(None, max_length=200, examples=["VW Golf 5,6"])


class PjeseUpdate(BaseModel):
    """Input për PATCH /pjeset/{id}."""
    model_config = ConfigDict(protected_namespaces=())

    emri: Optional[str] = Field(None, max_length=100)
    kategori_id: Optional[int] = Field(None, gt=0)
    marka_id: Optional[int] = Field(None, gt=0)
    pesha_kg: Optional[float] = Field(None, gt=0)
    pershkrimi: Optional[str] = Field(None, max_length=500)
    model_kompatibil: Optional[str] = Field(None, max_length=200)


class PjeseKerkimFilters(BaseModel):
    """Query parameters për GET /pjeset (kërkim me filtra)."""
    kategori_id: Optional[int] = None
    marka_id: Optional[int] = None
    kerkesa_tekst: Optional[str] = Field(
        None, description="Kërko në emri/kodi_oem/model_kompatibil"
    )


# ============ Response ============

class KategoriInline(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    emer: str


class MarkaInline(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    emer: str
    vendi_origjines: Optional[str]


class PjeseResponse(BaseModel):
    """Output bazë për GET /pjeset/{id}."""
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    kodi_oem: str
    emri: str
    kategori_id: int
    marka_id: int
    pesha_kg: float
    pershkrimi: Optional[str]
    model_kompatibil: Optional[str]
    krijuar_me: datetime


class PjeseResponseDetajuar(BaseModel):
    """Output i zgjeruar me kategorinë dhe markën e zgjidhura inline."""
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    kodi_oem: str
    emri: str
    pesha_kg: float
    pershkrimi: Optional[str]
    model_kompatibil: Optional[str]
    kategori: KategoriInline
    marka: MarkaInline
    krijuar_me: datetime
