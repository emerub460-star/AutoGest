"""
Sesión 1 · Minería de Datos · UNIMINUTO Ibagué
AutoGest — Exploración inicial + diagnóstico de calidad
Dataset: enhanced_motor_vehicle_repair_towing_dataset.csv (2M+ registros de taller)
Ejecutar: python sesiones/s1/exploracion_autogest.py
"""
from pathlib import Path
import pandas as pd

RUTA_RAW = Path(__file__).resolve().parents[2] / "data_pipeline" / "data" / "raw" / "enhanced_motor_vehicle_repair_towing_dataset.csv"
RUTA_ACTA = Path(__file__).resolve().parent / "ACTA_CONSTITUCION_ANALITICA.md"

# ────────────────────────────────────────────────────────────────
# 1. Carga
# ────────────────────────────────────────────────────────────────
print("Cargando dataset…")
df = pd.read_csv(RUTA_RAW, low_memory=False)
filas, cols = df.shape

print(f"Dimensiones: {filas:,} filas × {cols} columnas")

# ────────────────────────────────────────────────────────────────
# 2. Tipos de datos
# ────────────────────────────────────────────────────────────────
print("\nTipos de datos:")
print(df.dtypes.to_string())

# ────────────────────────────────────────────────────────────────
# 3. Problemas de calidad detectados (mín. 3)
# ────────────────────────────────────────────────────────────────
print("\n--- Diagnóstico de calidad ---")
nulos_por_col = df.isna().sum()
col_con_nulos = nulos_por_col[nulos_por_col > 0]
print("Columnas con nulos:")
print(col_con_nulos.to_string())

total_nulos = int(df.isna().sum().sum())
total_dup = int(df.duplicated().sum())
print(f"\nNulos totales: {total_nulos:,}")
print(f"Filas duplicadas exactas: {total_dup:,}")

# Customer Feedback: 100 % nula
pct_feedback = df["Customer Feedback"].isna().mean() * 100
print(f"\nCustomer Feedback: {pct_feedback:.1f}% nula (columna vacía)")

# Service Status: 99.99995 % tiene 's'
vc_status = df["Service Status"].value_counts()
pct_corrupto = vc_status.get("s", 0) / len(df) * 100
print(f"Service Status: {pct_corrupto:.4f}% contiene solo 's' (columna corrupta)")

# Nulos de grúa = nulos en Service Type != 'Towing'
mask_no_towing = df["Service Type"] != "Towing"
n_towing_cols = ["Towing Date", "Tow Location", "Drop-off Location", "Tow Truck Driver"]
for c in n_towing_cols:
    coincide = int(df[c].isna().sum() == mask_no_towing.sum())
    print(f"{c} nulo == Service Type != Towing: {coincide}")

print("\n--- Valor piso sospechoso ---")
n_piso = int((df["Total Cost"] == 20.00).sum())
print(f"Total Cost == $20.00 exacto: {n_piso:,} filas ({n_piso/len(df)*100:.2f}%)")

# ────────────────────────────────────────────────────────────────
# 4. Tasa de fuga / anomalía / urgencia (segmentos)
# ────────────────────────────────────────────────────────────────
print("\n--- Distribución de urgencia ---")
print(df["Urgency Level"].value_counts(normalize=True).round(3).to_string())

print("\n--- Seguimiento necesario ---")
print(df["Follow-up Needed"].value_counts(normalize=True).round(3).to_string())

print("\n--- Tipo de servicio ---")
print(df["Service Type"].value_counts(normalize=True).round(3).to_string())

# ────────────────────────────────────────────────────────────────
# 5. Pregunta de negocio y objetivo analítico
# ────────────────────────────────────────────────────────────────
pregunta = (
    "¿Cómo se relacionan el tipo y costo de los servicios de taller "
    "con la urgencia y la probabilidad de requerir seguimiento, "
    "para identificar clientes y vehículos de alto riesgo?"
)
objetivo = (
    "Clasificar servicios en función de la probabilidad de requerir "
    "seguimiento y/o presentar costos anómalos (outliers por tipo de servicio), "
    "usando variables numéricas (costo, duración, kilometraje, rating) y "
    "categóricas (tipo servicio, tipo vehículo, forma de pago)."
)
print("\nPregunta de negocio:", pregunta)
print("Objetivo analítico :", objetivo)

# ────────────────────────────────────────────────────────────────
# 6. Clasificación de la tarea de minería
# ────────────────────────────────────────────────────────────────
clasificacion = (
    "El proyecto es de CLASIFICACIÓN SUPERVISADA: la variable objetivo es "
    "'Follow-up Needed' (Yes/No), binaria y supervisada por el historial de "
    "seguimiento real. Complementariamente, la detección de outliers de costo "
    "por tipo de servicio es análisis NO SUPERVISADO (clustering/estadística)."
)
print("\nClasificación:", clasificacion)

# ────────────────────────────────────────────────────────────────
# 7. Exportar acta de constitución analítica
# ────────────────────────────────────────────────────────────────
num_cols = int(df.select_dtypes(include="number").shape[1])
cat_cols = df.shape[1] - num_cols
acta = f"""# Acta de Constitución Analítica — AutoGest
## Sesión 1 · Minería de Datos · 2026-2

**Dataset:** `enhanced_motor_vehicle_repair_towing_dataset.csv`
**Dimensiones:** {filas:,} filas × {cols} columnas

---

## 1. Dimensiones y tipos de datos

- Columnas: {', '.join(df.columns.tolist())}
- Numéricas ({num_cols}) y categóricas/texto ({cat_cols})
- Fechas: `Repair Date` y `Towing Date` (texto, no parseadas aún)

## 2. Problemas de calidad detectados

| # | Problema | Evidencia |
|---|----------|-----------|
| 1 | `Customer Feedback` 100 % nula | {pct_feedback:.1f}% sin ningún valor real — columna vacía |
| 2 | `Service Status` corrupta | {pct_corrupto:.4f}% contiene solo `'s'` (truncamiento ETL), solo 1 fila válida |
| 3 | Nulos estructurales en columnas de grúa (MAR) | `Towing Date`, `Tow Location`, `Drop-off Location`, `Tow Truck Driver` 85.71 % nulos, nulo = Service Type != Towing |
| 4 | Valor piso `$20.00` repetido en Total Cost | {n_piso:,} filas ({n_piso/len(df)*100:.2f}%) — posible tarifa mínima o error |
| 5 | Incoherencias marca/modelo | Ej.: "Harley-Davidson Ram 1500", "BMW Corolla" |
| 6 | Filas duplicadas exactas | {total_dup:,} duplicados |
| 7 | Fechas de grúa inconsistentes | Grúa puede ser posterior a reparación |

## 3. Pregunta de negocio

> {pregunta}

## 4. Objetivo analítico

> {objetivo}

## 5. Clasificación de la tarea de minería

> {clasificacion}

## 6. Segmento más preocupante

- Servicios con Follow-up Needed = Yes: {df['Follow-up Needed'].eq('Yes').mean()*100:.1f}%
- Servicios de Urgency = Emergency: {df['Urgency Level'].eq('Emergency').mean()*100:.1f}%
- Servicio con mayor costo promedio: {df.groupby('Service Type')['Total Cost'].mean().idxmax()}
"""

RUTA_ACTA.write_text(acta, encoding="utf-8")
print(f"\nActa guardada en: {RUTA_ACTA}")
print("FIN SESIÓN 1")
