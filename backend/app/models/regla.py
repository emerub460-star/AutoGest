from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ReglaIQR(Base):
    __tablename__ = "reglas_iqr_servicio"

    id_regla: Mapped[int] = mapped_column(primary_key=True)
    tipo_servicio: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    q1_costo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    q3_costo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    iqr_costo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    limite_inferior: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    limite_superior: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)