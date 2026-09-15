"""
Sesión 3 · Minería de Datos · UNIMINUTO Ibagué
AutoGest — Pipeline de limpieza del dataset de taller (MotorVehicleRepairTowing)
Replica el pipeline del curso sobre el dataset del PROYECTO:
 1. Diagnóstico (nulos, duplicados, categorías)
 2. Nulos estructurales MAR de grúa  -> bandera "No aplica"
 3. Duplicados y categorías
 4. IQR segmentado por tipo de servicio (equivalente a reglas_iqr_servicio)
 5. Validación y exportación + bitácora
Ejecutar: python sesiones/s3/limpieza_autogest.py
"""
from pathlib import Path
import unicodedata
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RUTA_RAW = RAIZ / "data_pipeline" / "data" / "raw" / "enhanced_motor_vehicle_repair_towing_dataset.csv"
RUTA_OUT = RAIZ / "data_pipeline" / "data" / "processed" / "motor_vehicle_limpio_propio.csv"
RUTA_BITACORA = RAIZ / "data_pipeline" / "outputs" / "bitacora_limpieza.csv"
RUTA_REGLAS = RAIZ / "data_pipeline" / "outputs" / "reglas_iqr_servicio.csv"

RUTA_OUT.parent.mkdir(parents=True, exist_ok=True)
RUTA_REGLAS.parent.mkdir(parents=True, exist_ok=True)

def titulo(n, texto):
    print(f"\n{'=' * 64}\nPASO {n} · {texto}")

def sin_tildes(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()

def iqr_bounds(serie):
    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    iqr = q3 - q1
    return q1, q3, iqr, q1 - 1.5 * iqr, q3 + 1.5 * iqr

bitacora = []

# ── PASO 0 · Carga y diagnóstico
titulo(0, "CARGA Y DIAGNÓSTICO INICIAL")
df = pd.read_csv(RUTA_RAW, low_memory=False)
filas0 = len(df)
print(f"Filas iniciales: {filas0:,}")
print(f"Dimensiones: {df.shape}")
print("Tipos de datos:")
print(df.dtypes.to_string())

print("\nNulos por columna:")
nulos = df.isna().sum()
print(nulos[nulos > 0].to_string())
print(f"Duplicados exactos: {int(df.duplicated().sum())}")

# ── PASO 1 · Columna 100% nula y columna corrupta
titulo(1, "ELIMINACIÓN DE COLUMNAS INUTILIZABLES")
pct_feedback = df["Customer Feedback"].isna().mean() * 100
df = df.drop(columns=["Customer Feedback"])
bitacora.append({"Columna": "Customer Feedback",
                 "Método aplicado": "ELIMINAR (100% nula)",
                 "Motivo / justificación": f"{pct_feedback:.1f}% nula: no hay señal que imputar",
                 "Filas afectadas": filas0})

vc = df["Service Status"].value_counts()
n_corrupto = int(vc.get("s", 0))
df = df.drop(columns=["Service Status"])
bitacora.append({"Columna": "Service Status",
                 "Método aplicado": "ELIMINAR (corrupta)",
                 "Motivo / justificación": f"{n_corrupto:,}/{filas0:,} filas con 's' (truncamiento ETL)",
                 "Filas afectadas": n_corrupto})
print(f"Customer Feedback: {pct_feedback:.1f}% nula -> eliminada")
print(f"Service Status: {n_corrupto:,} filas corruptas -> eliminada")

# ── PASO 2 · Nulos estructurales MAR de grúa
titulo(2, "NULOS ESTRUCTURALES MAR · GRÚA (RNF-03 'No aplica')")
mask_no_towing = df["Service Type"] != "Towing"
N_NO_TOW = int(mask_no_towing.sum())
for col in ["Tow Location", "Drop-off Location", "Tow Truck Driver"]:
    n_antes = int(df[col].isna().sum())
    assert n_antes == N_NO_TOW, f"{col}: los nulos no coinciden con no-towing"
    df[col] = df[col].fillna("No aplica (servicio sin remolque)")
    df[col + "_es_no_aplica"] = False
    df.loc[mask_no_towing, col + "_es_no_aplica"] = True
    bitacora.append({"Columna": col,
                     "Método aplicado": "CONSTANTE / BANDERA 'No aplica'",
                     "Motivo / justificación": "MAR verificado: el nulo coincide 1:1 con Service Type != Towing",
                     "Filas afectadas": n_antes})
    print(f"{col}: {n_antes:,} nulos MAR -> 'No aplica'")

# Towing Date se deja nula (NaT) — no se inventa una fecha
n_fecha = int(df["Towing Date"].isna().sum())
bitacora.append({"Columna": "Towing Date",
                 "Método aplicado": "SE DEJA NULO (NaT) documentado",
                 "Motivo / justificación": "MAR: no se inventa una fecha para servicios sin remolque",
                 "Filas afectadas": n_fecha})
print(f"Towing Date: {n_fecha:,} nulos MAR documentados, sin imputar")

# ── PASO 3 · Duplicados y categorías
titulo(3, "DUPLICADOS Y CATEGORÍAS")
n_dup_total = int(df.duplicated().sum())
df = df.drop_duplicates().reset_index(drop=True)
bitacora.append({"Columna": "Todas / Service ID",
                 "Método aplicado": "drop_duplicates",
                 "Motivo / justificación": "Eliminar filas 100% duplicadas",
                 "Filas afectadas": n_dup_total})
print(f"Duplicados exactos eliminados: {n_dup_total:,}")

for col in ["Vehicle Type", "Service Type", "Urgency Level", "Payment Method", "Customer Type"]:
    unicos = df[col].str.strip().str.lower().apply(sin_tildes).nunique()
    print(f"  {col}: {df[col].nunique()} valores -> {unicos} estandarizados")
    df[col] = df[col].str.strip().str.title()

# ── PASO 4 · IQR segmentado por tipo de servicio (reglas_iqr_servicio)
titulo(4, f"IQR POR TIPO DE SERVICIO · costos (equivalente a reglas_iqr_servicio)")
reglas = []
for col in ["Total Cost", "Estimated Cost"]:
    flag = col.replace(" ", "_") + "_Outlier_IQR"
    df[flag] = False
    n_out = 0
    for tipo, sub in df.groupby("Service Type")[col]:
        if sub.notna().sum() < 4:
            continue
        q1, q3, iqr, low, high = iqr_bounds(sub)
        idx = sub[(sub < low) | (sub > high)].index
        df.loc[idx, flag] = True
        n_out += len(idx)
        reglas.append({
            "tipo_servicio": tipo,
            "columna_costo": col.replace(" ", "_"),
            "q1_costo": round(q1, 2),
            "q3_costo": round(q3, 2),
            "iqr_costo": round(iqr, 2),
            "limite_inferior": round(low, 2),
            "limite_superior": round(high, 2),
        })
    bitacora.append({"Columna": col,
                     "Método aplicado": f"IQR SEGMENTADO por Service Type -> {flag}",
                     "Motivo / justificación": "El costo depende del tipo de servicio; el IQR global distorsiona",
                     "Filas afectadas": n_out})
    print(f"{col}: {n_out:,} outliers marcados ({n_out/len(df)*100:.3f}%)")

reglas_df = pd.DataFrame(reglas)
reglas_df.to_csv(RUTA_REGLAS, index=False)
print(f"\nReglas IQR guardadas: {RUTA_REGLAS} ({len(reglas_df)} filas)")
print(reglas_df.head(10).to_string())

# ── PASO 5 · Validación y exportación
titulo(5, "VALIDACIÓN Y EXPORTACIÓN")
print(f"Filas finales : {len(df):,}")
print(f"Columnas finales: {df.shape[1]}")
print("Validaciones de rango:")
for col, regla in [("Total Cost", ">=0"), ("Estimated Cost", ">=0"),
                   ("Service Duration Hours", ">0"), ("Mileage at Service", ">=0")]:
    ok = bool((df[col] >= 0).all() if regla == ">=0" else (df[col] > 0).all())
    print(f"  {col} {regla}: {'OK' if ok else 'FALLA'}")

df.to_csv(RUTA_OUT, index=False)
pd.DataFrame(bitacora).to_csv(RUTA_BITACORA, index=False)
print(f"Dataset limpio guardado : {RUTA_OUT} ({len(df):,} filas)")
print(f"Bitácora guardada      : {RUTA_BITACORA} ({len(bitacora)} decisiones)")
print("\nFIN SESIÓN 3")