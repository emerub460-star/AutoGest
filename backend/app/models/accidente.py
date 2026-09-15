from datetime import date

from sqlalchemy import Date, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Accidente(Base):
    __tablename__ = "accidentes"
    __table_args__ = (
        Index("idx_accidentes_fecha", "fecha_hecho"),
        Index("idx_accidentes_muni", "municipio"),
    )

    id_accidente: Mapped[int] = mapped_column(primary_key=True)
    fecha_hecho: Mapped[date] = mapped_column(Date, nullable=False)
    cod_depto: Mapped[str] = mapped_column(String(2), nullable=False)
    departamento: Mapped[str] = mapped_column(String(60), nullable=False)
    cod_muni: Mapped[str] = mapped_column(String(5), nullable=False)
    municipio: Mapped[str] = mapped_column(String(80), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)