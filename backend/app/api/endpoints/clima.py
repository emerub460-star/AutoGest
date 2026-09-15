from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep
from app.models.clima import ClimaNOAA
from app.schemas.clima import AlertaClima, ClimaRead

router = APIRouter(prefix="/api/v1/clima", tags=["clima"])

UMBRAL_LLUVIA_EXTREMA = Decimal("7.5")


@router.get("/", response_model=list[ClimaRead])
def listar_clima(
    db: DbDep,
    desde: date | None = None,
    hasta: date | None = None,
    limite: int = Query(31, le=366),
):
    q = select(ClimaNOAA).order_by(ClimaNOAA.fecha).limit(limite)
    if desde:
        q = q.where(ClimaNOAA.fecha >= desde)
    if hasta:
        q = q.where(ClimaNOAA.fecha <= hasta)
    return list(db.scalars(q).all())


@router.get("/alertas", response_model=list[AlertaClima])
def alertas_lluvia_extrema(db: DbDep, desde: date | None = None, hasta: date | None = None):
    """RF-04: emite alerta automática cuando precipitación > 7.5 mm (TC-005)."""
    q = select(ClimaNOAA).where(ClimaNOAA.precipitacion_mm > UMBRAL_LLUVIA_EXTREMA).order_by(ClimaNOAA.fecha)
    if desde:
        q = q.where(ClimaNOAA.fecha >= desde)
    if hasta:
        q = q.where(ClimaNOAA.fecha <= hasta)
    dias = db.scalars(q).all()
    return [
        AlertaClima(
            fecha=c.fecha,
            precipitacion_mm=c.precipitacion_mm,
            umbral_mm=UMBRAL_LLUVIA_EXTREMA,
            tipo="LLUVIA_EXTREMA",
        )
        for c in dias
    ]


@router.get("/resumen")
def resumen_clima(db: DbDep, anio: int | None = None, _: CurrentUser = None):
    import calendar

    q = select(ClimaNOAA)
    registros = list(db.scalars(q.order_by(ClimaNOAA.fecha)).all())
    filtrados = [c for c in registros if c.es_lluvia_extrema]
    if anio:
        filtrados = [c for c in filtrados if c.fecha.year == anio]
    meses_lluvia = {}
    for c in filtrados:
        clave = f"{c.fecha.year}-{c.fecha.month:02d}"
        meses_lluvia[clave] = meses_lluvia.get(clave, 0) + 1
    return {
        "total_dias": len(registros),
        "dias_lluvia_extrema": len(filtrados),
        "umbral_mm": float(UMBRAL_LLUVIA_EXTREMA),
        "max_precipitacion_mm": max((float(c.precipitacion_mm) for c in registros), default=0),
        "meses_con_mas_alertas": sorted(meses_lluvia.items(), key=lambda x: -x[1])[:6],
    }