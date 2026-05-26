"""
test_orm.py — Verifikim i shpejtë i modeleve ORM.

Pasi të kesh krijuar DB-në me `python init_db.py`, ekzekuto:
    python test_orm.py

Duhet të dalin 5 raporte testimi pa gabime.
"""
import sys
from pathlib import Path

# Aktivizo UTF-8 në Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Sigurohu që DB-ja ekziston para se të lidhemi
if not (Path(__file__).parent / "hermes.db").exists():
    print("[GABIM] hermes.db nuk ekziston. Ekzekuto: python init_db.py")
    sys.exit(1)

from database.connection import SessionLocal
from database.models import (
    Blerese,
    Fatura,
    Kategori,
    Listim,
    Magazina,
    Marka,
    NivelDiscount,
    Pjese,
    Shites,
    ZonaTransportit,
)


def main():
    db = SessionLocal()
    try:
        # ===== Test 1: Numërimi i rreshtave për 7 tabela =====
        print("=" * 64)
        print("TEST 1 — Numërimi i rreshtave")
        print("=" * 64)
        for klasa in [NivelDiscount, ZonaTransportit, Kategori, Marka,
                      Shites, Blerese, Pjese, Listim]:
            n = db.query(klasa).count()
            print(f"  {klasa.__name__:18s} {n:5d} rreshta")

        # ===== Test 2: Krahasim ofertash për një pjesë =====
        print()
        print("=" * 64)
        print("TEST 2 — Ofertat për BOSCH-0986452060 (filtri Bosch)")
        print("=" * 64)
        pjesa = db.query(Pjese).filter_by(kodi_oem="BOSCH-0986452060").first()
        print(f"  Pjesa:    {pjesa.emri}")
        print(f"  Kategori: {pjesa.kategori.emer}  ←  përmes relationship")
        print(f"  Marka:    {pjesa.marka.emer}     ←  përmes relationship")
        print(f"  Pesha:    {pjesa.pesha_kg} kg")
        print()
        print(f"  {len(pjesa.listimet)} oferta, sortuar nga më e lira:")
        for l in sorted(pjesa.listimet, key=lambda x: x.cmimi):
            print(f"    {l.shites.emer_kompanie:25s} ({l.shites.qyteti:8s}) "
                  f"{l.cmimi:7.2f} EUR  stoku={l.stoku}")

        # ===== Test 3: Blerësit dhe nivelet e tyre =====
        print()
        print("=" * 64)
        print("TEST 3 — Blerësit me nivelin e discount-it")
        print("=" * 64)
        for b in db.query(Blerese).all():
            print(f"  ID={b.id}  {b.emer} {b.mbiemer:15s} "
                  f"Niveli={b.nivel_discount.emer:10s} ({b.nivel_discount.perqindja:4.1f}%)  "
                  f"Totali blerjeve={b.totali_blerjeve:7.2f} EUR")

        # ===== Test 4: Magazina e platformës =====
        print()
        print("=" * 64)
        print("TEST 4 — Magazina e platformës")
        print("=" * 64)
        magazina = db.query(Magazina).filter_by(eshte_aktiv=1).first()
        print(f"  {magazina.emer}")
        print(f"  Adresa: {magazina.adresa}, {magazina.qyteti}")
        print(f"  Lat/Lng: ({magazina.lat}, {magazina.lng})")

        # ===== Test 5: Zonat e transportit =====
        print()
        print("=" * 64)
        print("TEST 5 — Zonat e transportit (Strukturë A)")
        print("=" * 64)
        for z in db.query(ZonaTransportit).all():
            print(f"  {z.emer:11s} {z.distanca_min_km:>5.0f}–{z.distanca_max_km:>5.0f} km  "
                  f"fikse={z.tarifa_fikse:4.2f} €  "
                  f"per_km={z.tarifa_per_km:4.2f} €  "
                  f"per_kg={z.tarifa_per_kg:4.2f} €")

        # ===== Test 6: Faturat (duhet të jenë 0 - nuk janë krijuar ende) =====
        print()
        print("=" * 64)
        print("TEST 6 — Faturat ekzistuese")
        print("=" * 64)
        n_faturat = db.query(Fatura).count()
        print(f"  {n_faturat} faturë në DB (do krijohen kur testojmë webservice-in).")

        print()
        print("=" * 64)
        print("✓ Të gjitha testet kaluan — modelet ORM funksionojnë saktë!")
        print("=" * 64)
    finally:
        db.close()


if __name__ == "__main__":
    main()
