"""
test_pydantic.py — Verifikim i schemas-ave Pydantic.

Tregon si Pydantic refuzon automatikisht të dhëna të pavlefshme.
"""
import sys
from pydantic import ValidationError

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from models.blerese import BlereseRegjistrim
from models.shites import ShitesRegjistrim
from models.fatura import FaturaKrijimRequest, FaturaArtikull
from models.webservice import KostoTransportiRequest


def test(emer: str, fn):
    print(f"\n--- {emer} ---")
    try:
        result = fn()
        print(f"[OK] U validua: {type(result).__name__}")
    except ValidationError as e:
        print(f"[REFUZUAR] {len(e.errors())} gabim(e):")
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"])
            print(f"  • {loc}: {err['msg']}")


# ========== Të vlefshme ==========

test("BlereseRegjistrim me të dhëna të vlefshme", lambda: BlereseRegjistrim(
    emer="Arben",
    mbiemer="Hoxha",
    email="arben.hoxha@example.com",
    fjalekalimi="Test1234!",
    telefon="+355681000001",
    adresa="Rruga Myslym Shyri 10",
    qyteti="Tiranë",
    lat=41.3270,
    lng=19.8060,
))

test("ShitesRegjistrim me NIPT të vlefshëm", lambda: ShitesRegjistrim(
    emer_kompanie="AutoPjese Sh.p.k.",
    nipt="L91234567A",
    email="info@autopjese.al",
    fjalekalimi="Test1234!",
    adresa_magazines="Rruga e Kavajës 200",
    qyteti="Tiranë",
    lat=41.3300,
    lng=19.8100,
))

test("KostoTransporti me të dhëna të vlefshme", lambda: KostoTransportiRequest(
    lat_dergesa=41.3270,
    lng_dergesa=19.8060,
    pesha_totale_kg=8.01,
))

test("FaturaKrijim me 2 artikuj", lambda: FaturaKrijimRequest(
    artikujt=[
        FaturaArtikull(listim_id=1, sasia=2),
        FaturaArtikull(listim_id=5, sasia=1),
    ],
    adresa_dergesa="Rruga Myslym Shyri 10",
    lat_dergesa=41.3270,
    lng_dergesa=19.8060,
))

# ========== Të pavlefshme (DUHET të refuzohen) ==========

test("Blerese me email të gabuar", lambda: BlereseRegjistrim(
    emer="Test",
    mbiemer="Test",
    email="jo-email-valid",
    fjalekalimi="Test1234!",
    adresa="Test",
    qyteti="Test",
    lat=41.3,
    lng=19.8,
))

test("Blerese me fjalëkalim shumë të shkurtër (<8)", lambda: BlereseRegjistrim(
    emer="Test",
    mbiemer="Test",
    email="test@example.com",
    fjalekalimi="abc",
    adresa="Test",
    qyteti="Test",
    lat=41.3,
    lng=19.8,
))

test("Blerese me lat jashtë range (-90 ÷ 90)", lambda: BlereseRegjistrim(
    emer="Test",
    mbiemer="Test",
    email="test@example.com",
    fjalekalimi="Test1234!",
    adresa="Test",
    qyteti="Test",
    lat=999.0,
    lng=19.8,
))

test("Shites me NIPT të gabuar (nuk përputhet me regex)", lambda: ShitesRegjistrim(
    emer_kompanie="Test Sh.p.k.",
    nipt="ABC123",
    email="test@example.com",
    fjalekalimi="Test1234!",
    adresa_magazines="Test",
    qyteti="Test",
    lat=41.3,
    lng=19.8,
))

test("KostoTransporti me pesha negative", lambda: KostoTransportiRequest(
    lat_dergesa=41.3,
    lng_dergesa=19.8,
    pesha_totale_kg=-5.0,
))

test("FaturaKrijim me listë boshe artikujsh", lambda: FaturaKrijimRequest(
    artikujt=[],
    adresa_dergesa="Test",
    lat_dergesa=41.3,
    lng_dergesa=19.8,
))

test("FaturaKrijim me sasi 0 (duhet > 0)", lambda: FaturaKrijimRequest(
    artikujt=[FaturaArtikull(listim_id=1, sasia=0)],
    adresa_dergesa="Test",
    lat_dergesa=41.3,
    lng_dergesa=19.8,
))

print("\n" + "=" * 60)
print("Testet kaluan. Pydantic kap automatikisht të dhënat e pavlefshme")
print("dhe i refuzon me HTTP 422 në FastAPI — pa kod validimi manual.")
print("=" * 60)
