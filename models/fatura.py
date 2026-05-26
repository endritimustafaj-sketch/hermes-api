"""
Pydantic schemas për FATURAT dhe detajet e tyre.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============ Request ============

class FaturaArtikull(BaseModel):
    """Një artikull (rresht) brenda kërkesës për krijim faturë."""
    listim_id: int = Field(..., gt=0, description="ID e ofertës që po blihet")
    sasia: int = Field(..., gt=0, examples=[2])


class FaturaKrijimRequest(BaseModel):
    """
    Input për POST /faturat — blerësi vendos artikujt nga 1 ose më shumë shitës.
    Webservisi llogarit nëntotalin, discount-in, transportin, dhe totalin
    automatikisht.
    """
    artikujt: list[FaturaArtikull] = Field(
        ...,
        min_length=1,
        description="Lista e artikujve të blerë (nga 1+ shitës)",
    )
    adresa_dergesa: str = Field(..., min_length=1, max_length=200)
    lat_dergesa: float = Field(..., ge=-90, le=90, examples=[41.3270])
    lng_dergesa: float = Field(..., ge=-180, le=180, examples=[19.8060])


# ============ Response ============

class FaturaDetajResponse(BaseModel):
    """Një rresht detaji brenda faturës."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    listim_id: int
    sasia: int
    cmimi_njesi: float
    pesha_njesi_kg: float
    total_rreshti: float


class FaturaDetajMeListim(BaseModel):
    """Detaj me info të ofertës dhe pjesës inline (për shfaqje në UI ose JSON)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    listim_id: int
    sasia: int
    cmimi_njesi: float
    pesha_njesi_kg: float
    total_rreshti: float
    # Mund të popullohet manualisht në service-in përkatës
    kodi_oem: Optional[str] = None
    emri_pjeses: Optional[str] = None
    emer_shitesi: Optional[str] = None


class FaturaResponse(BaseModel):
    """Output bazë për GET /faturat/{id}."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    blerese_id: int
    zona_transportit_id: int
    status: str
    nentotali: float
    discount_perqindja: float
    discount_shuma: float
    pesha_totale_kg: float
    distanca_km: float
    kosto_transporti: float
    totali: float
    adresa_dergesa: str
    lat_dergesa: float
    lng_dergesa: float
    krijuar_me: datetime


class FaturaResponseFull(BaseModel):
    """Output i plotë me të gjitha detajet inline."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    blerese_id: int
    status: str
    nentotali: float
    discount_perqindja: float
    discount_shuma: float
    pesha_totale_kg: float
    distanca_km: float
    kosto_transporti: float
    totali: float
    adresa_dergesa: str
    detajet: list[FaturaDetajResponse]
    krijuar_me: datetime


class FaturaStatusUpdate(BaseModel):
    """Input për PATCH /faturat/{id}/status — ndrysho gjendjen e dorëzimit."""
    status: str = Field(
        ...,
        description="Vlera e lejuar: E_RE, NE_MAGAZINE, NE_TRANSPORT, DORZUAR, ANULUAR",
        examples=["NE_TRANSPORT"],
    )
