"""
Logjika për llogaritjen e plotë të faturës (PA e ruajtur në DB).

Ky është endpoint-i kryesor publik për partnerët B2B që duan të marrin një
parashikim të kostos totale para se të bëjnë porosinë reale.

Hapat:
    1. Validon blerësin (nëse u jep) dhe gjen nivelin e discount-it
    2. Për çdo artikull, validon listimin dhe stokun
    3. Mbledh nëntotalin dhe peshën totale
    4. Aplikon discount-in (vetëm te nëntotali, jo te transporti)
    5. Llogarit transportin sipas distancës dhe peshës
    6. Bashkon në totalin final
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from core.exceptions import (
    ListimJoaktiv,
    NukUEGjet,
    StokuPamjaftueshem,
)
from database.models import Blerese, Listim
from services.transport_service import llogarit_kosto_transporti


def llogarit_fature(
    db: Session,
    artikujt: list[dict],
    distanca_km: float,
    blerese_id: int | None = None,
) -> dict:
    """
    Llogarit faturën komplete pa e ruajtur.

    Args:
        db: Sesion DB
        artikujt: Listë me [{"listim_id": int, "sasia": int}, ...]
        distanca_km: Distanca për transport
        blerese_id: ID-ja e blerësit (opsionale; pa të, discount = 0)

    Returns:
        dict që përputhet me LlogaritFatureResponse

    Raises:
        NukUEGjet: blerësi ose ndonjë listim nuk gjendet
        ListimJoaktiv: listimi është çaktivizuar nga shitësi
        StokuPamjaftueshem: sasia e kërkuar tejkalon stokun
    """
    # ----- 1. Validon blerësin (nëse u dha) -----
    bleresi = None
    niveli_emer = "Standard"
    discount_perqindja = 0.0
    if blerese_id is not None:
        bleresi = db.query(Blerese).filter(Blerese.id == blerese_id).first()
        if bleresi is None:
            raise NukUEGjet(
                f"Blerësi me ID {blerese_id} nuk u gjet",
                {"blerese_id": blerese_id},
            )
        nivel = bleresi.nivel_discount
        niveli_emer = nivel.emer
        discount_perqindja = nivel.perqindja

    # ----- 2. Validon dhe llogarit çdo artikull -----
    detajet = []
    nentotali = 0.0
    pesha_totale = 0.0

    for art in artikujt:
        listim_id = art["listim_id"]
        sasia = art["sasia"]

        listimi = db.query(Listim).filter(Listim.id == listim_id).first()
        if listimi is None:
            raise NukUEGjet(
                f"Listimi me ID {listim_id} nuk u gjet",
                {"listim_id": listim_id},
            )
        if not listimi.aktive:
            raise ListimJoaktiv(
                f"Listimi {listim_id} ({listimi.pjese.kodi_oem}) është çaktivizuar",
                {"listim_id": listim_id, "kodi_oem": listimi.pjese.kodi_oem},
            )
        if listimi.stoku < sasia:
            raise StokuPamjaftueshem(
                f"Stoku i pamjaftueshëm për {listimi.pjese.kodi_oem}: "
                f"kërkuar {sasia}, në stok {listimi.stoku}",
                {
                    "listim_id": listim_id,
                    "kodi_oem": listimi.pjese.kodi_oem,
                    "stoku_aktual": listimi.stoku,
                    "sasia_e_kerkuar": sasia,
                },
            )

        total_rreshti = listimi.cmimi * sasia
        pesha_rreshti = listimi.pjese.pesha_kg * sasia

        detajet.append({
            "listim_id": listimi.id,
            "kodi_oem": listimi.pjese.kodi_oem,
            "emri_pjeses": listimi.pjese.emri,
            "emer_shitesi": listimi.shites.emer_kompanie,
            "sasia": sasia,
            "cmimi_njesi": listimi.cmimi,
            "pesha_njesi_kg": listimi.pjese.pesha_kg,
            "total_rreshti": round(total_rreshti, 2),
        })

        nentotali += total_rreshti
        pesha_totale += pesha_rreshti

    # ----- 3. Aplikon discount-in (vetëm te nëntotali) -----
    discount_shuma = nentotali * (discount_perqindja / 100.0)
    nentotali_pas_discount = nentotali - discount_shuma

    # ----- 4. Llogarit transportin -----
    transp = llogarit_kosto_transporti(
        db=db,
        distanca_km=distanca_km,
        pesha_totale_kg=pesha_totale,
    )

    # ----- 5. Totali final -----
    totali = nentotali_pas_discount + transp["kosto_totale"]

    # ----- 6. Përgatit përgjigjen -----
    bleresi_emer = None
    if bleresi is not None:
        bleresi_emer = f"{bleresi.emer} {bleresi.mbiemer}"
        if bleresi.nipt:
            bleresi_emer += f" (NIPT: {bleresi.nipt})"

    return {
        "blerese_id": blerese_id,
        "bleresi_emer": bleresi_emer,
        "niveli_discount": niveli_emer,
        "discount_perqindja": discount_perqindja,
        "discount_shuma": round(discount_shuma, 2),
        "artikujt": detajet,
        "numri_i_artikujve": len(detajet),
        "nentotali": round(nentotali, 2),
        "nentotali_pas_discount": round(nentotali_pas_discount, 2),
        "pesha_totale_kg": round(pesha_totale, 2),
        "distanca_km": round(distanca_km, 2),
        "zona_transportit": transp["zona"],
        "kosto_transporti": transp["kosto_totale"],
        "totali": round(totali, 2),
        "krijuar_me": datetime.now(timezone.utc),
    }
