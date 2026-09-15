from datetime import datetime

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep, require_roles
from app.models.cita import Cita
from app.models.sede import SedeTaller
from app.schemas.cita import CitaCrear, CitaEstado, CitaRead

router = APIRouter(prefix="/api/v1/citas", tags=["citas"])

GESTIONA = require_roles("CLIENTE", "RECEPCION", "ADMIN")

ESTADOS = {"PENDIENTE", "CONFIRMADA", "REPROGRAMADA", "CANCELADA", "FINALIZADA"}


@router.get("/", response_model=list[CitaRead])
def listar_citas(db: DbDep, usuario: CurrentUser):
    q = select(Cita).order_by(Cita.fecha_hora)
    if usuario.rol == "CLIENTE":
        q = q.where(Cita.id_cliente == usuario.id_usuario)
    return list(db.scalars(q).all())


@router.post("/", response_model=CitaRead, status_code=201)
def crear_cita(datos: CitaCrear, db: DbDep, usuario: CurrentUser):
    if not db.get(SedeTaller, datos.id_sede):
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    cita = Cita(
        id_cliente=usuario.id_usuario,
        id_vehiculo=datos.id_vehiculo,
        id_sede=datos.id_sede,
        fecha_hora=datos.fecha_hora,
        motivo=datos.motivo,
        estado="PENDIENTE",
    )
    db.add(cita)
    db.commit()
    db.refresh(cita)
    return cita


@router.patch("/{id_cita}/estado", response_model=CitaRead)
def cambiar_estado_cita(id_cita: int, datos: CitaEstado, db: DbDep, usuario: CurrentUser):
    """RF-05: confirmar/cancelar/reprogramar."""
    cita = db.get(Cita, id_cita)
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    if usuario.rol == "CLIENTE" and cita.id_cliente != usuario.id_usuario:
        raise HTTPException(status_code=403, detail="La cita no pertenece a este cliente")
    if datos.estado.upper() not in ESTADOS:
        raise HTTPException(status_code=422, detail="Estado no válido")
    cita.estado = datos.estado.upper()
    db.commit()
    db.refresh(cita)
    return cita