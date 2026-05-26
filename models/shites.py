"""
Pydantic schemas për SHITËSIT — regjistrim, përditësim, përgjigje.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============ Request ============

class ShitesRegjistrim(BaseModel):
    """Input për POST /shitesit/regjistrim — kërkon NIPT (vetëm biznese)."""
    emer_kompanie: str = Field(..., min_length=1, max_length=100, examples=["AutoPjese Sh.p.k."])
    nipt: str = Field(
        ...,
        min_length=10,
        max_length=12,
        pattern=r"^[A-Z][0-9]{8}[A-Z]$",
        description="Format: shkronjë + 8 shifra + shkronjë (p.sh. L91234567A)",
        examples=["L91234567A"],
    )
    email: EmailStr = Field(..., examples=["info@autopjese.al"])
    fjalekalimi: str = Field(..., min_length=8, max_length=100, examples=["Test1234!"])
    telefon: Optional[str] = Field(None, max_length=20, examples=["+355692111111"])
    adresa_magazines: str = Field(..., min_length=1, max_length=200, examples=["Rruga e Kavajës 200"])
    qyteti: str = Field(..., min_length=1, max_length=50, examples=["Tiranë"])
    lat: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Koordinata e magazinës — përdoret për transport",
        examples=[41.3300],
    )
    lng: float = Field(..., ge=-180, le=180, examples=[19.8100])


class ShitesLogin(BaseModel):
    """Input për POST /shitesit/login."""
    email: EmailStr
    fjalekalimi: str


class ShitesUpdate(BaseModel):
    """Input për PATCH /shitesit/{id}."""
    telefon: Optional[str] = Field(None, max_length=20)
    adresa_magazines: Optional[str] = Field(None, max_length=200)
    qyteti: Optional[str] = Field(None, max_length=50)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)


# ============ Response ============

class ShitesResponse(BaseModel):
    """Output për GET /shitesit/{id}."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    emer_kompanie: str
    nipt: str
    email: str
    telefon: Optional[str]
    adresa_magazines: str
    qyteti: str
    lat: float
    lng: float
    eshte_verifikuar: int
    komision_perqindja: float
    krijuar_me: datetime


class ShitesPublikResponse(BaseModel):
    """Variant publik (pa info të ndjeshme) për listim ofertash."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    emer_kompanie: str
    qyteti: str


class ShitesRegjistruarResponse(BaseModel):
    """Output për POST /shitesit/regjistrim — përfshin api_key-n."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    emer_kompanie: str
    nipt: str
    email: str
    eshte_verifikuar: int
    api_key: str = Field(..., examples=["SHIT-xxxx-xxxxxxxxxxxxxxxx"])
    mesazh: str = (
        "Llogaria u krijua. Pret verifikimin nga admini para se "
        "të mund të krijosh listime."
    )
