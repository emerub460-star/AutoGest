from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

EstadoServicio = Enum(
    "EN_DIAGNOSTICO", "EN_REPARACION", "ESPERA_REPUESTOS", "COMPLETADO", "ENTREGADO",
    name="estado_servicio",
)


class ServicioReparacion(Base):
    __tablename__ = "servicios_reparacion"

    id_servicio: Mapped[int] = mapped_column(primary_key=True)
    id_vehiculo: Mapped[int] = mapped_column(ForeignKey("vehiculos.id_vehiculo"), nullable=False)
    id_mecanico: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"))
    id_sede: Mapped[int] = mapped_column(ForeignKey("sedes_taller.id_sede"), nullable=False)
    fecha_servicio: Mapped[date] = mapped_column(
        Date, ForeignKey("clima_noaa.fecha"), nullable=False
    )
    tipo_servicio: Mapped[str] = mapped_column(String(80), nullable=False)
    nivel_urgencia: Mapped[str] = mapped_column(String(20), nullable=False)
    duracion_horas: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    costo_mano_obra: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    costo_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    requirio_grua: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    estado: Mapped[str] = mapped_column(
        EstadoServicio, nullable=False, default="EN_DIAGNOSTICO", server_default="EN_DIAGNOSTICO"
    )
    es_outlier_costo: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    observaciones_tecnicas: Mapped[str | None] = mapped_column(Text)