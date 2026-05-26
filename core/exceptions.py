"""
Klasa të personalizuara për gabimet e biznesit + handler-at e tyre për FastAPI.

Përdorimi te services:
    from core.exceptions import NukUEGjet, StokuPamjaftueshem

    if not blerese:
        raise NukUEGjet("Blerësi nuk ekziston", {"blerese_id": id})

Kthimi i përgjigjes JSON është automatik. Klienti merr:
    HTTP 404
    {
        "gabim": "NukUEGjet",
        "mesazh": "Blerësi nuk ekziston",
        "detaje": {"blerese_id": 99}
    }
"""
from fastapi import Request
from fastapi.responses import JSONResponse


class AutoServisException(Exception):
    """Klasa bazë për të gjitha gabimet e aplikacionit."""
    status_code: int = 400

    def __init__(self, mesazh: str, detaje: dict | None = None):
        self.mesazh = mesazh
        self.detaje = detaje or {}
        super().__init__(mesazh)


class NukUEGjet(AutoServisException):
    """Resursi i kërkuar nuk u gjet në DB (404)."""
    status_code = 404


class StokuPamjaftueshem(AutoServisException):
    """Sasia e kërkuar e tejkalon stokun e disponueshëm (409)."""
    status_code = 409


class ApiKeyIPavlefshme(AutoServisException):
    """Header-i X-API-Key mungon, është i gabuar, ose është çaktivizuar (401)."""
    status_code = 401


class FjalekalimGabim(AutoServisException):
    """Email ose fjalëkalim i gabuar gjatë login (401)."""
    status_code = 401


class ListimDuplikat(AutoServisException):
    """Shitësi ka tashmë një listim për të njëjtën pjesë (409)."""
    status_code = 409


class ListimJoaktiv(AutoServisException):
    """Listimi është çaktivizuar dhe nuk mund të porositet (409)."""
    status_code = 409


class VlefshmeriaEPjesemarrjes(AutoServisException):
    """
    Veprim që kërkon verifikim nga admin (p.sh. shitësi i paverifikuar
    nuk mund të krijojë listime).
    """
    status_code = 403


async def autoservis_exception_handler(
    request: Request, exc: AutoServisException
) -> JSONResponse:
    """
    Konverton çdo AutoServisException në përgjigje JSON të strukturuar.
    Regjistrohet te main.py: app.add_exception_handler(...)
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "gabim": exc.__class__.__name__,
            "mesazh": exc.mesazh,
            "detaje": exc.detaje,
        },
    )
