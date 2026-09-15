from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ClimaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fecha: date
    estacion_id: str
    precipitacion_mm: Decimal
    temp_max_c: Decimal | None = None
    temp_min_c: Decimal | None = None
    es_lluvia_extrema: bool
    imputado_mediana: bool = False


class AlertaClima(BaseModel):
    fecha: date
    precipitacion_mm: Decimal
    umbral_mm: Decimal
    tipo: str = "LLUVIA_EXTREMA"