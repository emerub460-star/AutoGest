from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id_vehiculo: Mapped[int] = mapped_column(primary_key=True)
    id_cliente: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False
    )
    vin: Mapped[str | None] = mapped_column(String(17), unique=True)
    placa: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    marca: Mapped[str] = mapped_column(String(50), nullable=False)
    modelo: Mapped[str] = mapped_column(String(50), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_combustible: Mapped[str | None] = mapped_column(String(30))
    kilometraje_actual: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")