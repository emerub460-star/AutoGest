from pydantic import BaseModel, ConfigDict, Field


class VehiculoBase(BaseModel):
    placa: str = Field(min_length=5, max_length=15)
    vin: str | None = Field(default=None, max_length=17)
    marca: str
    modelo: str
    anio: int = Field(ge=1950, le=2035)
    tipo_combustible: str | None = None
    kilometraje_actual: int = 0


class VehiculoCrear(VehiculoBase):
    id_cliente: int | None = None


class VehiculoUpdate(BaseModel):
    tipo_combustible: str | None = None
    kilometraje_actual: int | None = None


class VehiculoKilometraje(BaseModel):
    kilometraje_actual: int = Field(ge=0)


class VehiculoRead(VehiculoBase):
    model_config = ConfigDict(from_attributes=True)

    id_vehiculo: int
    id_cliente: int