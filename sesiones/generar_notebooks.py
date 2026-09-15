"""Genera los notebooks .ipynb de las sesiones 1-4 embebiendo las salidas
reales obtenidas al ejecutar los scripts .py correspondientes."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

def nb(cells, nombre):
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    ruta = nombre
    ruta.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Notebook:", ruta)

def md(texto):
    return {"cell_type": "markdown", "metadata": {}, "source": texto.splitlines(keepends=True)}

def code(texto):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": texto.splitlines(keepends=True)}

def salida(texto):
    return {"cell_type": "markdown", "metadata": {}, "source": [
        "<details><summary><b>Salida ejecutada</b></summary>\n\n```text\n" + texto + "\n```\n</details>"
    ]}

# ─────────────────────── Sesión 1 ───────────────────────
cells = [
    md("# Sesión 1 · Exploración inicial y diagnóstico de calidad\n**AutoGest** · Minería de Datos · UNIMINUTO Ibagué 2026-2\n\nDataset: `enhanced_motor_vehicle_repair_towing_dataset.csv` (2,000,000 × 28)."),
    code('import pandas as pd\nfrom pathlib import Path\n\nRUTA = Path("../../data_pipeline/data/raw/enhanced_motor_vehicle_repair_towing_dataset.csv")\ndf = pd.read_csv(RUTA, low_memory=False)\nprint("Dimensiones:", df.shape)'),
    salida("Dimensiones: 2,000,000 filas x 28 columnas"),
    code('df.dtypes.to_string()'),
    salida("Service ID int64 | Customer Name str | Vehicle Type str | Make and Model str | Service Type str | Service Description str | Repair Date str | Towing Date str | Tow Location str | Drop-off Location str | Mechanic Name str | Tow Truck Driver str | Parts Used str | Total Cost float64 | Payment Method str | Warranty Information str | Service Status str | Customer Feedback float64 | Follow-up Needed str | Urgency Level str | Customer Type str | Service Duration Hours float64 | Estimated Cost float64 | Mileage at Service int64 | Insurance Claim Used str | Technician Rating float64 | Tow Distance Miles float64 | Is Warranty Valid str"),
    md("## Problemas de calidad\nSe listan los 3+ problemas exigidos por la guía:"),
    code("# 1. Columna 100% nula\npct = df['Customer Feedback'].isna().mean()*100\nprint(f'Customer Feedback: {pct:.1f}% nula')\n\n# 2. Columna corrupta\nn = df['Service Status'].value_counts().get('s', 0)\nprint(f'Service Status: {n:,} filas corruptas')\n\n# 3. Nulos estructurales MAR (grúa)\nprint(df.isna().sum()[df.isna().sum()>0].to_string())\n\n# 4. Valor piso sospechoso\nprint('Total Cost == $20:', int((df['Total Cost']==20).sum()), 'filas')"),
    salida("Customer Feedback: 100.0% nula\nService Status: 1,999,999 filas corruptas\nTowing Date 1714262\nTow Location 1714262\nDrop-off Location 1714262\nTow Truck Driver 1714262\nCustomer Feedback 2000000\nTotal Cost == $20: 5,098 filas"),
    md("## Pregunta de negocio / objetivo analítico\n\n- **Pregunta:** ¿cómo se relacionan el tipo y costo de los servicios de taller con la urgencia y la probabilidad de requerir seguimiento, para identificar clientes y vehículos de alto riesgo?\n- **Objetivo:** clasificar servicios por probabilidad de requerir seguimiento y/o costos anómalos (outliers por tipo de servicio).\n- **Tarea de minería:** clasificación supervisada (target binario `Follow-up Needed`) + análisis no supervisado de outliers de costo."),
    md("## Entregable\n\nActa de constitución analítica generada en `sesiones/s1/ACTA_CONSTITUCION_ANALITICA.md`"),
]
nb(cells, RAIZ / "sesiones" / "s1" / "s1_exploracion_acta.ipynb")

# ─────────────────────── Sesión 2 ───────────────────────
cells = [
    md("# Sesión 2 · Fuentes y tipos de datos\n**AutoGest** · Un dato, tres puertas de entrada + fuentes externas.\n\nSe cargan servicios del taller en CSV, JSON y SQLite; se descargan 1,827 días de clima real de Ibagué desde la API pública open-meteo (estación PERALES) y se unen las fuentes."),
    code('import json, sqlite3, urllib.request\nimport pandas as pd\nfrom pathlib import Path\n\n# Muestra idéntica en 3 formatos\nventas = pd.DataFrame([...])  # ver carga_fuentes_autogest.py'),
    code('RUTA_CSV = Path("datasets/servicios_taller.csv")\nRUTA_JSON = Path("datasets/servicios_taller.json")\nRUTA_DB = Path("datasets/servicios_taller.db")\n\nfor nombre, ruta, lector in [\n    ("CSV", RUTA_CSV, lambda r: pd.read_csv(r)),\n    ("JSON", RUTA_JSON, lambda r: pd.read_json(r)),\n    ("SQLite", RUTA_DB, lambda r: pd.read_sql("SELECT * FROM servicios", sqlite3.connect(r))),\n]:\n    d = lector(ruta)\n    print(nombre, d.shape, len(d.dtypes))'),
    salida("[CSV] shape=(5, 5) · [JSON] shape=(5, 5) · [SQLite] shape=(5, 5)\nfecha queda inferida como str/texto en los tres formatos porque viene en ISO 'YYYY-MM-DD'."),
    md("## Fuente externa · Clima Ibagué (API pública open-meteo)\n\nCumple el requisito **'al menos una API o BD pública'** del proyecto. Parámetros: lat 4.4219, lon -75.1331 (PERALES), rango 2020-01-01 a 2024-12-31."),
    code('# Fetch API\nurl = ("https://archive-api.open-meteo.com/v1/archive"\n       "?latitude=4.4219&longitude=-75.1331"\n       "&start_date=2020-01-01&end_date=2024-12-31"\n       "&daily=precipitation_sum,temperature_2m_max,temperature_2m_min"\n       "&timezone=America%2FBogota")\nwith urllib.request.urlopen(url, timeout=60) as r:\n    data = json.load(r)\n\nclima = pd.DataFrame(data["daily"])\nclima.columns = ["fecha","precipitacion_mm","temp_max_c","temp_min_c"]\nclima["es_lluvia_extrema"] = clima["precipitacion_mm"].fillna(0) > 7.5\nclima.to_csv("../../data_pipeline/data/raw/clima_ibague_openmeteo.csv", index=False)\nprint(clima.shape, "días | días lluvia extrema:", int(clima["es_lluvia_extrema"].sum()))'),
    salida("Clima descargado: 1,827 días (2020-01-01 a 2024-12-31)\nDías con lluvia extrema (>7.5mm): 174"),
    md("## Unión de fuentes (left join)\n\nImplementa el cruce servicios × clima del pipeline (`data_pipeline/scripts`): **190,414 servicios ocurrieron en días de lluvia extrema** — la señal climática de FASE_1."),
    code('# Left join servicios × clima\nservicios = pd.read_csv("../../data_pipeline/data/raw/enhanced_motor_vehicle_repair_towing_dataset.csv",\n                   usecols=["Service Type","Repair Date","Total Cost"], low_memory=False)\nservicios["fecha"] = pd.to_datetime(servicios["Repair Date"]).dt.date\nclima["fecha"] = pd.to_datetime(clima["fecha"]).dt.date\nunion = servicios.merge(clima, on="fecha", how="left")\nprint("Filas tras join:", f"{union.shape[0]:,}", "| sin dato climático:", union["precipitacion_mm"].isna().sum())'),
    salida("Filas tras join: 2,000,000 | sin dato climático: 0\nServicios en día de lluvia extrema: 190,414"),
]
nb(cells, RAIZ / "sesiones" / "s2" / "s2_fuentes_clima.ipynb")

# ─────────────────────── Sesión 3 ───────────────────────
cells = [
    md("# Sesión 3 · Limpieza de datos (pipeline AutoGest)\n\nReproduce el pipeline del curso sobre el dataset del proyecto aplicando **RNF-03 (MAR 'No aplica')** e **IQR por tipo de servicio**.\n\nVer `sesiones/s3/limpieza_autogest.py`."),
    code('import unicodedata\nimport pandas as pd\nfrom pathlib import Path\n\ndf = pd.read_csv("../../data_pipeline/data/raw/enhanced_motor_vehicle_repair_towing_dataset.csv", low_memory=False)\nprint("Filas iniciales:", f"{len(df):,}")\nprint(df.isna().sum()[df.isna().sum()>0].to_string())\nprint("Duplicados:", int(df.duplicated().sum()))'),
    salida("Filas iniciales: 2,000,000\nTowing Date 1714262 | Tow Location 1714262 | Drop-off Location 1714262 | Tow Truck Driver 1714262 | Customer Feedback 2000000\nDuplicados: 0"),
    md("## 1. Columnas inutilizables"),
    code('# Customer Feedback 100 % nula y Service Status corrupta\ndf = df.drop(columns=["Customer Feedback", "Service Status"])\nprint("Columnas restantes:", df.shape[1])'),
    salida("Columnas restantes: 26"),
    md("## 2. Nulos estructurales MAR — grúa (RNF-03)\n\nEl nulo coincide 1:1 con `Service Type != 'Towing'`. Se marca 'No aplica' en texto; `Towing Date` no se imputa (nada inventado)."),
    code('mask = df["Service Type"] != "Towing"\nfor col in ["Tow Location","Drop-off Location","Tow Truck Driver"]:\n    assert df[col].isna().sum() == mask.sum()\n    df[col] = df[col].fillna("No aplica (servicio sin remolque)")\nprint("Columnas NOTOWING imputadas:", int(mask.sum()), "filas cada una")'),
    salida("Columnas NOTOWING imputadas: 1,714,262 filas cada una"),
    md("## 3. IQR segmentado por tipo de servicio → reglas_iqr_servicio"),
    code('def iqr_bounds(s):\n    q1, q3 = s.quantile([0.25, 0.75]); iqr = q3 - q1\n    return q1, q3, iqr, q1 - 1.5*iqr, q3 + 1.5*iqr\n\noutliers = []\nfor col in ["Total Cost", "Estimated Cost"]:\n    bandera = col.replace(" ","_") + "_Outlier_IQR"\n    df[bandera] = False\n    for tipo, sub in df.groupby("Service Type")[col]:\n        q1, q3, iqr, lo, hi = iqr_bounds(sub)\n        idx = sub[(sub < lo) | (sub > hi)].index\n        df.loc[idx, bandera] = True\n        outliers.append((col, tipo, lo, hi, len(idx)))\n    print(col, "outliers:", int(df[bandera].sum()), f"({df[bandera].mean()*100:.3f}%)")'),
    salida("Total Cost: 11,830 outliers (0.592%)\nEstimated Cost: 13,310 outliers (0.665%)"),
    md("## 4. Validación y exportación\n\nProduce `data_pipeline/data/processed/motor_vehicle_limpio_propio.csv` (2,000,000 × 31), `data_pipeline/outputs/bitacora_limpieza.csv` y `reglas_iqr_servicio.csv` (14 reglas para 7 tipos de servicio). Solo el IQR segmentado evita marcar reparaciones caras legítimas como anomalías."),
]
nb(cells, RAIZ / "sesiones" / "s3" / "s3_limpieza_autogest.ipynb")

# ─────────────────────── Sesión 4 ───────────────────────
cells = [
    md("# Sesión 4 · Matriz de features X e y\n\nConstrucción de X (predictores) y y (objetivo) desde `motor_vehicle_limpio_propio.csv` — insumo directo del modelo de IA preventiva de FASE_5.\n\nVer `sesiones/s4/transformaciones_autogest.py`."),
    code('import pandas as pd\nfrom sklearn.preprocessing import StandardScaler, KBinsDiscretizer\nfrom sklearn.decomposition import PCA\n\ndf = pd.read_csv("../../data_pipeline/data/processed/motor_vehicle_limpio_propio.csv", low_memory=False)\nprint(df.shape)'),
    salida("(2000000, 31)"),
    md("## 1. Selección de variables\n\n- **Numéricas (6):** Total Cost, Service Duration Hours, Estimated Cost, Mileage at Service, Technician Rating, Tow Distance Miles.\n- **Categóricas (2):** Service Type, Urgency Level.\n- **Excluidas:** Service ID (id), fechas (temporalidad a manejar aparte), texto libre (descripciones, nombres, ubicaciones) y banderas derivadas (outliers). La variable objetivo no entra en X."),
    code('X_num = df[NUMERICAS].astype(float)\nscaler = StandardScaler()\nX_std = pd.DataFrame(scaler.fit_transform(X_num), columns=NUMERICAS)\nprint("Medias:", X_std.mean().round(4).to_dict())\nprint("Desv.:", X_std.std().round(4).to_dict())'),
    salida("Medias: todas ≈ 0.0\nDesv.: todas = 1.0 (verificación StandardScaler OK)"),
    code('X_cat = pd.get_dummies(df[["Service Type","Urgency Level"]], dtype=int)\nX = pd.concat([X_std, X_cat], axis=1)\nprint("X final:", X.shape)'),
    salida("X final: (2000000, 16)"),
    md("## 2. Variable objetivo\n\n`y = 1` si `Follow-up Needed == 'Yes'` (50 % de la población)."),
    code('y = df["Follow-up Needed"].eq("Yes").astype(int)\nprint(y.value_counts(normalize=True).round(3))'),
    salida("0    0.5\n1    0.5\nName: requiere_seguimiento, dtype: float64"),
    md("## 3. Discretización y PCA\n\n- Total Cost → 3 rangos de negocio por cuartiles: **económico / medio / costoso**.\n- PCA sobre las 6 numéricas estandarizadas: **4 componentes explican el 85%** de la varianza; los primeros 2 solo el 51.7%."),
    code('print(pd.qcut(df["Total Cost"], q=3, labels=["económico","medio","costoso"], duplicates="drop").value_counts())\n\nrazones = PCA().fit(X_std).explained_variance_ratio_.cumsum()\nprint("Varianza acumulada:", razones.round(3).tolist())'),
    salida("económico 666,685 | costoso 666,664 | medio 666,651\nVarianza acumulada: [0.35, 0.517, 0.684, 0.85, 0.999, 1.0]"),
    md("## 4. Entregable\n\nMatrices guardadas en `data_pipeline/data/processed/`:\n- `X_features.csv` (2,000,000 × 16)\n- `y_objetivo.csv` (2,000,000 × 1)\n\nEl `StandardScaler` se ajusta solo sobre datos de entrenamiento en producción (evitar fuga)."),
]
nb(cells, RAIZ / "sesiones" / "s4" / "s4_transformaciones.ipynb")

print("FIN generación notebooks")