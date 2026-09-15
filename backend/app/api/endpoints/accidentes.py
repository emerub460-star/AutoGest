from datetime import date

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import DbDep
from app.models.accidente import Accidente
from app.schemas.externos import AccidenteAgregado, AccidenteRead

router = APIRouter(prefix="/api/v1/accidentes", tags=["accidentes"])

DEFAULT_DEPTO = "TOLIMA"


@router.get("/", response_model=list[AccidenteRead])
def listar_accidentes(
    db: DbDep,
    departamento: str | None = None,
    municipio: str | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    limite: int = Query(100, le=1000),
):
    q = select(Accidente).order_by(Accidente.fecha_hecho.desc()).limit(limite)
    if departamento:
        q = q.where(Accidente.departamento == departamento.upper())
    if municipio:
        q = q.where(Accidente.municipio == municipio.upper())
    if desde:
        q = q.where(Accidente.fecha_hecho >= desde)
    if hasta:
        q = q.where(Accidente.fecha_hecho <= hasta)
    return list(db.scalars(q).all())


@router.get("/agregado", response_model=list[AccidenteAgregado])
def agregado_accidentes(
    db: DbDep,
    departamento: str = DEFAULT_DEPTO,
    municipio: str | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    agregacion: str = Query("month", pattern="^(day|month)$"),
):
    """TC-006: agregados por municipio (diario o mensual). Por defecto Tolima."""
    registros = list(
        db.scalars(
            select(Accidente)
            .where(Accidente.departamento == departamento.upper())
            .order_by(Accidente.fecha_hecho)
        ).all()
    )
    if municipio:
        registros = [a for a in registros if a.municipio == municipio.upper()]
    if desde:
        registros = [a for a in registros if a.fecha_hecho >= desde]
    if hasta:
        registros = [a for a in registros if a.fecha_hecho <= hasta]

    totales: dict[tuple, dict] = {}
    for a in registros:
        if agregacion == "month":
            periodo = a.fecha_hecho.replace(day=1)
        else:
            periodo = a.fecha_hecho
        clave = (periodo, a.departamento, a.municipio)
        totales.setdefault(clave, {"total": 0})["total"] += a.cantidad

    return [
        AccidenteAgregado(
            periodo=periodo, departamento=depto, municipio=muni, total_accidentes=datos["total"]
        )
        for (periodo, depto, muni), datos in sorted(totales.items())
    ]


@router.get("/resumen")
def resumen_accidentes(db: DbDep, departamento: str = DEFAULT_DEPTO, anio: int | None = None):
    registros = list(db.scalars(select(Accidente).where(Accidente.departamento == departamento.upper())).all())
    if anio:
        registros = [a for a in registros if a.fecha_hecho.year == anio]
    total_periodo = sum(r.cantidad for r in registros)
    por_municipio = {}
    por_anio = {}
    for r in registros:
        por_municipio[r.municipio] = por_municipio.get(r.municipio, 0) + r.cantidad
        por_anio[r.fecha_hecho.year] = por_anio.get(r.fecha_hecho.year, 0) + r.cantidad
    return {
        "departamento": departamento.upper(),
        "periodo": f"{min((r.fecha_hecho for r in registros), default=None)} .. {max((r.fecha_hecho for r in registros), default=None)}",
        "total_accidentes": total_periodo,
        "municipio_con_mas": max(por_municipio.items(), key=lambda x: x[1], default=None),
        "por_anio": {str(k): v for k, v in sorted(por_anio.items())},
    }