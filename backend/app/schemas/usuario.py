from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    nombre_completo: str
    email: EmailStr
    telefono: str | None = None
    rol: str
    activo: bool
    creado_en: datetime | None = None


class UsuarioRolUpdate(BaseModel):
    rol: str