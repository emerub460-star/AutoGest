FASE_6_Emergencias_Geolocalizacion_y_Frontend.md

# AutoGest — Fase 6: Emergencias, Geolocalización y Frontend

## 1. Ficha Técnica y Código QR de Auxilio
Cada vehículo posee un código QR único que apunta a una vista pública optimizada[cite: 3]. Muestra datos de remolque (tracción, transmisión), contactos de emergencia y seguro, excluyendo intencionalmente información personal privada[cite: 3].

```python
def generar_qr_vehiculo(id_vehiculo: int, db: Session) -> str:
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id_vehiculo == id_vehiculo).first()
    url_publica = f"[https://autogest.app/auxilio/qr/](https://autogest.app/auxilio/qr/){vehiculo.vin}"
    img = qrcode.make(url_publica)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")