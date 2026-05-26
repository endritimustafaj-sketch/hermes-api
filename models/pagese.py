"""
Pydantic schemas për PAGESAT.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ============ Request ============

class PagesaKrijim(BaseModel):
    """Input për POST /pagesat — regjistro pagesën e një fature."""
    fatura_id: int = Field(..., gt=0)
    menyra_pageses: Literal["CASH", "KARTE", "TRANSFER"] = Field(
        ...,
        description="Mënyra: CASH, KARTE, ose TRANSFER",
        examples=["KARTE"],
    )


# ============ Response ============

class PagesaResponse(BaseModel):
    """Output për GET /pagesat/{id}."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    fatura_id: int
    shuma: float
    menyra_pageses: str
    status: str
    krijuar_me: datetime
