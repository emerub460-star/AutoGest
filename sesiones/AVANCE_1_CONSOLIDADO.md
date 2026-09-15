# Avance 1 · Consolidación — Sesiones 1–4
## Proyecto integrador · Minería de Datos · 2026-2 · AutoGest

> Fases CRISP-DM cubiertas: **Negocio · Datos · Preparación** (sesiones 1 a 4).
> Artefactos generados y verificados durante la ejecución del plan.

---

## 1. Checklist de entregables (sesiones 1–4)

| # | Entregable (Checklist del curso) | Ruta | Estado |
|---|---------------------------------|------|--------|
| 1 | Cuaderno Colab ejecutado + acta de constitución analítica | `sesiones/s1/s1_exploracion_acta.ipynb` · `sesiones/s1/ACTA_CONSTITUCION_ANALITICA.md` | ✅ Verificado |
| 2 | Las 2 fuentes definitivas documentadas (una API/BD pública) | `sesiones/s2/FUENTES_DATOS.md` · `sesiones/s2/s2_fuentes_clima.ipynb` | ✅ Verificado |
| 3 | Dataset limpio validado contra el canónico + bitácora de limpieza | `sesiones/s3/s3_limpieza_autogest.ipynb` · `data_pipeline/data/processed/motor_vehicle_limpio_propio.csv` · `data_pipeline/outputs/bitacora_limpieza.csv` | ✅ Verificado |
| 4 | Matriz de features `X` e `y` guardadas por separado | `sesiones/s4/s4_transformaciones.ipynb` · `data_pipeline/data/processed/X_features.csv` · `data_pipeline/data/processed/y_objetivo.csv` | ✅ Verificado |
| 5 | *(próx.)* EDA con visualizaciones | Sesión 5 | ⏳ Pendiente |
| 6 | *(próx.)* Consolidación del Avance 1 | Sesión 6 | ⏳ Pendiente |

---

## 2. Resultados verificados (números reales)

| Métrica | Valor |
|---------|-------|
| Dimensiones del dataset crudo | 2,000,000 × 28 |
| Nulos totales en crudo | 8,857,048 |
| Columnas inutilizables eliminadas | 2 (`Customer Feedback` 100% nula, `Service Status` corrupta) |
| Nulos MAR de grúa tratados con "No aplica" (RNF-03) | 1,714,262 × 3 columnas (Towing Date documentada, sin imputar) |
| Duplicados exactos | 0 |
| Dimensiones del dataset limpio | 2,000,000 × 31 (sin filas eliminadas, + banderas de auditoría) |
| Outliers de costo Total Cost (IQR segmentado) | 11,830 (0.592%) |
| Outliers de costo Estimated Cost (IQR segmentado) | 13,310 (0.665%) |
| Reglas IQR por tipo de servicio | 14 reglas / 7 tipos de servicio (`reglas_iqr_servicio.csv`) |
| Días de clima descargados (API) | 1,827 (2020-01-01 → 2024-12-31) |
| Días de lluvia extrema (>7.5 mm) | 174 |
| Servicios en días de lluvia extrema (left join) | 190,414 |
| Matriz X final | 2,000,000 × 16 (6 numéricas escaladas + 10 one-hot) |
| Variable objetivo y | `Follow-up Needed = Yes` → 50% |
| PCA (varianza acumulada) | 4 componentes ≈ 85% |

---

## 3. Decisión CRISP-DM documentada

- **Pregunta de negocio:** ¿cómo se relacionan el tipo y costo de los servicios de taller con la urgencia y la probabilidad de requerir seguimiento, para identificar clientes y vehículos de alto riesgo?
- **Objetivo analítico:** clasificar servicios por probabilidad de requerir seguimiento (target `Follow-up Needed`), con detección complementaria de costos anómalos por tipo de servicio (no supervisado).
- **Tarea de minería:** clasificación supervisada (binaria) + análisis de outliers.

---

## 4. Estructura del repositorio tras la ejecución

```text
AutoGest/
├── data_pipeline/
│   ├── data/
│   │   ├── raw/          # enhanced_motor_vehicle_repair_towing_dataset.csv, clima_ibague_openmeteo.csv
│   │   └── processed/    # motor_vehicle_limpio_propio.csv, X_features.csv, y_objetivo.csv
│   └── outputs/          # reglas_iqr_servicio.csv, bitacora_limpieza.csv
├── sesiones/
│   ├── s1/               # s1_exploracion_acta.ipynb, exploracion_autogest.py, ACTA_CONSTITUCION_ANALITICA.md
│   ├── s2/               # s2_fuentes_clima.ipynb, carga_fuentes_autogest.py, FUENTES_DATOS.md
│   ├── s3/               # s3_limpieza_autogest.ipynb, limpieza_autogest.py
│   ├── s4/               # s4_transformaciones.ipynb, transformaciones_autogest.py
│   └── generar_notebooks.py
├── FASE_1..FASE_7.md      # especificación por fases del proyecto
└── PLAN_DETALLADO_SESIONES_1_A_4.md
```

---

## 5. Verificación estadística (resumen)

- StandardScaler: medias ≈ 0, desviaciones = 1 (validación de escalado correcta).
- Discretización en cuartiles: 3 rangos balanceados (~666k cada uno).
- Validaciones de rango del dataset limpio: Total Cost ≥ 0, Estimated Cost ≥ 0, Service Duration > 0, Mileage ≥ 0 → **OK**.