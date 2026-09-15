from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep
from app.models.vehiculo import Vehiculo
from app.schemas.vehiculo import VehiculoCrear, VehiculoKilometraje, VehiculoRead, VehiculoUpdate

router = APIRouter(prefix="/api/v1/vehiculos", tags=["vehiculos"])

ROLES_STAFF = ("RECEPCION", "MECANICO", "ADMIN")


def _get_o_404(db, id_vehiculo: int) -> Vehiculo:
    v = db.get(Vehiculo, id_vehiculo)
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    return v


def _permiso(db, v: Vehiculo, usuario) -> None:
    if usuario.rol in ROLES_STAFF:
        return
    if v.id_cliente != usuario.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="El vehículo no pertenece a este cliente")


@router.get("/", response_model=list[VehiculoRead])
def listar_vehiculos(db: DbDep, usuario: CurrentUser):
    q = select(Vehiculo).order_by(Vehiculo.placa)
    if usuario.rol not in ROLES_STAFF:
        q = q.where(Vehiculo.id_cliente == usuario.id_usuario)
    return list(db.scalars(q).all())


@router.get("/{id_vehiculo}", response_model=VehiculoRead)
def obtener_vehiculo(id_vehiculo: int, db: DbDep, usuario: CurrentUser):
    v = _get_o_404(db, id_vehiculo)
    _permiso(db, v, usuario)
    return v


@router.post("/", response_model=VehiculoRead, status_code=status.HTTP_201_CREATED)
def crear_vehiculo(datos: VehiculoCrear, db: DbDep, usuario: CurrentUser):
    if db.scalar(select(Vehiculo).where(Vehiculo.placa == datos.placa.upper())):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ya existe un vehículo con esa placa (TC-002)"
        )
    id_cliente = usuario.id_usuario if usuario.rol == "CLIENTE" else datos.id_cliente
    if id_cliente is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Envíe id_cliente o use rol CLIENTE")
    v = Vehiculo(
        id_cliente=id_cliente,
        placa=datos.placa.upper(),
        vin=datos.vin,
        marca=datos.marca,
        modelo=datos.modelo,
        anio=datos.anio,
        tipo_combustible=datos.tipo_combustible,
        kilometraje_actual=datos.kilometraje_actual,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


@router.patch("/{id_vehiculo}/kilometraje", response_model=VehiculoRead)
def actualizar_kilometraje(id_vehiculo: int, datos: VehiculoKilometraje, db: DbDep, usuario: CurrentUser):
    """FASE_4: controla regresión de kilometraje (TC asociado a RNF)."""
    v = _get_o_404(db, id_vehiculo)
    _permiso(db, v, usuario)
    if datos.kilometraje_actual < v.kilometraje_actual:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El kilometraje no puede ser menor al registrado ({v.kilometraje_actual})",
        )
    v.kilometraje_actual = datos.kilometraje_actual
    db.commit()
    db.refresh(v)
    return v