from datetime import date
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DbDep, require_roles
from app.models.regla import ReglaIQR
from app.models.servicio import ServicioReparacion
from app.models.grua import ServicioGrua
from app.models.sede import SedeTaller
from app.models.vehiculo import Vehiculo
from app.schemas.servicio import (
    ServicioCrear,
    ServicioEstado,
    ServicioRead,
    ValidacionCostoIn,
    ValidacionCostoOut,
)

router = APIRouter(prefix="/api/v1/servicios", tags=["servicios"])

SOLICITA = require_roles("RECEPCION", "MECANICO", "ADMIN")
VERIFICA = require_roles("RECEPCION", "ADMIN")


@router.post("/validate-costo", response_model=ValidacionCostoOut)
def validar_costo(datos: ValidacionCostoIn, db: DbDep, _: CurrentUser = VERIFICA):
    """RF-02: valida costo contra regla IQR del tipo de servicio (costo_mano_obra=Total_Cost)."""
    regla = db.scalar(select(ReglaIQR).where(ReglaIQR.tipo_servicio == datos.tipo_servicio))
    if not regla:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de servicio sin regla IQR")
    es_outlier = datos.costo_total < regla.limite_inferior or datos.costo_total > regla.limite_superior
    return ValidacionCostoOut(
        tipo_servicio=datos.tipo_servicio,
        costo_total=datos.costo_total,
        q1_costo=regla.q1_costo,
        q3_costo=regla.q3_costo,
        iqr_costo=regla.iqr_costo,
        limite_inferior=regla.limite_inferior,
        limite_superior=regla.limite_superior,
        es_outlier_costo=es_outlier,
    )


@router.get("/", response_model=list[ServicioRead])
def listar_servicios(
    db: DbDep,
    usuario: CurrentUser,
    tipo_servicio: str | None = None,
    id_vehiculo: int | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    es_outlier: bool | None = None,
    limite: int = Query(50, le=1000),
):
    q = select(ServicioReparacion).order_by(ServicioReparacion.fecha_servicio.desc()).limit(limite)
    if usuario.rol == "CLIENTE":
        mis_vehiculos = select(Vehiculo.id_vehiculo).where(Vehiculo.id_cliente == usuario.id_usuario)
        q = q.where(ServicioReparacion.id_vehiculo.in_(mis_vehiculos))
    if tipo_servicio:
        q = q.where(ServicioReparacion.tipo_servicio == tipo_servicio)
    if id_vehiculo:
        q = q.where(ServicioReparacion.id_vehiculo == id_vehiculo)
    if desde:
        q = q.where(ServicioReparacion.fecha_servicio >= desde)
    if hasta:
        q = q.where(ServicioReparacion.fecha_servicio <= hasta)
    if es_outlier is not None:
        q = q.where(ServicioReparacion.es_outlier_costo.is_(es_outlier))
    return list(db.scalars(q).all())


@router.get("/tipos", response_model=list[str])
def tipos_servicio(db: DbDep):
    return list(db.scalars(select(ReglaIQR.tipo_servicio)).all())


@router.post("/", response_model=ServicioRead, status_code=status.HTTP_201_CREATED)
def crear_servicio(datos: ServicioCrear, db: DbDep, _: CurrentUser = SOLICITA):
    veh = db.get(Vehiculo, datos.id_vehiculo)
    if not veh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    sede_id = db.scalar(select(SedeTaller.id_sede).limit(1))
    regla = db.scalar(select(ReglaIQR).where(ReglaIQR.tipo_servicio == datos.tipo_servicio))
    if not regla:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tipo de servicio sin regla IQR")
    es_outlier = datos.costo_total < regla.limite_inferior or datos.costo_total > regla.limite_superior

    sv = ServicioReparacion(
        id_vehiculo=datos.id_vehiculo,
        id_sede=sede_id,
        fecha_servicio=datos.fecha_servicio,
        tipo_servicio=datos.tipo_servicio,
        nivel_urgencia=datos.nivel_urgencia,
        duracion_horas=datos.duracion_horas,
        costo_mano_obra=datos.costo_mano_obra,
        costo_total=datos.costo_total,
        requirio_grua=(datos.grua is not None),
        estado="EN_DIAGNOSTICO",
        es_outlier_costo=es_outlier,
        observaciones_tecnicas=datos.observaciones_tecnicas,
    )
    db.add(sv)
    db.flush()

    if datos.grua is not None:
        db.add(
            ServicioGrua(
                id_servicio=sv.id_servicio,
                aplica_grua=datos.grua.aplica,
                conductor_grua="No aplica",
                ubicacion_origen=datos.grua.ubicacion_origen,
                latitud_origen=datos.grua.latitud_origen,
                longitud_origen=datos.grua.longitud_origen,
                estado="SOLICITADA",
            )
        )
    db.commit()
    db.refresh(sv)
    return sv


@router.get("/{id_servicio}", response_model=ServicioRead)
def obtener_servicio(id_servicio: int, db: DbDep, usuario: CurrentUser):
    sv = db.get(ServicioReparacion, id_servicio)
    if not sv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    if usuario.rol == "CLIENTE":
        veh = db.get(Vehiculo, sv.id_vehiculo)
        if not veh or veh.id_cliente != usuario.id_usuario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso sobre este servicio")
    return sv


@router.patch("/{id_servicio}/estado", response_model=ServicioRead)
def cambiar_estado_servicio(id_servicio: int, datos: ServicioEstado, db: DbDep, _: CurrentUser = VERIFICA):
    sv = db.get(ServicioReparacion, id_servicio)
    if not sv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    validos = {"EN_DIAGNOSTICO", "EN_REPARACION", "ESPERA_REPUESTOS", "COMPLETADO", "ENTREGADO"}
    if datos.estado not in validos:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Estado no válido")
    sv.estado = datos.estado
    db.commit()
    db.refresh(sv)
    return sv