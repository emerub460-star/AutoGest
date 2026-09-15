from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep
from app.core.config import settings
from app.models.clima import ClimaNOAA
from app.models.regla import ReglaIQR
from app.models.vehiculo import Vehiculo
from app.schemas.ia import FactorRiesgo, RiesgoIn, RiesgoOut

router = APIRouter(prefix="/api/v1/ia", tags=["ia"])

TIPO_PESO = {
    "Oil Change": 1,
    "Battery Replacement": 2,
    "Brake Service": 3,
    "Tire Replacement": 3,
    "Transmission Repair": 4,
    "Engine Repair": 4,
    "Towing": 5,
}


@router.post("/evaluar-riesgo", response_model=RiesgoOut)
def evaluar_riesgo(datos: RiesgoIn, db: DbDep, _: CurrentUser = None):
    """FASE_5: riesgo preventivo = bandas IQR por tipo de servicio + lluvia extrema reciente.

    Si OPENAI_API_KEY está configurada, enriquece la recomendación con OpenAI (best-effort).
    """
    vehiculo = db.get(Vehiculo, datos.id_vehiculo)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    regla = db.scalar(select(ReglaIQR).where(ReglaIQR.tipo_servicio == datos.tipo_servicio))
    if not regla:
        raise HTTPException(status_code=422, detail="Tipo de servicio sin regla IQR")

    factores: list[FactorRiesgo] = []
    puntaje = 0

    costo = datos.costo_total
    if costo is not None:
        es_outlier = costo < float(regla.limite_inferior) or costo > float(regla.limite_superior)
        if es_outlier:
            puntaje += 3
            factores.append(
                FactorRiesgo(
                    nombre="costo_atipico",
                    detalle=f"Costo fuera de la banda IQR ({regla.limite_inferior}–{regla.limite_superior}) para {datos.tipo_servicio}",
                    nivel="alto",
                )
            )
        else:
            factores.append(
                FactorRiesgo(nombre="costo_dentro_banda", detalle="Costo dentro de la banda IQR", nivel="bajo")
            )

    peso = TIPO_PESO.get(datos.tipo_servicio, 2)
    puntaje += peso
    factores.append(
        FactorRiesgo(nombre="tipo_servicio", detalle=f"Complejidad del servicio: {datos.tipo_servicio}", nivel="medio" if peso >= 3 else "bajo")
    )

    lluvia_reciente = list(
        db.scalars(
            select(ClimaNOAA)
            .where(ClimaNOAA.es_lluvia_extrema.is_(True))
            .order_by(ClimaNOAA.fecha.desc())
            .limit(5)
        ).all()
    )
    if len(lluvia_reciente) >= 3:
        puntaje += 2
        factores.append(
            FactorRiesgo(
                nombre="clima_adverso",
                detalle="Varios días recientes con lluvia extrema (>7.5 mm): mayor riesgo en vías y remolques",
                nivel="alto",
            )
        )
    else:
        factores.append(
            FactorRiesgo(nombre="clima", detalle="Condiciones climáticas recientes sin alerta extrema", nivel="bajo")
        )

    if puntaje >= 8:
        nivel, recomendacion = "ALTO", "Programar inspección preventiva prioritaria y verificar estado de llantas/frenos."
    elif puntaje >= 5:
        nivel, recomendacion = "MEDIO", "Programar revisión preventiva; monitorear próximo kilometraje de servicio."
    else:
        nivel, recomendacion = "BAJO", "Mantenimiento preventivo ordinario, sin señales de alerta."

    fuente = "reglas_iqr+clima"

    if datos.usar_ia and settings.openai_api_key:
        try:
            recomendacion = _consultar_openai(datos, vehiculo, regla, nivel, lluvia_reciente)
            fuente = "openai"
        except Exception:
            fuente = "reglas_iqr+clima (openai no disponible)"

    return RiesgoOut(
        id_vehiculo=datos.id_vehiculo,
        tipo_servicio=datos.tipo_servicio,
        nivel_riesgo=nivel,
        puntaje=puntaje,
        factores=factores,
        recomendacion=recomendacion,
        fuente=fuente,
    )


def _consultar_openai(datos: RiesgoIn, vehiculo: Vehiculo, regla: ReglaIQR, nivel: str, lluvia: list) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    lluvia_msj = f"{len(lluvia)} días de lluvia extrema recientes en Ibagué." if lluvia else "Sin lluvia extrema reciente."
    prompt = (
        f"Vehículo {vehiculo.marca} {vehiculo.modelo} ({vehiculo.anio}), placa {vehiculo.placa}. "
        f"Servicio {datos.tipo_servicio}, costo {datos.costo_total}, bandas IQR {regla.limite_inferior}-{regla.limite_superior}. "
        f"Riesgo heurístico {nivel}. {lluvia_msj} "
        "Da una recomendación preventiva concreta en <=120 caracteres, en español."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Eres un asesor técnico de taller automotriz."}, {"role": "user", "content": prompt}],
        max_tokens=120,
    )
    return resp.choices[0].message.content.strip()