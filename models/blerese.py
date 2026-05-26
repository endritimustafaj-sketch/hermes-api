"""
Pydantic schemas për BLERËSIT — regjistrim, përditësim, përgjigje.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============ Request ============

class BlereseRegjistrim(BaseModel):
    """Input për POST /bleresit/regjistrim — krijon llogari të re blerësi."""
    emer: str = Field(..., min_length=1, max_length=50, examples=["Arben"])
    mbiemer: str = Field(..., min_length=1, max_length=50, examples=["Hoxha"])
    email: EmailStr = Field(..., examples=["arben.hoxha@example.com"])
    fjalekalimi: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Minimum 8 karaktere; do hash-ohet me bcrypt",
        examples=["Test1234!"],
    )
    telefon: Optional[str] = Field(None, max_length=20, examples=["+355681000001"])
    nipt: Optional[str] = Field(
        None,
        max_length=15,
        description="Vetëm për biznese; lëre bosh për individë",
        examples=[None],
    )
    adresa: str = Field(..., min_length=1, max_length=200, examples=["Rruga Myslym Shyri 10"])
    qyteti: str = Field(..., min_length=1, max_length=50, examples=["Tiranë"])
    lat: float = Field(..., ge=-90, le=90, examples=[41.3270])
    lng: float = Field(..., ge=-180, le=180, examples=[19.8060])


class BlereseLogin(BaseModel):
    """Input për POST /bleresit/login."""
    email: EmailStr
    fjalekalimi: str


class BlereseUpdate(BaseModel):
    """Input për PATCH /bleresit/{id} — të gjitha fushat janë opsionale."""
    telefon: Optional[str] = Field(None, max_length=20)
    adresa: Optional[str] = Field(None, max_length=200)
    qyteti: Optional[str] = Field(None, max_length=50)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)


# ============ Response ============

class NivelDiscountInline(BaseModel):
    """Niveli i discount-it i përfshirë në përgjigjen e blerësit."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    emer: str
    perqindja: float


class BlereseResponse(BaseModel):
    """Output për GET /bleresit/{id} — pa fjalëkalim, me niveli inline."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    emer: str
    mbiemer: str
    email: str
    telefon: Optional[str]
    nipt: Optional[str]
    adresa: str
    qyteti: str
    lat: float
    lng: float
    nivel_discount: NivelDiscountInline
    totali_blerjeve: float
    krijuar_me: datetime


class BlereseRegjistruarResponse(BaseModel):
    """Output për POST /bleresit/regjistrim — përfshin api_key-n fillestar."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    emer: str
    mbiemer: str
    email: str
    nivel_discount: NivelDiscountInline
    api_key: str = Field(
        ...,
        description="Ruaje këtë — duhet për të bërë thirrje në API.",
        examples=["BLER-xxxx-xxxxxxxxxxxxxxxx"],
    )
    mesazh: str = "Llogaria u krijua me sukses"
