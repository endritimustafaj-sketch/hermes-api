# Hermes Marketplace API

> Marketplace për pjesë këmbimi makinash. Webservice që lidh shitësit me blerësit dhe automatizon transportin.
>
> *Pjesë e Detyrës së Kursit "Arkitektura dhe Inxhinieria e Sistemeve" (CIS450) — Master Shkencor, Universiteti i Tiranës.*

Hermes — perëndia greke e tregtisë, e udhëtarëve dhe e mesazheve. Tre funksionet që mbulon platforma: tregton, transporton, komunikon nëpërmjet API-së.

---

## Stack-u teknologjik

- **Python 3.11+**
- **FastAPI 0.115** — web framework
- **SQLAlchemy 2.0** — ORM
- **Pydantic 2.9** — validim modelesh
- **SQLite** (testim lokal) / **MySQL** ose **PostgreSQL** (prodhim)
- **bcrypt** — hash i fjalëkalimeve
- **uvicorn** — ASGI server

---

## Setup në 5 hapa

### 1. Klono ose kopjo projektin

```bash
cd hermes-api
```

### 2. Krijo dhe aktivizo virtual environment

```bash
python -m venv venv

# Linux / macOS:
source venv/bin/activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Windows (CMD):
venv\Scripts\activate.bat
```

### 3. Instalo varësitë

```bash
pip install -r requirements.txt
```

### 4. Krijo bazën e të dhënave SQLite (me të dhëna testimi)

**Metoda e rekomanduar** — script Python (funksionon kudo, pa varësi nga sqlite3 CLI):

```bash
python init_db.py
```

Për ta rikrijuar nga fillimi (fshin DB ekzistuese):

```bash
python init_db.py --reset
```

**Alternativa** — nëse ke sqlite3 CLI të instaluar:

```bash
# Linux / macOS / Windows CMD:
sqlite3 hermes.db < hermes_db.sql

# Windows PowerShell (PowerShell nuk e mbështet `<`, përdor në vend `.read`):
sqlite3 hermes.db ".read hermes_db.sql"
```

Të dyja krijojnë `hermes.db` me **13 tabela**, **87 pjesë në katalog**, **191 listime nga 7 shitës**, **5 blerës** me nivele të ndryshme discount-i, dhe **4 API keys** për testim.

### 5. Niset serveri

```bash
uvicorn main:app --reload --port 8000
```

Pasi serveri është aktiv:

| URL | Çfarë |
|-----|-------|
| http://localhost:8000/ | Info bazë + link te dokumentimi |
| http://localhost:8000/docs | **Swagger UI** (rekomanduar) |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/health | Health check |

---

## Si testohet (pa UI)

Profesori mund ta testojë në 3 mënyra, asnjëra prej tyre s'kërkon UI të vetën:

1. **Postman** — krijo një collection me kërkesat HTTP. Vlerat ndryshohen direkt te `Body → raw → JSON`.
2. **curl** — komanda nga terminali. Vlerat ndryshohen direkt te string-u i komandës.
3. **Swagger UI** — te `/docs`. Klik te endpoint-i → *Try it out* → modifiko JSON-in → *Execute*.

Asnjë formular HTML, asnjë faqe ueb e ndërtuar. **Vetëm kod + JSON.**

---

## Struktura e projektit

```
hermes-api/
├── main.py                      # Pika e hyrjes FastAPI
├── requirements.txt             # Varësitë
├── hermes_db.sql                # Schema + seed (DDL + të dhëna)
├── hermes.db                    # SQLite DB (gjenerohet pas seed)
├── .env.example                 # Shabllon variabla mjedisi
├── README.md                    # Ky file
│
├── core/                        # Funksionalitete bazë
│   ├── config.py                # Konfigurim global (Pydantic Settings)
│   └── exceptions.py            # Gabime të personalizuara + handler
│
├── database/                    # Shtresa e bazës së të dhënave
│   ├── connection.py            # SQLAlchemy engine + session
│   └── models.py                # Modelet ORM (vjen te Hapi 5)
│
├── models/                      # Pydantic schemas (validim request/response)
│   ├── blerese.py               # (vjen te Hapi 6)
│   ├── shites.py
│   ├── pjese.py
│   ├── listim.py
│   ├── fatura.py
│   └── pagese.py
│
├── services/                    # Logjika e biznesit
│   ├── llogarite_service.py     # (vjen te Hapi 7)
│   ├── listimet_service.py
│   ├── kerkim_service.py
│   ├── fatura_service.py        # discount + transport
│   ├── pagesa_service.py
│   └── transport_service.py     # Haversine + zona
│
└── routers/                     # Endpoints HTTP të grupuar sipas domenit
    ├── bleresit.py              # (vjen te Hapi 8)
    ├── shitesit.py
    ├── pjeset.py
    ├── listimet.py
    ├── faturat.py
    ├── pagesat.py
    └── webservice_publik.py     # API publik për partnerë (Kërkesa 5)
```

---

## Konfigurim përmes `.env`

Kopjoje `.env.example` në `.env` dhe ndrysho vlerat sipas mjedisit:

```bash
cp .env.example .env
```

Variablat e mbështetura:

| Variabël | Default | Përshkrim |
|----------|---------|-----------|
| `APP_NAME` | "Hermes Marketplace API" | Emri i aplikacionit |
| `DEBUG` | `true` | Logon çdo SQL të ekzekutuar |
| `DATABASE_URL` | `sqlite:///./hermes.db` | URL e bazës së të dhënave |

Për kalim në MySQL/PostgreSQL, vetëm ndrysho `DATABASE_URL` te `.env`:

```bash
# MySQL
DATABASE_URL="mysql+pymysql://user:pass@localhost:3306/hermes"

# PostgreSQL
DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/hermes"
```

(Për këto duhen edhe driver-at përkatës: `pip install pymysql` ose `pip install psycopg2-binary`.)

---

## Autor

**AMF** — Master Shkencor, Inxhinieri Elektronike / Sisteme Informacioni
