from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep
from app.core.security import create_access_token, hash_password, verify_password
from app.models.usuario import Usuario
from app.schemas.auth import Token, UsuarioRegistro
from app.schemas.usuario import UsuarioRead

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def registrar(datos: UsuarioRegistro, db: DbDep):
    existe = db.scalar(select(Usuario).where(Usuario.email == datos.email.lower()))
    if existe:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado")
    usuario = Usuario(
        nombre_completo=datos.nombre_completo,
        email=datos.email.lower(),
        password_hash=hash_password(datos.password),
        telefono=datos.telefono,
        rol="CLIENTE",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    from app.db.database import SessionLocal

    with SessionLocal() as session:
        usuario = session.scalar(select(Usuario).where(Usuario.email == form.username.lower()))
        if not usuario or not verify_password(form.password, usuario.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o contraseña incorrectos")
        if not usuario.activo:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")
        token = create_access_token(usuario.id_usuario, usuario.rol)
        return Token(
            access_token=token,
            id_usuario=usuario.id_usuario,
            nombre_completo=usuario.nombre_completo,
            email=usuario.email,
            rol=usuario.rol,
        )


@router.get("/me", response_model=UsuarioRead)
def me(usuario: CurrentUser):
    return usuario