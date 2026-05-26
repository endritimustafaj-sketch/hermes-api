"""
init_db.py — Inicializon bazën e të dhënave Hermes.

Lexon hermes_db.sql dhe ekzekuton të gjitha komandat te skedari hermes.db.
Funksionon në Windows, Linux, dhe macOS pa nevojë për sqlite3 CLI.

Përdorimi:
    python init_db.py                # krijon DB nëse nuk ekziston
    python init_db.py --reset        # fshin DB ekzistuese dhe e rikrijon
"""
import sqlite3
import argparse
import sys
from pathlib import Path

# UTF-8 output (i nevojshëm në Windows ku codepage default mund të mos jetë UTF-8)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SQL_FILE = Path(__file__).parent / "hermes_db.sql"
DB_FILE = Path(__file__).parent / "hermes.db"
TABELAT = [
    "nivelet_discount", "zonat_transportit", "magazina",
    "kategorite", "markat", "shitesit", "bleresit",
    "pjeset", "listimet", "api_keys",
]


def init_db(reset: bool = False) -> None:
    if not SQL_FILE.exists():
        print(f"[GABIM] Nuk u gjet skedari {SQL_FILE.name} në {SQL_FILE.parent}")
        sys.exit(1)

    if reset and DB_FILE.exists():
        DB_FILE.unlink()
        print(f"[OK] U fshi {DB_FILE.name}")

    if DB_FILE.exists():
        print(f"[INFO] {DB_FILE.name} ekziston tashmë.")
        print(f"       Përdor 'python init_db.py --reset' për ta rikrijuar.")
        return

    print(f"[INFO] Po lexoj {SQL_FILE.name}...")
    sql_script = SQL_FILE.read_text(encoding="utf-8")

    print(f"[INFO] Po krijoj {DB_FILE.name}...")
    conn = sqlite3.connect(str(DB_FILE))
    try:
        conn.executescript(sql_script)
        conn.commit()
    finally:
        conn.close()

    # Verifikim — numëro rreshtat e çdo tabele
    conn = sqlite3.connect(str(DB_FILE))
    cur = conn.cursor()
    counts = {}
    for t in TABELAT:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        counts[t] = cur.fetchone()[0]
    conn.close()

    size_kb = DB_FILE.stat().st_size // 1024
    print()
    print(f"[OK] DB u krijua me sukses ({size_kb} KB)")
    print()
    print("Përmbajtja:")
    for t, n in counts.items():
        print(f"  {t:22s} {n:5d} rreshta")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inicializon DB-në e Hermes")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Fshin hermes.db ekzistuese dhe e rikrijon nga fillimi",
    )
    args = parser.parse_args()
    init_db(reset=args.reset)
