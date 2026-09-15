"""
Sesión 2 · Minería de Datos · UNIMINUTO Ibagué
AutoGest — Un dato, tres puertas de entrada + fuentes externas
1) Cargar el mismo dataset en CSV y JSON (SQLite a partir del CSV)
2) Descargar clima real Ibagué (PERALES) desde API pública open-meteo
Ejecutar: python sesiones/s2/carga_fuentes_autogest.py
"""
from pathlib import Path
import json
import sqlite3
import urllib.request
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RUTA_RAW = RAIZ / "data_pipeline" / "data" / "raw" / "enhanced_motor_vehicle_repair_towing_dataset.csv"
RUTA_DATOS = Path(__file__).resolve().parent / "datasets"
RUTA_CSV = RUTA_DATOS / "servicios_taller.csv"
RUTA_JSON = RUTA_DATOS / "servicios_taller.json"
RUTA_DB = RUTA_DATOS / "servicios_taller.db"
RUTA_CLIMA = RAIZ / "data_pipeline" / "data" / "raw" / "clima_ibague_openmeteo.csv"

RUTA_DATOS.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────────────
# Preparar muestra idéntica en 3 formatos (curso: ventas_tienda)
# ────────────────────────────────────────────────────────────────
muestra = pd.DataFrame([
    {"id_servicio": 1, "fecha": "2023-05-14", "tipo_servicio": "Oil Change",     "costo_total": 77.82, "sede": "Ibagué"},
    {"id_servicio": 2, "fecha": "2020-07-08", "tipo_servicio": "Tire Replacement", "costo_total": 135.97, "sede": "Espinal"},
    {"id_servicio": 3, "fecha": "2023-09-16", "tipo_servicio": "Battery Replacement", "costo_total": 329.70, "sede": "Ibagué"},
    {"id_servicio": 4, "fecha": "2021-01-12", "tipo_servicio": "Brake Replacement", "costo_total": 412.50, "sede": "Girardot"},
    {"id_servicio": 5, "fecha": "2022-11-02", "tipo_servicio": "Transmission Repair", "costo_total": 1190.00, "sede": "Ibagué"},
])

# CSV
RUTA_CSV.write_text(muestra.to_csv(index=False), encoding="utf-8")
# JSON
RUTA_JSON.write_text(muestra.to_json(orient="records", force_ascii=False), encoding="utf-8")
# SQLite
if RUTA_DB.exists():
    RUTA_DB.unlink()
con = sqlite3.connect(RUTA_DB)
muestra.to_sql("servicios", con, if_exists="replace", index=False)
con.close()

print("=" * 62)
print("PARTE A · El MISMO dato en 3 formatos")
for nombre, ruta in [("CSV", RUTA_CSV), ("JSON", RUTA_JSON), ("SQLite", RUTA_DB)]:
    if nombre == "CSV":
        dfx = pd.read_csv(ruta)
    elif nombre == "JSON":
        dfx = pd.read_json(ruta)
    else:
        with sqlite3.connect(ruta) as c:
            dfx = pd.read_sql("SELECT * FROM servicios", c)
    print(f"\n[{nombre}] shape={dfx.shape}")
    print(dfx.dtypes.to_string())

print("\n--- ¿Por qué 'fecha' se infiere igual en los 3 formatos? ---")
print("Porque en los 3 casos viene como texto ISO 'YYYY-MM-DD' y pandas la")
print("lee como object/string. No se convierte a datetime hasta que se decida,")
print("lo que implica que no se pueden hacer operaciones temporales sin parsear.")

# ────────────────────────────────────────────────────────────────
print("\n" + "=" * 62)
print("PARTE B · Ingesta del dataset completo real (2M registros)")

# Leer solo columnas necesarias para no cargar toda la memoria en demo
cols = ["Service Type", "Repair Date", "Total Cost", "Service Duration Hours",
        "Urgency Level", "Follow-up Needed", "Mileage at Service", "Payment Method"]
df = pd.read_csv(RUTA_RAW, usecols=cols, low_memory=False)
print(f"Dimensiones: {df.shape[0]:,} filas × {df.shape[1]} columnas")
print(df.dtypes.to_string())
print("\nPrimeras 5 filas:")
print(df.head().to_string())
print("\nNulos por columna:")
print(df.isna().sum()[df.isna().sum() > 0].to_string())
print(f"Duplicados: {int(df.duplicated().sum())}")

# ────────────────────────────────────────────────────────────────
print("\n" + "=" * 62)
print("PARTE C · Fuente externa pública: clima Ibagué (open-meteo API)")

# Rango de fechas disponible en el dataset real
fechas = pd.to_datetime(df["Repair Date"].dropna(), errors="coerce")
min_date, max_date = fechas.min().strftime("%Y-%m-%d"), fechas.max().strftime("%Y-%m-%d")
print(f"Rango de fechas del dataset: {min_date} a {max_date}")

# PERALES: aeropuerto de Ibagué
LAT, LON = 4.4219, -75.1331
url = (
    "https://archive-api.open-meteo.com/v1/archive"
    f"?latitude={LAT}&longitude={LON}"
    f"&start_date={min_date}&end_date={max_date}"
    "&daily=precipitation_sum,temperature_2m_max,temperature_2m_min"
    "&timezone=America%2FBogota"
)
with urllib.request.urlopen(url, timeout=60) as r:
    data = json.load(r)

clima = pd.DataFrame(data["daily"])
clima.columns = ["fecha", "precipitacion_mm", "temp_max_c", "temp_min_c"]
clima["es_lluvia_extrema"] = clima["precipitacion_mm"].fillna(0) > 7.5
print(f"Clima descargado: {clima.shape[0]} días ({min_date} a {max_date})")
print(clima.head().to_string())
print(f"Días con lluvia extrema (>7.5mm): {int(clima['es_lluvia_extrema'].sum())}")

clima.to_csv(RUTA_CLIMA, index=False)
print(f"Guardado en: {RUTA_CLIMA}")

# ────────────────────────────────────────────────────────────────
print("\n" + "=" * 62)
print("PARTE D · Unión de fuentes (left join servicios × clima)")

df["fecha"] = pd.to_datetime(df["Repair Date"], errors="coerce").dt.date
clima["fecha"] = pd.to_datetime(clima["fecha"]).dt.date
union = df.merge(clima, on="fecha", how="left")
print(f"Filas tras left join: {union.shape[0]:,} (no se pierden servicios)")
print(f"Días sin dato climático (medidos en el join): {int(union['precipitacion_mm'].isna().sum()):,}")
print(f"Del total: {union['es_lluvia_extrema'].sum():,} servicios en día de lluvia extrema")

print("\nFIN SESIÓN 2")