from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Computed, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ClimaNOAA(Base):
    __tablename__ = "clima_noaa"

    fecha: Mapped[date] = mapped_column(Date, primary_key=True)
    estacion_id: Mapped[str] = mapped_column(String(20), server_default="COM00080214")
    precipitacion_mm: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, server_default="0.00")
    temp_max_c: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    temp_min_c: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    es_lluvia_extrema: Mapped[bool] = mapped_column(
        Boolean, Computed("precipitacion_mm > 7.5", persisted=True), nullable=False
    )
    imputado_mediana: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")