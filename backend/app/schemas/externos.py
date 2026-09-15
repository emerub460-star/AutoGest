from datetime import date

from pydantic import BaseModel, ConfigDict


class AccidenteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_accidente: int
    fecha_hecho: date
    cod_depto: str
    departamento: str
    cod_muni: str
    municipio: str
    cantidad: int


class AccidenteAgregado(BaseModel):
    periodo: date
    departamento: str
    municipio: str
    total_accidentes: int


class TraficoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_trafico: int
    id_peaje: int
    peaje: str
    categoria_tarifa: str
    periodo_desde: date
    periodo_hasta: date
    valor_tarifa_cop: object
    cantidad_trafico: int
    cantidad_evasores: int
    cantidad_exentos787: int