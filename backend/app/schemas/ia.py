from typing import Literal

from pydantic import BaseModel


class RiesgoIn(BaseModel):
    id_vehiculo: int
    tipo_servicio: str
    costo_total: float | None = None
    usar_ia: bool = True


class FactorRiesgo(BaseModel):
    nombre: str
    detalle: str
    nivel: Literal["alto", "medio", "bajo"]


class RiesgoOut(BaseModel):
    id_vehiculo: int
    tipo_servicio: str
    nivel_riesgo: str
    puntaje: int
    factores: list[FactorRiesgo]
    recomendacion: str
    fuente: str  # "reglas_iqr+clima" | "openai"