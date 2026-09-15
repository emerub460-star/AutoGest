from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep, require_roles
from app.models.grua import ServicioGrua
from app.schemas.grua import GruaCrear, GruaEstado, GruaRead

router = APIRouter(prefix="/api/v1/gruas", tags=["gruas"])

SOLICITA = require_roles("CLIENTE", "RECEPCION", "ADMIN")
GESTIONA = require_roles("RECEPCION", "ADMIN")

ESTADOS = {"NO_APLICA", "SOLICITADA", "EN_CAMINO", "REMOLCANDO", "FINALIZADA"}


@router.post("/", response_model=GruaRead, status_code=status.HTTP_201_CREATED)
def solicitar_grua(datos: GruaCrear, db: DbDep, _: CurrentUser = SOLICITA):
    """RF-03 + RNF-03: GPS configurable o 'No aplica' (marcar MAR, no inventar)."""
    g = ServicioGrua(
        id_servicio=datos.id_servicio,
        aplica_grua=datos.aplica_grua,
        conductor_grua="No aplica",
        ubicacion_origen=datos.ubicacion_origen or "No aplica",
        latitud_origen=datos.latitud_origen,
        longitud_origen=datos.longitud_origen,
        estado="SOLICITADA",
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


@router.get("/", response_model=list[GruaRead])
def listar_gruas(db: DbDep, estado: str | None = None, limite: int = Query(50, le=500)):
    q = select(ServicioGrua).order_by(ServicioGrua.id_grua.desc()).limit(limite)
    if estado:
        q = q.where(ServicioGrua.estado == estado.upper())
    return list(db.scalars(q).all())


@router.get("/{id_grua}", response_model=GruaRead)
def obtener_grua(id_grua: int, db: DbDep):
    g = db.get(ServicioGrua, id_grua)
    if not g:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de grúa no encontrada")
    return g


@router.patch("/{id_grua}/estado", response_model=GruaRead)
def cambiar_estado_grua(id_grua: int, datos: GruaEstado, db: DbDep, _: CurrentUser = GESTIONA):
    g = db.get(ServicioGrua, id_grua)
    if not g:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de grúa no encontrada")
    if datos.estado.upper() not in ESTADOS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Estado no válido")
    g.estado = datos.estado.upper()
    db.commit()
    db.refresh(g)
    return g