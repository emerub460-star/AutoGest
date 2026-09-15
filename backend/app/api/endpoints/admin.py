from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbDep, require_roles
from app.models.accidente import Accidente
from app.models.cita import Cita
from app.models.clima import ClimaNOAA
from app.models.grua import ServicioGrua
from app.models.servicio import ServicioReparacion
from app.models.trafico import TraficoVehicular

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
es_admin = require_roles("ADMIN")

META_UMBRAL_LLUVIA = 7.5


@router.get("/dashboard")
def dashboard(db: DbDep, _: CurrentUser = es_admin):
    total_servicios = db.scalar(select(func.count()).select_from(ServicioReparacion)) or 0
    total_outliers = (
        db.scalar(
            select(func.count())
            .select_from(ServicioReparacion)
            .where(ServicioReparacion.es_outlier_costo.is_(True))
        )
        or 0
    )
    total_gruas = db.scalar(select(func.count()).select_from(ServicioGrua)) or 0
    citas_pendientes = (
        db.scalar(
            select(func.count()).select_from(Cita).where(Cita.estado.in_(["PENDIENTE", "CONFIRMADA"]))
        )
        or 0
    )
    dias_lluvia_extrema = (
        db.scalar(
            select(func.count())
            .select_from(ClimaNOAA)
            .where(ClimaNOAA.precipitacion_mm > META_UMBRAL_LLUVIA)
        )
        or 0
    )
    accidentes_tolima = (
        db.scalar(
            select(func.sum(Accidente.cantidad)).where(Accidente.departamento == "TOLIMA")
        )
        or 0
    )
    trafico_alvarado = (
        db.scalar(
            select(func.sum(TraficoVehicular.cantidad_trafico)).where(TraficoVehicular.peaje == "ALVARADO")
        )
        or 0
    )
    return {
        "total_servicios": total_servicios,
        "porcentaje_outliers_costo": round(total_outliers / total_servicios * 100, 2) if total_servicios else 0,
        "total_servicios_grua": total_gruas,
        "citas_pendientes": citas_pendientes,
        "dias_lluvia_extrema": dias_lluvia_extrema,
        "accidentes_tolima_total": accidentes_tolima,
        "trafico_peaje_alvarado_total": trafico_alvarado,
        "umbral_lluvia_extrema_mm": META_UMBRAL_LLUVIA,
    }


@router.get("/cruce-lluvia-accidentes")
def cruce_lluvia_accidentes(db: DbDep, _: CurrentUser = es_admin):
    """Servicios en días de lluvia extrema vs siniestralidad Tolima (concepto de FASE_1)."""
    servicios_lluvia = (
        db.scalar(
            select(func.count())
            .select_from(ServicioReparacion)
            .join(ClimaNOAA, ClimaNOAA.fecha == ServicioReparacion.fecha_servicio)
            .where(ClimaNOAA.es_lluvia_extrema.is_(True))
        )
        or 0
    )
    accidentes_2024 = (
        db.scalar(
            select(func.sum(Accidente.cantidad)).where(
                Accidente.departamento == "TOLIMA", func.date_part("year", Accidente.fecha_hecho) == 2024
            )
        )
        or 0
    )
    return {
        "servicios_en_dias_lluvia_extrema": servicios_lluvia,
        "accidentes_tolima_2024": accidentes_2024,
        "conclusion": "La intersección servicios×clima×siniestralidad permite planear capacidad en temporada de lluvia."
    }