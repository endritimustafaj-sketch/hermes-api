"""
Pydantic schemas të përbashkëta — përdoren në më shumë se një domen.
"""
from pydantic import BaseModel


class MesazhResponse(BaseModel):
    """Përgjigje e thjeshtë vetëm me një mesazh tekstual."""
    mesazh: str


class GabimResponse(BaseModel):
    """Përgjigje e standardizuar për gabime (përputhet me AutoServisException)."""
    gabim: str
    mesazh: str
    detaje: dict = {}
