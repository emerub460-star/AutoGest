import io
import json

import qrcode
from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select

from app.api.deps import DbDep
from app.models.vehiculo import Vehiculo
from app.models.servicio import ServicioReparacion

router = APIRouter(prefix="/api/v1/auxilio", tags=["auxilio"])


def _vehiculo_o_404(db, vin: str):
    v = db.scalar(select(Vehiculo).where(Vehiculo.vin == vin.upper()))
    if not v:
        raise HTTPException(status_code=404, detail="VIN no registrado en AutoGest")
    return v


@router.get("/qr/{vin}", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
def qr_vehiculo(vin: str, db: DbDep):
    """FASE_6: QR público con ficha técnica del vehículo (sin datos sensibles)."""
    v = _vehiculo_o_404(db, vin)
    payload = json.dumps(
        {
            "app": "AutoGest",
            "vin": v.vin,
            "placa": v.placa,
            "marca": v.marca,
            "modelo": v.modelo,
            "anio": v.anio,
            "sede": "Ibagué (Tolima)",
            "qr_pub": "ficha-vehicular-autogest",
        },
        ensure_ascii=False,
    )
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")


@router.get("/ficha/{vin}", response_class=Response, responses={200: {"content": {"text/html": {}}}})
def ficha_vehiculo(vin: str, db: DbDep):
    v = _vehiculo_o_404(db, vin)
    servicios = list(
        db.scalars(
            select(ServicioReparacion)
            .where(ServicioReparacion.id_vehiculo == v.id_vehiculo)
            .order_by(ServicioReparacion.fecha_servicio.desc())
            .limit(5)
        ).all()
    )
    filas = "".join(
        f"<li>{s.fecha_servicio} · {s.tipo_servicio} · ${float(s.costo_total):.2f}</li>" for s in servicios
    )
    html = f"""
    <!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Ficha AutoGest</title>
    <style>body{{font-family:sans-serif;margin:2rem}}h1{{color:#0f766e}}li{{margin:.4rem 0}}</style></head>
    <body><h1>AutoGest — Ficha del vehículo</h1>
    <p><strong>Placa:</strong> {v.placa} | <strong>VIN:</strong> {v.vin}</p>
    <p><strong>{v.marca} {v.modelo}</strong> · año {v.anio} · {v.tipo_combustible or 's/d'}</p>
    <p>Kilometraje registrado: {v.kilometraje_actual} km</p>
    <h2>Últimos servicios</h2><ul>{filas or '<li>Sin servicios registrados</li>'}</ul>
    <p><small>Documento público generado por AutoGest (Ibagué, Tolima).</small></p>
    </body></html>"""
    return Response(content=html, media_type="text/html; charset=utf-8")