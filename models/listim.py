"""
Pydantic schemas për LISTIMET — ofertat e shitësve për pjesët.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models.pjese import PjeseResponseDetajuar
from models.shites import ShitesPublikResponse


# ============ Request ============

class ListimKrijim(BaseModel):
    """Input për POST /listimet — shitësi krijon ofertë të re."""
    pjese_id: int = Field(..., gt=0)
    cmimi: float = Field(..., ge=0, examples=[12.50])
    stoku: int = Field(..., ge=0, examples=[50])


class ListimUpdate(BaseModel):
    """Input për PATCH /listimet/{id} — ndrysho çmim, stok, ose status."""
    cmimi: Optional[float] = Field(None, ge=0)
    stoku: Optional[int] = Field(None, ge=0)
    aktive: Optional[int] = Field(None, ge=0, le=1, description="0 ose 1")


# ============ Response ============

class ListimResponse(BaseModel):
    """Output bazë për GET /listimet/{id}."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    shites_id: int
    pjese_id: int
    cmimi: float
    stoku: int
    aktive: int
    krijuar_me: datetime


class ListimResponseDetajuar(BaseModel):
    """Output i zgjeruar me shitësin dhe pjesën inline (për ofertat)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    cmimi: float
    stoku: int
    aktive: int
    shites: ShitesPublikResponse
    pjese: PjeseResponseDetajuar
    krijuar_me: datetime
