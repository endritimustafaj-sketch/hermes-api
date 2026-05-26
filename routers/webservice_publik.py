"""
Webservice publik — endpoints që përdoren nga partnerët e jashtëm
(servise auto, kompani sigurimesh, aggregatorë çmimesh).

Kjo është pjesa qendrore për **Kërkesën 5 të detyrës**:
    "krijim webservisi që lejon integrim programatik"

Të gjitha endpoints kthejnë JSON. (Autentifikimi me X-API-Key do shtohet te Hapi 10.)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from models.webservice import (
    KerkimPjeseResponse,
    KostoTransportiRequest,
    KostoTransportiResponse,
    LlogaritFatureRequest,
    LlogaritFatureResponse,
    OfertePjeseResponse,
)
from services.fature_service import llogarit_fature
from services.kerkim_service import kerko_ofertat_per_kodi, kerko_pjeset_me_tekst
from services.transport_service import llogarit_kosto_transporti


router = APIRouter(prefix="/public", tags=["Webservice Publik"])


@router.post(
    "/llogarit-fature",
    response_model=LlogaritFatureResponse,
    summary="Llogarit faturën komplete (pa e ruajtur)",
    description=(
        "Endpoint-i kryesor i webservice-it. Llogarit **faturën e plotë** "
        "pa e ruajtur në DB — i përdorshëm për:\n\n"
        "- B2B që duan parashikim çmimi para porosisë reale\n"
        "- Aggregatorë çmimesh që krahasojnë oferta\n"
        "- Konfigurues online që tregojnë totalin live ndërsa user shtjellon\n\n"
        "**Hapat e llogaritjes:**\n"
        "1. Validon blerësin (nëse u jep) → nxjerr nivelin e discount-it\n"
        "2. Për çdo artikull → validon listimin + stokun → llogarit total rreshtin\n"
        "3. Mblidhet nëntotali + pesha totale\n"
        "4. **Discount aplikohet vetëm te nëntotali**, jo te transporti\n"
        "5. Transport llogaritet sipas distancës + peshës (zona Urbane/Suburbane/Rurale)\n"
        "6. **Total final = (nëntotali − discount) + transport**\n\n"
        "**Pa blerese_id:** discount = 0, niveli = 'Standard'.\n"
        "**Me blerese_id:** discount sipas historisë së blerjeve të blerësit."
    ),
)
def llogarit_fature_endpoint(
    request: LlogaritFatureRequest,
    db: Session = Depends(get_db),
) -> LlogaritFatureResponse:
    rezultati = llogarit_fature(
        db=db,
        artikujt=[a.model_dump() for a in request.artikujt],
        distanca_km=request.distanca_km,
        blerese_id=request.blerese_id,
    )
    return LlogaritFatureResponse(**rezultati)


@router.get(
    "/kerko-pjese",
    response_model=KerkimPjeseResponse,
    summary="Kërkim pjesësh me tekst të lirë",
    description=(
        "Kërkim inteligjent me tekst të lirë në katalog.\n\n"
        "**Veçoritë:**\n"
        "- **Multi-fjalë AND** — të gjitha fjalët duhet të përputhen (`filter vaji` → kërko `filter` DHE `vaji`)\n"
        "- **Normalizim diakritikësh shqipe** — `filter` ≈ `filtër`, `kandele` ≈ `kandelë`\n"
        "- **Mbaresa shqipe** — `kandelet`, `kandelete` → `kandele`\n"
        "- **Tolerancë gabimesh 1-karakter** — `flter` → `filter`, `kndele` → `kandele`\n"
        "- **Renditje me peshë** — përputhjet ekzakte renditen para atyre tolerantë\n\n"
        "**Fushat ku kërkohet:**\n"
        "- `kodi_oem` (p.sh. `BOSCH-0986452060`)\n"
        "- `emri` (p.sh. `Filtër vaji premium`)\n"
        "- `pershkrimi`\n"
        "- `model_kompatibil` (p.sh. `VW Golf`, `BMW 3 Series`)\n"
        "- `kategori` dhe `marka`\n\n"
        "Për çdo pjesë të gjetur kthen edhe **ofertat e të gjithë shitësve** "
        "(sortuar nga më e lira)."
    ),
)
def kerko_pjese(
    q: str = Query(
        ...,
        min_length=1,
        description="Termi i kërkimit (kod OEM, emër, përshkrim, model)",
        examples=["kandele"],
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Maksimumi i pjesëve të kthyera (default 10, max 50)",
    ),
    db: Session = Depends(get_db),
) -> KerkimPjeseResponse:
    rezultati = kerko_pjeset_me_tekst(db, q=q, limit=limit)
    return KerkimPjeseResponse(**rezultati)


@router.get(
    "/oferta-pjeses/{kodi_oem}",
    response_model=OfertePjeseResponse,
    summary="Lista e ofertave për një pjesë",
    description=(
        "Kthen të gjitha ofertat aktive nga shitësit për një pjesë të "
        "identifikuar me kodin OEM (p.sh. `BOSCH-0986452060`).\n\n"
        "- Ofertat **renditen nga më e lira te më e shtrenjta**.\n"
        "- Përfshin info të pjesës (emri, kategori, marka, peshë).\n"
        "- Përfshin çmimin min/max për krahasim të shpejtë.\n"
        "- Vetëm listimet me `aktive=1` dhe `stoku > 0` përfshihen."
    ),
)
def oferta_pjeses(
    kodi_oem: str,
    db: Session = Depends(get_db),
) -> OfertePjeseResponse:
    rezultati = kerko_ofertat_per_kodi(db, kodi_oem)
    return OfertePjeseResponse(**rezultati)


@router.post(
    "/kosto-transporti",
    response_model=KostoTransportiResponse,
    summary="Llogarit kostonë e transportit",
    description=(
        "Llogarit kostonë e dorëzimit nga magazina e Hermes te adresa e blerësit. "
        "Përdor formulën:\n\n"
        "**kosto = tarifa_fikse + (distanca × tarifa_per_km) + (pesha × tarifa_per_kg)**\n\n"
        "- **Distanca** llogaritet sipas distancës që jepet direkt si input.\n"
        "- **Zona** (Urbane / Suburbane / Rurale) zgjidhet automatikisht sipas distancës.\n"
        "- Përgjigja jep çdo komponent veçmas që të mund ta verifikosh manualisht."
    ),
)
def kosto_transporti(
    request: KostoTransportiRequest,
    db: Session = Depends(get_db),
) -> KostoTransportiResponse:
    rezultati = llogarit_kosto_transporti(
        db=db,
        distanca_km=request.distanca_km,
        pesha_totale_kg=request.pesha_totale_kg,
    )
    return KostoTransportiResponse(**rezultati)
