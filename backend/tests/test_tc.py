"""Casos de prueba TC-001..TC-007 (FASE_7 + integración externa)."""


def test_tc001_auth_sin_token_rechazado(client):
    resp = client.get("/api/v1/vehiculos/")
    assert resp.status_code == 401


def test_tc002_placa_duplicada_rechazada(client, auth_admin):
    payload = {
        "placa": "TC002XR",
        "vin": "TC002VIN000000001",
        "marca": "Chevrolet",
        "modelo": "Spark GT",
        "anio": 2020,
        "kilometraje_actual": 12000,
    }
    r1 = client.post("/api/v1/vehiculos/", json=payload, headers=auth_admin)
    assert r1.status_code == 201
    r2 = client.post("/api/v1/vehiculos/", json=payload, headers=auth_admin)
    assert r2.status_code == 409


def test_tc003_validacion_costo_outlier_iqr(client, auth_admin):
    body = {"tipo_servicio": "Oil Change", "costo_total": 5.0}
    resp = client.post("/api/v1/servicios/validate-costo", json=body, headers=auth_admin)
    assert resp.status_code == 200
    data = resp.json()
    assert data["es_outlier_costo"] is True
    assert data["limite_inferior"] < data["costo_total"] < data["limite_superior"] or data["es_outlier_costo"]


def test_tc004_grua_mar_no_aplica(client, auth_cliente):
    resp = client.post(
        "/api/v1/gruas/",
        json={"aplica_grua": True, "ubicacion_origen": ""},
        headers=auth_cliente,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["ubicacion_origen"] == "No aplica"
    assert data["estado"] == "SOLICITADA"


def test_tc005_alerta_lluvia_extrema(client, auth_cliente):
    resp = client.get("/api/v1/clima/alertas", headers=auth_cliente)
    assert resp.status_code == 200
    datos = resp.json()
    assert len(datos) > 0
    assert all(d["precipitacion_mm"] > d["umbral_mm"] for d in datos)


def test_tc006_accidentes_agregado_municipio(client):
    resp = client.get("/api/v1/accidentes/agregado", params={"municipio": "IBAGUE"})
    assert resp.status_code == 200
    datos = resp.json()
    assert len(datos) > 0
    assert all(d["municipio"].upper() == "IBAGUE" for d in datos)
    assert all(d["total_accidentes"] > 0 for d in datos)


def test_tc007_trafico_agregado_mensual_peaje(client):
    resp = client.get("/api/v1/trafico/resumen", params={"peaje": "ALVARADO"})
    assert resp.status_code == 200
    datos = resp.json()
    assert datos["peaje"] == "ALVARADO"
    assert len(datos["meses"]) > 0
    assert datos["total_trafico_periodo"] > 0