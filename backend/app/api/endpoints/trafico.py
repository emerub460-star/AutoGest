from datetime import date

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import DbDep
from app.models.trafico import TraficoVehicular
from app.schemas.externos import TraficoRead

router = APIRouter(prefix="/api/v1/trafico", tags=["trafico"])

DEFAULT_PEAJE = "ALVARADO"


@router.get("/peajes", response_model=list[str])
def listar_peajes(db: DbDep):
    return list(db.scalars(select(TraficoVehicular.peaje).distinct().order_by(TraficoVehicular.peaje)).all())


@router.get("/", response_model=list[TraficoRead])
def listar_trafico(
    db: DbDep,
    peaje: str | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    limite: int = Query(100, le=1000),
):
    q = select(TraficoVehicular).order_by(TraficoVehicular.periodo_desde.desc()).limit(limite)
    if peaje:
        q = q.where(TraficoVehicular.peaje == peaje.upper())
    if desde:
        q = q.where(TraficoVehicular.periodo_hasta >= desde)
    if hasta:
        q = q.where(TraficoVehicular.periodo_desde <= hasta)
    return list(db.scalars(q).all())


@router.get("/resumen")
def resumen_trafico(
    db: DbDep,
    peaje: str = DEFAULT_PEAJE,
    mes_inicio: str = Query("2014-04"),
    mes_fin: str = Query("2026-05"),
):
    """TC-007: agregado mensual de tráfico por peaje (por defecto ALVARADO, cerca de Ibagué)."""
    registros = list(
        db.scalars(select(TraficoVehicular).where(TraficoVehicular.peaje == peaje.upper())).all()
    )
    if mes_inicio:
        registros = [r for r in registros if str(r.periodo_desde)[:7] >= mes_inicio]
    if mes_fin:
        registros = [r for r in registros if str(r.periodo_hasta)[:7] <= mes_fin]

    por_mes: dict[str, dict] = {}
    for r in registros:
        periodo = str(r.periodo_desde)[:7]
        por_mes.setdefault(periodo, {"trafico": 0, "evasores": 0, "vehiculos_categoria": {}})
        por_mes[periodo]["trafico"] += r.cantidad_trafico
        por_mes[periodo]["evasores"] += r.cantidad_evasores
    return {
        "peaje": peaje.upper(),
        "meses": [
            {"periodo": periodo, **datos}
            for periodo, datos in sorted(por_mes.items(), key=lambda x: x[0], reverse=True)
        ],
        "total_trafico_periodo": sum(d["trafico"] for d in por_mes.values()),
        "total_evasores_periodo": sum(d["evasores"] for d in por_mes.values()),
    }