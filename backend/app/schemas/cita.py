from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CitaCrear(BaseModel):
    id_vehiculo: int | None = None
    id_sede: int = 1
    fecha_hora: datetime
    motivo: str | None = None


class CitaEstado(BaseModel):
    estado: str


class CitaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cita: int
    id_cliente: int
    id_vehiculo: int | None = None
    id_sede: int
    fecha_hora: datetime
    motivo: str | None = None
    estado: str