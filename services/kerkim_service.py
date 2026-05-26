"""
Logjika për kërkim pjesësh dhe ofertash në katalog.

Dy funksione kryesore:
- `kerko_ofertat_per_kodi`: kërkim me kod OEM ekzakt (1 rezultat ose 404)
- `kerko_pjeset_me_tekst`: kërkim inteligjent me tekst të lirë (N rezultate)

Kërkimi me tekst mbështet:
  - Normalizim diakritikësh shqipe (ë→e, ç→c)
  - Multi-fjalë AND (të gjitha fjalët duhet të përputhen)
  - Substring në të dy drejtimet (handle mbaresa shqipe: kandele/kandelete)
  - Tolerancë gabimesh drejtshkrimore (Levenshtein ratio ≥ 0.85)
  - Renditje me peshë (përputhje ekzakte > prefiks > tolerantë)
"""
import unicodedata
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from core.exceptions import NukUEGjet
from database.models import Listim, Pjese, Shites


# Pragu për të pranuar përputhje me gabime drejtshkrimore (0..1, sa më afër 1 aq më strikt)
PRAGU_FUZZY = 0.85


def _normalizo(s: str | None) -> str:
    """
    Normalizim teksti për kërkim:
        - heq diakritikët shqipe (ë→e, ç→c, î→i, ...)
        - lowercase
        - heq hapësira të dyfishta

    Shembull: 'Filtër Vaji' → 'filter vaji'
    """
    if not s:
        return ""
    # Dekompozim NFD: ndan shkronjën nga akcenti (p.sh. ë → e + ¨)
    dekompozuar = unicodedata.normalize("NFD", s)
    # Hiq të gjitha karakteret e kategorisë "Mn" (Mark, Nonspacing — diakritikët)
    pa_diakritika = "".join(c for c in dekompozuar if unicodedata.category(c) != "Mn")
    return " ".join(pa_diakritika.lower().split())


def _fjala_ne_fjale(fjala_kerkesa: str, fjalet_dokumentit: list[str]) -> str | None:
    """
    Verifiko nëse `fjala_kerkesa` përputhet me ndonjë fjalë te `fjalet_dokumentit`.

    Kthen llojin e ndeshjes ose None:
        - "ekzakte":  fjala_kerkesa është nën-string i fjalës së dokumentit
                      (p.sh. 'filter' në 'filteri')
        - "mbaresa":  fjala e dokumentit është nën-string i fjala_kerkesa
                      (p.sh. 'kandele' brenda 'kandelete')
        - "tolerante": ratio Levenshtein ≥ PRAGU_FUZZY
        - None: s'ka përputhje
    """
    if not fjala_kerkesa:
        return None

    for w in fjalet_dokumentit:
        # Përputhje ekzakte / nën-string: kërkesa ⊂ dokument
        if fjala_kerkesa in w:
            return "ekzakte"

    for w in fjalet_dokumentit:
        # Mbaresa shqipe: dokument ⊂ kërkesa (kandele ⊂ kandelete)
        if len(w) >= 3 and w in fjala_kerkesa:
            return "mbaresa"

    for w in fjalet_dokumentit:
        # Tolerancë gabimesh drejtshkrimore: vetëm për fjalë me 4+ shkronja
        if len(fjala_kerkesa) >= 4 and len(w) >= 4:
            if SequenceMatcher(None, fjala_kerkesa, w).ratio() >= PRAGU_FUZZY:
                return "tolerante"

    return None


def _strukturo_oferta_per_pjese(db: Session, pjesa: Pjese) -> dict:
    """Për një pjesë të dhënë, gjej dhe strukturo ofertat e saj aktive."""
    listimet = (
        db.query(Listim)
        .join(Shites, Shites.id == Listim.shites_id)
        .filter(
            Listim.pjese_id == pjesa.id,
            Listim.aktive == 1,
            Listim.stoku > 0,
        )
        .order_by(Listim.cmimi.asc())
        .all()
    )

    ofertat = [
        {
            "listim_id": l.id,
            "shites_id": l.shites.id,
            "emer_kompanie": l.shites.emer_kompanie,
            "qyteti": l.shites.qyteti,
            "cmimi": l.cmimi,
            "stoku": l.stoku,
        }
        for l in listimet
    ]

    return {
        "kodi_oem": pjesa.kodi_oem,
        "emri_pjeses": pjesa.emri,
        "kategori": pjesa.kategori.emer,
        "marka": pjesa.marka.emer,
        "pesha_kg": pjesa.pesha_kg,
        "model_kompatibil": pjesa.model_kompatibil,
        "numri_i_ofertave": len(ofertat),
        "cmimi_min": ofertat[0]["cmimi"] if ofertat else None,
        "cmimi_max": ofertat[-1]["cmimi"] if ofertat else None,
        "ofertat": ofertat,
    }


def kerko_ofertat_per_kodi(db: Session, kodi_oem: str) -> dict:
    """Kërkim me kod OEM ekzakt. Kthen ofertat për 1 pjesë specifike."""
    pjesa = db.query(Pjese).filter(Pjese.kodi_oem == kodi_oem).first()
    if pjesa is None:
        raise NukUEGjet(
            f"Pjesa me kodi_oem '{kodi_oem}' nuk u gjet në katalog",
            {"kodi_oem": kodi_oem},
        )
    return _strukturo_oferta_per_pjese(db, pjesa)


# Peshat për renditje sipas cilësisë së përputhjes
PESHA_NDESHJES = {"ekzakte": 3, "mbaresa": 2, "tolerante": 1}


def kerko_pjeset_me_tekst(db: Session, q: str, limit: int = 10) -> dict:
    """
    Kërkim inteligjent me tekst të lirë.

    Algoritmi:
        1. Normalizo kërkesën (heq diakritikët shqipe, lowercase)
        2. Ndaje në fjalë (split sipas hapësirave)
        3. Për çdo pjesë:
             - Mblidh tekstin e të gjitha fushave të kërkueshme
             - Normalizo dhe ndaje në fjalë
             - Verifiko që ÇDO fjalë e kërkesës përputhet me ndonjë fjalë të dokumentit
             - Llogarit pikët (ekzakte=3, mbaresa=2, tolerante=1)
        4. Rendit sipas pikëve DESC, pastaj kodi_oem ASC
        5. Kthe top `limit`
    """
    q_norm = _normalizo(q)
    if not q_norm:
        return {"q": q, "numri_total": 0, "limit": limit, "rezultatet": []}

    fjalet_kerkimit = q_norm.split()

    te_gjitha = db.query(Pjese).all()
    matches_me_pike = []

    for p in te_gjitha:
        # Teksti i kombinuar nga 6 fusha
        tekst_komplet = " ".join(filter(None, [
            p.kodi_oem,
            p.emri,
            p.pershkrimi or "",
            p.model_kompatibil or "",
            p.kategori.emer if p.kategori else "",
            p.marka.emer if p.marka else "",
        ]))
        fjalet_dokumentit = _normalizo(tekst_komplet).split()

        # Çdo fjalë e kërkesës duhet të përputhet me një fjalë të dokumentit (AND)
        pike_total = 0
        te_gjitha_ndeshen = True
        for fjala in fjalet_kerkimit:
            lloji = _fjala_ne_fjale(fjala, fjalet_dokumentit)
            if lloji is None:
                te_gjitha_ndeshen = False
                break
            pike_total += PESHA_NDESHJES[lloji]

        if te_gjitha_ndeshen:
            matches_me_pike.append((pike_total, p))

    # Rendit: më shumë pikë para, pastaj alfabetik
    matches_me_pike.sort(key=lambda x: (-x[0], x[1].kodi_oem))
    pjeset_top = [p for _, p in matches_me_pike[:limit]]

    rezultatet = [_strukturo_oferta_per_pjese(db, p) for p in pjeset_top]

    return {
        "q": q,
        "numri_total": len(rezultatet),
        "limit": limit,
        "rezultatet": rezultatet,
    }
