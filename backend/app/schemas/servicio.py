from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RegistroGrua(BaseModel):
    aplica: bool = True
    ubicacion_origen: str = "No aplica"
    latitud_origen: Decimal | None = None
    longitud_origen: Decimal | None = None


class ServicioCrear(BaseModel):
    id_vehiculo: int
    fecha_servicio: date
    tipo_servicio: str
    nivel_urgencia: str = "MEDIA"
    duracion_horas: Decimal
    costo_mano_obra: Decimal
    costo_total: Decimal
    observaciones_tecnicas: str | None = None
    grua: RegistroGrua | None = None


class ServicioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_servicio: int
    id_vehiculo: int
    id_mecanico: int | None = None
    id_sede: int
    fecha_servicio: date
    tipo_servicio: str
    nivel_urgencia: str
    duracion_horas: Decimal
    costo_mano_obra: Decimal
    costo_total: Decimal
    requirio_grua: bool
    estado: str
    es_outlier_costo: bool
    observaciones_tecnicas: str | None = None


class ServicioEstado(BaseModel):
    estado: str


class ValidacionCostoIn(BaseModel):
    tipo_servicio: str
    costo_total: Decimal


class ValidacionCostoOut(BaseModel):
    tipo_servicio: str
    costo_total: Decimal
    q1_costo: Decimal
    q3_costo: Decimal
    iqr_costo: Decimal
    limite_inferior: Decimal
    limite_superior: Decimal
    es_outlier_costo: bool