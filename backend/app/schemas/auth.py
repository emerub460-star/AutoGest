from typing import Literal

from pydantic import BaseModel, EmailStr, field_validator

Rol = Literal["CLIENTE", "MECANICO", "RECEPCION", "ADMIN"]


class UsuarioRegistro(BaseModel):
    nombre_completo: str
    email: EmailStr
    password: str
    telefono: str | None = None

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v


class UsuarioCrear(UsuarioRegistro):
    rol: Rol = "CLIENTE"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id_usuario: int
    nombre_completo: str
    email: str
    rol: str