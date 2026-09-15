from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class GruaCrear(BaseModel):
    id_servicio: int | None = None
    aplica_grua: bool = True
    conductor_grua: str | None = "No aplica"
    ubicacion_origen: str = "No aplica"
    latitud_origen: Decimal | None = None
    longitud_origen: Decimal | None = None


class GruaEstado(BaseModel):
    estado: str


class GruaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_grua: int
    id_servicio: int | None = None
    aplica_grua: bool
    conductor_grua: str | None = None
    ubicacion_origen: str | None = None
    latitud_origen: Decimal | None = None
    longitud_origen: Decimal | None = None
    estado: str