from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep, require_roles
from app.core.security import hash_password
from app.models.usuario import Usuario
from app.schemas.auth import UsuarioCrear
from app.schemas.usuario import UsuarioRead, UsuarioRolUpdate

router = APIRouter(prefix="/api/v1/usuarios", tags=["usuarios"])
es_admin = require_roles("ADMIN")


@router.get("/", response_model=list[UsuarioRead])
def listar_usuarios(db: DbDep, _: CurrentUser = es_admin, activos: bool | None = None):
    q = select(Usuario).order_by(Usuario.id_usuario)
    if activos is not None:
        q = q.where(Usuario.activo.is_(activos))
    return list(db.scalars(q).all())


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCrear, db: DbDep, _: CurrentUser = es_admin):
    existe = db.scalar(select(Usuario).where(Usuario.email == datos.email.lower()))
    if existe:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado")
    usuario = Usuario(
        nombre_completo=datos.nombre_completo,
        email=datos.email.lower(),
        password_hash=hash_password(datos.password),
        telefono=datos.telefono,
        rol=datos.rol,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{id_usuario}/rol", response_model=UsuarioRead)
def cambiar_rol(id_usuario: int, datos: UsuarioRolUpdate, db: DbDep, _: CurrentUser = es_admin):
    if datos.rol not in {"CLIENTE", "MECANICO", "RECEPCION", "ADMIN"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rol no válido")
    usuario = db.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    usuario.rol = datos.rol
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{id_usuario}/activo", response_model=UsuarioRead)
def toggle_activo(id_usuario: int, db: DbDep, _: CurrentUser = es_admin):
    usuario = db.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    usuario.activo = not usuario.activo
    db.commit()
    db.refresh(usuario)
    return usuario