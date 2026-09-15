from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

EstadoCita = Enum(
    "PENDIENTE", "CONFIRMADA", "REPROGRAMADA", "CANCELADA", "FINALIZADA", name="estado_cita"
)


class Cita(Base):
    __tablename__ = "citas"

    id_cita: Mapped[int] = mapped_column(primary_key=True)
    id_cliente: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False
    )
    id_vehiculo: Mapped[int | None] = mapped_column(ForeignKey("vehiculos.id_vehiculo"))
    id_sede: Mapped[int] = mapped_column(ForeignKey("sedes_taller.id_sede"), nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    motivo: Mapped[str | None] = mapped_column(String(255))
    estado: Mapped[str] = mapped_column(
        EstadoCita, nullable=False, default="PENDIENTE", server_default="PENDIENTE"
    )