# Hermes Marketplace API

> Marketplace për pjesë këmbimi makinash. Webservice që lidh shitësit me blerësit dhe automatizon transportin.
>
> *Pjesë e Detyrës së Kursit "Arkitektura dhe Inxhinieria e Sistemeve" (CIS450) — Master Shkencor, Universiteti i Tiranës.*

Hermes — perëndia greke e tregtisë, e udhëtarëve dhe e mesazheve. Tre funksionet që mbulon platforma: tregton, transporton, komunikon nëpërmjet API-së.

---

## 🌐 Demo Live

| | URL |
|---|-----|
| 🎯 **Swagger UI (rekomanduar)** | https://hermes-api-cwnf.onrender.com/docs |
| 📖 ReDoc (alternativ) | https://hermes-api-cwnf.onrender.com/redoc |
| 🩺 Health check | https://hermes-api-cwnf.onrender.com/health |
| 📊 Status & veçoritë | https://hermes-api-cwnf.onrender.com/version |

> **Shënim:** Render free-plan fle pas 15 min pa trafik. Thirrja e parë mund të zgjasë ~30 sek. UptimeRobot e mban të zgjuar duke pinguar `/health` çdo 5 min.

---

## ⭐ Endpoints publike (Kërkesa 5 e detyrës)

API-ja ekspozon **4 endpoints publike** për integrim programatik nga partnerët B2B:

| Metoda | Endpoint | Funksioni |
|--------|----------|-----------|
| `GET` | `/api/v1/public/kerko-pjese?q=...&limit=N` | Kërkim inteligjent me tekst të lirë |
| `GET` | `/api/v1/public/oferta-pjeses/{kodi_oem}` | Krahasim ofertash sipas kodi OEM |
| `POST` | `/api/v1/public/kosto-transporti` | Llogarit transport sipas distancës + peshës |
| `POST` | `/api/v1/public/llogarit-fature` | Faturë komplete: artikuj + discount + transport |

### Veçoritë e kërkimit (`/kerko-pjese`)

- **Multi-fjalë AND** — `filter vaji` → kërko `filter` DHE `vaji`
- **Normalizim diakritikësh shqipe** — `filter` ≈ `filtër`, `kandele` ≈ `kandelë`
- **Mbaresa shqipe** — `kandelet`, `kandelete` → `kandele`
- **Tolerancë gabimesh 1-karakter** — `flter` → `filter`, `kndele` → `kandele`
- **Fushat e kërkueshme:** `kodi_oem`, `emri`, `pershkrimi`, `model_kompatibil`, `kategori`, `marka`

---

## 🚀 Si ta testosh (pa UI)

API mund të testohet në 3 mënyra, asnjëra nuk kërkon ndërfaqe grafike të vetën:

1. **Swagger UI** (më e thjeshta) — hap `/docs`, klik endpoint → *Try it out* → modifiko JSON → *Execute*
2. **Postman** — krijo collection me kërkesat HTTP, ndrysho vlerat te `Body → raw → JSON`
3. **curl** — komanda nga terminali

### Shembuj të shpejtë (curl)

```bash
# 1. Kërkim pjesësh (kërkimi inteligjent — toleron gabime e mbaresa)
curl 'https://hermes-api-cwnf.onrender.com/api/v1/public/kerko-pjese?q=filter+vaji'

# 2. Oferta për një kod OEM specifik
curl 'https://hermes-api-cwnf.onrender.com/api/v1/public/oferta-pjeses/BOSCH-0986452060'

# 3. Llogarit transport
curl -X POST 'https://hermes-api-cwnf.onrender.com/api/v1/public/kosto-transporti' \
  -H 'Content-Type: application/json' \
  -d '{"distanca_km": 2.5, "pesha_totale_kg": 8.01}'

# 4. Faturë komplete me discount (Welcome 5%)
curl -X POST 'https://hermes-api-cwnf.onrender.com/api/v1/public/llogarit-fature' \
  -H 'Content-Type: application/json' \
  -d '{
    "artikujt": [
      {"listim_id": 2, "sasia": 1},
      {"listim_id": 93, "sasia": 4}
    ],
    "distanca_km": 2.5,
    "blerese_id": 1
  }'
```

### Nivelet e discount-it (sipas blerësit)

| `blerese_id` | Blerësi | Niveli | Përqindja |
|-------------:|---------|--------|----------:|
| 1 | Arben Hoxha | Welcome | 5% (porosia 1) |
| 2 | Edi Krasniqi | Standard | 0% |
| 3 | Anila Berisha | Silver | 5% (≥500€) |
| 4 | Edmond Beqiri | Gold | 10% (≥2000€) |
| 5 | AutoServis Bega Sh.p.k. | Platinum | 15% (≥5000€) |
| _omitet_ | Anonim | Standard | 0% |

---

## 🛠 Stack-u teknologjik

- **Python 3.11**
- **FastAPI 0.115** — web framework
- **SQLAlchemy 2.0** — ORM
- **Pydantic 2.9** — validim modelesh
- **SQLite** (testim lokal) / **MySQL** ose **PostgreSQL** (prodhim)
- **uvicorn** — ASGI server
- **bcrypt** — hash i fjalëkalimeve
- **Render** — hosting (free plan, region Frankfurt)
- **UptimeRobot** — monitorim 24/7

---

## 💻 Setup lokal

### 1. Klono nga GitHub

```bash
git clone https://github.com/USERNAME/hermes-api.git
cd hermes-api
```

### 2. Krijo virtual environment

```bash
python -m venv venv

# Linux / macOS:
source venv/bin/activate

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 3. Instalo varësitë

```bash
pip install -r requirements.txt
```

### 4. Krijo bazën e të dhënave

```bash
python init_db.py
```

Kjo krijon `hermes.db` me **13 tabela**, **87 pjesë**, **191 listime nga 7 shitës**, **5 blerës**, dhe **4 API keys** për testim.

### 5. Nise serverin

```bash
uvicorn main:app --reload --port 8000
```

Pasi serveri është aktiv, hap http://localhost:8000/docs

---

## 📂 Struktura e projektit

```
hermes-api/
├── main.py                      # Pika e hyrjes FastAPI + endpoints sistem (/version, /health)
├── init_db.py                   # Script për inicializim DB
├── requirements.txt             # Varësitë Python
├── hermes_db.sql                # Schema + seed (DDL + të dhëna)
├── render.yaml                  # Konfigurim Render Blueprint
├── .python-version              # Specifikon Python 3.11.7 për Render
├── .gitignore
│
├── core/
│   ├── config.py                # Konfigurim global (Pydantic Settings)
│   └── exceptions.py            # Gabime të personalizuara + handler
│
├── database/
│   ├── connection.py            # SQLAlchemy engine + session factory
│   └── models.py                # 13 modelet ORM
│
├── models/                      # Pydantic schemas (validim request/response)
│   ├── common.py
│   ├── blerese.py
│   ├── shites.py
│   ├── pjese.py
│   ├── listim.py
│   ├── fatura.py
│   ├── pagese.py
│   └── webservice.py            # Schemas për endpoints publike
│
├── services/                    # Logjika e biznesit
│   ├── transport_service.py     # Llogaritja e transportit me zona
│   ├── kerkim_service.py        # Kërkim inteligjent (norm. + multi-fjalë + fuzzy)
│   └── fature_service.py        # Faturë komplete (discount + transport)
│
└── routers/
    └── webservice_publik.py     # 4 endpoints publike (Kërkesa 5 e detyrës)
```

---

## 🗄️ Skema e bazës së të dhënave (13 tabela)

| Tabela | Përmbajtja |
|--------|------------|
| `nivelet_discount` | 5 nivele: Welcome, Standard, Silver, Gold, Platinum |
| `zonat_transportit` | 3 zona: Urbane (0-30km), Suburbane (30-100km), Rurale (>100km) |
| `magazina` | Pika qendrore e Hermes (Tiranë) |
| `kategorite` | 15 kategori pjesësh |
| `markat` | 30 marka (Bosch, Mahle, Brembo, NGK, Michelin, etj.) |
| `pjeset` | 87 pjesë në katalog master (me kodi_oem unik) |
| `shitesit` | 7 shitës me NIPT, lat/lng, komision |
| `bleresit` | 5 blerës (individë + biznese) me nivel_discount_id |
| `listimet` | 191 oferta (çift unik shites_id+pjese_id) |
| `faturat` | Porositë (statuset: E_RE, NE_MAGAZINE, NE_TRANSPORT, DORZUAR, ANULUAR) |
| `fatura_detajet` | Artikujt e secilës faturë me snapshot çmimi/peshe |
| `pagesat` | Pagesa 1:1 me faturat |
| `api_keys` | Çelësa autentifikimi për blerës/shitës |

---

## 🚀 Deployment

API është i deployed te **Render** (free plan) me konfigurim te `render.yaml`:

- **Build:** `pip install -r requirements.txt && python init_db.py`
- **Start:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health check:** `/health`
- **Region:** Frankfurt
- **Auto-deploy:** çdo `git push` te branch `main`

**UptimeRobot** ping-on `/health` çdo 5 min për ta mbajtur Render-in zgjuar (free plan flë pas 15 min pa trafik).

---

## ⚙️ Konfigurim me variabla mjedisi

| Variabël | Default | Përshkrim |
|----------|---------|-----------|
| `DEBUG` | `true` | Logon çdo SQL të ekzekutuar |
| `DATABASE_URL` | `sqlite:///./hermes.db` | URL e bazës së të dhënave |
| `PYTHON_VERSION` | `3.11.7` | Versioni i Python (lexohet nga Render) |

Për kalim në MySQL/PostgreSQL, vetëm ndrysho `DATABASE_URL`:

```bash
# MySQL
DATABASE_URL="mysql+pymysql://user:pass@localhost:3306/hermes"

# PostgreSQL  
DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/hermes"
```

(Për këto duhen drivers shtesë: `pip install pymysql` ose `pip install psycopg2-binary`.)

---

## 👤 Autor

**Endrit Mustafaj** — Master Shkencor, Inxhinieri Elektronike / Sisteme Informacioni

Universiteti Politeknik i Tiranës, Maj 2026
