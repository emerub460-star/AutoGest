from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

EstadoGrua = Enum(
    "NO_APLICA", "SOLICITADA", "EN_CAMINO", "REMOLCANDO", "FINALIZADA", name="estado_grua"
)


class ServicioGrua(Base):
    __tablename__ = "servicios_grua"

    id_grua: Mapped[int] = mapped_column(primary_key=True)
    id_servicio: Mapped[int | None] = mapped_column(
        ForeignKey("servicios_reparacion.id_servicio", ondelete="CASCADE"), unique=True
    )
    aplica_grua: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    conductor_grua: Mapped[str] = mapped_column(String(120), server_default="No aplica")
    ubicacion_origen: Mapped[str] = mapped_column(Text, server_default="No aplica")
    latitud_origen: Mapped[Decimal | None] = mapped_column(Numeric(10, 8))
    longitud_origen: Mapped[Decimal | None] = mapped_column(Numeric(11, 8))
    estado: Mapped[str] = mapped_column(
        EstadoGrua, nullable=False, default="SOLICITADA", server_default="SOLICITADA"
    )