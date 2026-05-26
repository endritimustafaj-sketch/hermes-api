"""
Pydantic schemas për WEBSERVICE-IN PUBLIK — endpoints që përdoren nga
partnerët e jashtëm me header X-API-Key.

Kjo është pjesa qendrore e Kërkesës 5 të detyrës.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Endpoint 1: GET /api/v1/public/oferta-pjeses/{kodi_oem}
# =============================================================================

class OfertaShitesi(BaseModel):
    """Një ofertë nga një shitës specifik për një pjesë."""
    model_config = ConfigDict(from_attributes=True)

    listim_id: int = Field(..., description="ID e listimit (përdore për të blerë)")
    shites_id: int
    emer_kompanie: str
    qyteti: str
    cmimi: float
    stoku: int


class OfertePjeseResponse(BaseModel):
    """
    Përgjigje për GET /api/v1/public/oferta-pjeses/{kodi_oem}.

    Kthen TË GJITHA ofertat aktive për një kod OEM, të renditura sipas çmimit.
    """
    model_config = ConfigDict(protected_namespaces=())

    kodi_oem: str = Field(..., examples=["BOSCH-0986452060"])
    emri_pjeses: str = Field(..., examples=["Filtër vaji premium"])
    kategori: str = Field(..., examples=["Filtra"])
    marka: str = Field(..., examples=["Bosch"])
    pesha_kg: float = Field(..., examples=[0.350])
    model_kompatibil: Optional[str] = Field(None, examples=["VW Golf 5,6"])
    numri_i_ofertave: int = Field(..., description="Sa shitës e listojnë")
    cmimi_min: Optional[float] = Field(None, description="Çmimi më i lirë")
    cmimi_max: Optional[float] = Field(None, description="Çmimi më i shtrenjtë")
    ofertat: list[OfertaShitesi] = Field(
        ...,
        description="Lista e ofertave, renditur ASC sipas çmimit",
    )


class KerkimPjeseResponse(BaseModel):
    """
    Përgjigje për GET /api/v1/public/kerko-pjese?q=...

    Kërkim me tekst të lirë në kodi_oem, emri, pershkrimi, model_kompatibil.
    """
    q: str = Field(..., description="Termi i kërkuar")
    numri_total: int = Field(..., description="Sa pjesë u gjetën që përputhen")
    limit: int = Field(..., description="Maksimumi i rezultateve të kthyera")
    rezultatet: list[OfertePjeseResponse] = Field(
        ...,
        description="Lista e pjesëve që përputhen, secila me ofertat e veta",
    )


# =============================================================================
# Endpoint 2: POST /api/v1/public/kosto-transporti
# =============================================================================

class KostoTransportiRequest(BaseModel):
    """Input — distanca në km + pesha totale."""
    distanca_km: float = Field(
        ...,
        ge=0,
        description="Distanca nga magazinës te blerësi në kilometra",
        examples=[2.5],
    )
    pesha_totale_kg: float = Field(
        ...,
        gt=0,
        description="Pesha totale e të gjitha pjesëve që do dërgohen",
        examples=[8.01],
    )


class KostoTransportiResponse(BaseModel):
    """Output — kosto e detajuar e transportit."""
    distanca_km: float = Field(..., description="Distanca magazina → blerës (e dhënë në input)")
    pesha_totale_kg: float
    zona: str = Field(..., description="Urbane / Suburbane / Rurale")
    tarifa_fikse: float
    kosto_distance: float = Field(..., description="distanca × tarifa_per_km")
    kosto_pesha: float = Field(..., description="pesha × tarifa_per_kg")
    kosto_totale: float = Field(..., description="fikse + kosto_distance + kosto_pesha")


# =============================================================================
# Endpoint 3: POST /api/v1/public/llogarit-fature
# =============================================================================
# (Llogarit faturën pa e ruajtur — për preview / planifikim)

class LlogaritFatureArtikull(BaseModel):
    """Një artikull për të llogaritur."""
    listim_id: int = Field(..., gt=0)
    sasia: int = Field(..., gt=0)


class LlogaritFatureRequest(BaseModel):
    """Input — artikujt + distanca, pa ruajtur asgjë në DB."""
    artikujt: list[LlogaritFatureArtikull] = Field(..., min_length=1)
    distanca_km: float = Field(
        ...,
        ge=0,
        description="Distanca nga magazina e Hermes te blerësi në km",
        examples=[2.5],
    )
    blerese_id: Optional[int] = Field(
        None,
        description=(
            "Nëse jepet, aplikohet niveli i discount-it i blerësit. "
            "Përndryshe llogaritet pa discount."
        ),
    )


class LlogaritFatureArtikullDetaj(BaseModel):
    """Artikulli i llogaritur me detajet snapshot."""
    listim_id: int
    kodi_oem: str
    emri_pjeses: str
    emer_shitesi: str
    sasia: int
    cmimi_njesi: float
    pesha_njesi_kg: float
    total_rreshti: float


class LlogaritFatureResponse(BaseModel):
    """Output — fatura e llogaritur me të gjitha komponentët."""
    blerese_id: Optional[int] = Field(None)
    bleresi_emer: Optional[str] = Field(None, description="Emri i blerësit (nëse u jep blerese_id)")
    niveli_discount: str = Field(..., description="Welcome / Standard / Silver / Gold / Platinum")
    discount_perqindja: float = Field(..., description="0 nëse blerese_id nuk u dha")
    discount_shuma: float
    artikujt: list[LlogaritFatureArtikullDetaj]
    numri_i_artikujve: int = Field(..., description="Sa rreshta artikujsh")
    nentotali: float = Field(..., description="Shuma e të gjithë artikujve para discount-it")
    nentotali_pas_discount: float = Field(..., description="nentotali - discount_shuma")
    pesha_totale_kg: float
    distanca_km: float
    zona_transportit: str
    kosto_transporti: float
    totali: float = Field(..., description="(nentotali - discount) + kosto_transporti")
    krijuar_me: datetime = Field(..., description="Timestamp i llogaritjes (jo i ruajtur)")
