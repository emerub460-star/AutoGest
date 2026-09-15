from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Date, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TraficoVehicular(Base):
    __tablename__ = "trafico_vehicular"
    __table_args__ = (
        Index("idx_trafico_peaje", "peaje"),
        Index("idx_trafico_periodo", "periodo_desde", "periodo_hasta"),
    )

    id_trafico: Mapped[int] = mapped_column(primary_key=True)
    id_peaje: Mapped[int] = mapped_column(Integer, nullable=False)
    peaje: Mapped[str] = mapped_column(String(80), nullable=False)
    categoria_tarifa: Mapped[str] = mapped_column(String(20), nullable=False)
    periodo_desde: Mapped[date] = mapped_column(Date, nullable=False)
    periodo_hasta: Mapped[date] = mapped_column(Date, nullable=False)
    valor_tarifa_cop: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cantidad_trafico: Mapped[int] = mapped_column(BigInteger, nullable=False)
    cantidad_evasores: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    cantidad_exentos787: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)