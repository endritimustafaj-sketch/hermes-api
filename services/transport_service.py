"""
Llogaritja e transportit nga magazina e Hermes te blerësi.

Aplikohet **Strukturë A**:
    kosto = tarifa_fikse + (distanca × tarifa_per_km) + (pesha × tarifa_per_kg)

Distanca jepet direkt si input (në km). Sistemi zgjedh automatikisht
zonën (Urbane / Suburbane / Rurale) sipas distancës dhe kthen koston
e ndarë në komponentët e veta.

Përdorim:
    from services.transport_service import llogarit_kosto_transporti
    result = llogarit_kosto_transporti(db, distanca_km=2.5, pesha_totale_kg=8.01)
"""
from sqlalchemy.orm import Session

from core.exceptions import NukUEGjet
from database.models import ZonaTransportit


def gjej_zonen_per_distance(db: Session, distanca_km: float) -> ZonaTransportit:
    """
    Gjej zonën që përputhet me distancën: [distanca_min_km, distanca_max_km).
    Hidhet NukUEGjet nëse asnjë zonë nuk e mbulon këtë distancë.
    """
    zona = (
        db.query(ZonaTransportit)
        .filter(
            ZonaTransportit.distanca_min_km <= distanca_km,
            ZonaTransportit.distanca_max_km > distanca_km,
        )
        .first()
    )
    if zona is None:
        raise NukUEGjet(
            f"Nuk u gjet zonë transporti për distancën {distanca_km:.2f} km",
            {"distanca_km": distanca_km},
        )
    return zona


def llogarit_kosto_transporti(
    db: Session,
    distanca_km: float,
    pesha_totale_kg: float,
) -> dict:
    """
    Funksioni kryesor — zgjedh zonën sipas distancës dhe llogarit koston.

    Args:
        db: Sesion DB për të lexuar zonat
        distanca_km: distanca nga magazina e Hermes te blerësi (në km)
        pesha_totale_kg: pesha e të gjitha pjesëve që dërgohen

    Returns:
        dict me të gjitha komponentët (përputhet me KostoTransportiResponse):
            distanca_km, pesha_totale_kg, zona, tarifa_fikse,
            kosto_distance, kosto_pesha, kosto_totale
    """
    zona = gjej_zonen_per_distance(db, distanca_km)

    kosto_distance = distanca_km * zona.tarifa_per_km
    kosto_pesha = pesha_totale_kg * zona.tarifa_per_kg
    kosto_totale = zona.tarifa_fikse + kosto_distance + kosto_pesha

    return {
        "distanca_km": round(distanca_km, 2),
        "pesha_totale_kg": round(pesha_totale_kg, 2),
        "zona": zona.emer,
        "tarifa_fikse": zona.tarifa_fikse,
        "kosto_distance": round(kosto_distance, 2),
        "kosto_pesha": round(kosto_pesha, 2),
        "kosto_totale": round(kosto_totale, 2),
    }
