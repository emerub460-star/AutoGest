from decimal import Decimal

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class SedeTaller(Base):
    __tablename__ = "sedes_taller"

    id_sede: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    direccion: Mapped[str] = mapped_column(Text, nullable=False)
    latitud: Mapped[Decimal | None] = mapped_column(Numeric(10, 8))
    longitud: Mapped[Decimal | None] = mapped_column(Numeric(11, 8))