# Hermes Marketplace API

> Marketplace REST API për pjesë këmbimi makinash · *Detyrë e Kursit CIS450, UPT, Maj 2026*

## 🌐 Live Demo

**[hermes-api-cwnf.onrender.com/docs](https://hermes-api-cwnf.onrender.com/docs)** — Swagger UI me 4 endpoints publike

## ⭐ Endpoints (Kërkesa 5 e detyrës)

| Metoda | Endpoint | Funksioni |
|--------|----------|-----------|
| `GET`  | `/api/v1/public/kerko-pjese?q=...` | Kërkim inteligjent (multi-fjalë, mbaresa shqipe, tolerancë gabimesh) |
| `GET`  | `/api/v1/public/oferta-pjeses/{kodi_oem}` | Krahasim çmimesh nga shumë shitës |
| `POST` | `/api/v1/public/kosto-transporti` | Llogarit transport (3 zona, sipas distancës + peshës) |
| `POST` | `/api/v1/public/llogarit-fature` | Faturë komplete me discount + transport |

## 🛠 Stack

Python 3.11 · FastAPI · SQLAlchemy 2.0 · Pydantic 2 · SQLite (dev) / MySQL ose PostgreSQL (prod) · Render + UptimeRobot

## 💻 Setup lokal

```bash
python -m venv venv && .\venv\Scripts\Activate.ps1     # Windows
# ose: source venv/bin/activate                        # Linux/macOS
pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload
```

Hap **http://localhost:8000/docs**

## 👤 Autor

**Endrit Mustafaj** — Master Shkencor, Universiteti Politeknik i Tiranës, Maj 2026
