# Plan detallado · Sesiones 1 a 4 · Minería de Datos → Proyecto AutoGest

> Materia: Minería de Datos · UNIMINUTO Ibagué · 2026-2
> Documento generado a partir de `TAREAS_SESIONES_1_A_4.md`, mapeando cada tarea al contexto del proyecto **AutoGest** (fases 1–7 y stack de `estructura.md`).

---

## 1. Mapa sesión ↔ fase AutoGest

| Sesión | Tema del curso | Entrega del curso | Fase AutoGest que alimenta | Componente del repo |
|--------|----------------|-------------------|---------------------------|---------------------|
| 1 | Introducción a la Minería de Datos | Acta de constitución analítica, pregunta/objetivo | FASE_1 · Planificación y Requisitos | `FASE_1_Planificacion_y_Requisitos.md` (RF-01…05, RNF-01…03) |
| 2 | Fuentes y Tipos de Datos | 2 fuentes definitivas del equipo documentadas | FASE_3 · Datos y Backend Base | `clima_noaa`, `servicios_reparacion`, `data_pipeline/data/raw/` |
| 3 | Limpieza de Datos | Dataset limpio + bitácora | FASE_3 · Datos + `reglas_iqr_servicio` | `data_pipeline/scripts` (limpieza, left join, IQR) |
| 4 | Transformación y Reducción | Matriz de features `X` e `y` | FASE_5 · IA y Análisis Climático | Matriz de features para el modelo preventivo |
| — | Avance 1 (consolidación) | Dataset preprocesado y documentado | Todas (negocio · datos · preparación) | Ver §6 |

**Regla de oro del proyecto:** los ejercicios en clase se ejecutan sobre `telecom_*` (para aprender el método) y **el mismo pipeline se replica sobre el dataset del proyecto** (2.000.000+ registros de reparación/remolque + clima NOAA `COM00080214`).

---

## 2. Sesión 1 · Introducción a la Minería de Datos

**Objetivo:** formalizar la pregunta de negocio y el objetivo analítico del proyecto y conectar el enfoque de `FASE_1` con un dataset real.

### 2.1 Ejercicio en clase — "Acta de constitución analítica" (equipos de 3)

- [ ] **T1.1 Abrir el dataset en Colab**
  - [ ] Crear cuaderno Colab y montar el dataset base del curso (`telecom_*`).
  - [ ] `pd.read_csv(...)`, imprimir `shape` (dimensiones) y `dtypes`.
  - [ ] Registrar ≥ 3 problemas de calidad observados (nulos, duplicados, tipos errados, categorías inconsistentes).
- [ ] **T1.2 Tasas de fuga**
  - [ ] Tasa global de fuga: `df["fuga"].mean()`.
  - [ ] Tasa por `tipo_plan` (`groupby`).
  - [ ] Tasa para `num_quejas >= 3`.
  - [ ] Conclusión: identificar el segmento más preocupante y citar cifras.
- [ ] **T1.3 Pregunta de negocio y objetivo analítico (máx. 3 líneas c/u)**
  - Contexto AutoGest: la pregunta debe mantenerse consistente con `FASE_1` — p. ej. *"¿Cómo se relaciona el clima extremo (>7.5 mm) con la demanda de servicios/remolque para planear recursos?"*.
- [ ] **T1.4 Clasificar la tarea de minería** (clasificación vs. clustering) + justificación en 2 líneas. Para AutoGest aplicamos clasificación supervisada (variable objetivo binaria: fuga de servicio / demanda alta) y clustering para segmentar tipos de falla.
- [ ] **T1.5 Subir** `.ipynb` + acta al espacio del curso; portavoz socializa en 60 segundos.

### 2.2 Trabajo independiente (→ sesión 2) · ~6 h

- [ ] **T1.6 Lectura (2 h):** Han, Kamber & Pei, cap. 1 → anotar 3 ideas y 2 dudas.
- [ ] **T1.7 Práctica (2 h):** tutorial "Intro to Pandas" (Kaggle Learn) + reproducir la demo desde cero sin mirar el cuaderno.
- [ ] **T1.8 Proyecto (2 h):** listar **2 datasets candidatos** para AutoGest (uno de `datos.gov.co`): enlace, nº filas y posible variable objetivo. Insumo directo para las fuentes definitivas de la sesión 2.

### 2.3 Instrumento de evaluación

- Cuaderno Colab ejecutado (50%) · acta (30%) · socialización (20%).

---

## 3. Sesión 2 · Fuentes y Tipos de Datos

**Objetivo:** dominar la ingesta de datos estructurados/semiestructurados y definir las **2 fuentes definitivas** de AutoGest.

### 3.1 Ejercicio en clase — "Un dato, tres puertas de entrada" (equipos de 3)

- [ ] **T2.1** Ubicar los 3 archivos en `sesion2/datasets/` (`ventas_tienda.csv`, `.json`, `.db`) y abrirlos en editor de texto / DB Browser.
- [ ] **T2.2** Cargar con `read_csv`, `read_json`, `read_sql`; imprimir `shape` y `dtypes` de cada uno.
- [ ] **T2.3** Tabla comparativa de tipos por columna; explicar por qué `fecha` queda igual en los 3 formatos y qué implica.
- [ ] **T2.4** Ingresos por categoría con SQL (`GROUP BY`) y con pandas (`groupby`); verificar igualdad de resultados.
- [ ] **T2.5** Justificar en 3 líneas qué fuente elegirían al crecer a 50 sedes (p. ej. base centralizada + API) y subir el cuaderno.

### 3.2 Quiz simulacro (prueba escrita corta)

- [ ] **T2.6** Responder y repasar: clasificación SQL/JSON/audio, `edad` con 123 nulos → `float64`, API REST vs CSV por correo, CSV DANE con `encoding="latin-1"` y `sep=";"`, y funcionamiento de `pd.read_sql`.

### 3.3 Trabajo independiente (→ sesión 3) · ~6 h

- [ ] **T2.7 Lectura (2 h):** guía de tipos/formatos + Han, Kamber & Pei §2.1 → 2 dudas para el foro.
- [ ] **T2.8 Práctica (2 h):** descargar 2 datasets de `datos.gov.co`, cargarlos en Colab y documentar parámetros requeridos (`sep`, `encoding`) y dtypes resultantes.
- [ ] **T2.9 Proyecto (2 h):** definir las **2 fuentes definitivas de AutoGest** (al menos una API o BD pública) y documentar formato, tamaño y variable objetivo:
  - [ ] Fuente A: dataset 2M+ registros de reparación/remolque (variable objetivo: demanda por día / fuga de servicio).
  - [ ] Fuente B: **estación NOAA `COM00080214` (PERALES)** — variable: `precipitacion_mm` (→ `es_lluvia_extrema > 7.5 mm`). Mitiga la tabla `clima_noaa` de `FASE_3`.
  - [ ] Guardar la documentación como insumo de la bitácora del Avance 1.

### 3.4 Instrumento de evaluación

- Prueba escrita: comprensión conceptual (40%) · lectura crítica JSON/API (25%) · aplicación práctica (25%) · precisión terminológica (10%).

---

## 4. Sesión 3 · Limpieza de Datos

**Objetivo:** producir `telecom_limpio_propio.csv` (2.400 filas, 0 nulos) y **replicar el pipeline sobre el dataset de AutoGest**, cumpliendo `RNF-03` (MAR "No aplica" en grúas) y preparando `reglas_iqr_servicio`.

### 4.1 Ejercicio en clase — "Dejar TelecomUNO impecable" (equipos de 3)

- [ ] **T3.1 Diagnóstico** con `isna().sum()`, `duplicated().sum()`, `describe()` → listar los **5 problemas principales con cifras**.
- [ ] **T3.2 Duplicados y categorías** (strip, tildes, mapeo) → verificar: 2.400 filas, 5 ciudades, 3 planes.
- [ ] **T3.3 Imputación** de nulos columna por columna, comentando método y justificación (mediana/moda/bandera).
- [ ] **T3.4 IQR** sobre `gb_datos` → corregir edades, facturación y minutos imposibles; reportar cuántos valores se ajustaron.
- [ ] **T3.5 Validación y exportación:** comparar contra `telecom_clientes_limpio.csv` (filas y nulos) y exportar `telecom_limpio_propio.csv`. Subir el notebook ejecutado.

### 4.2 Trabajo independiente (→ sesión 4) · ~6 h

- [ ] **T3.6 Lectura (2 h):** Han, Kamber & Pei §2.3 + artículo MCAR/MAR/MNAR.
- [ ] **T3.7 Práctica (2 h):** completar el ejercicio hasta la validación en verde + informe ≤ 1 página (qué imputó, método, por qué).
- [ ] **T3.8 Proyecto (2 h):** aplicar el **pipeline de limpieza al dataset AutoGest** y documentar en qué difieren los problemas:
  - [ ] Tratamiento MAR de grúa: bandera "No aplica" (nunca inventar datos, `RNF-03`) → tabla `servicios_grua`.
  - [ ] IQR de costos por **categoría de servicio** → poblar `reglas_iqr_servicio` (Q1, Q3, IQR, límites) y bandera `es_outlier_costo`.
  - [ ] Cruzar servicios vs. clima con *left join* por fecha → `data_pipeline/scripts`.

### 4.3 Instrumento de evaluación

- Rúbrica de código: funcionalidad (40%) · justificación técnica (30%) · documentación (20%) · reproducibilidad (10%).

---

## 5. Sesión 4 · Transformación y Reducción de Datos

**Objetivo:** construir la matriz de features `X` y el vector objetivo `y` (base del modelo preventivo de `FASE_5`).

### 5.1 Ejercicio en clase — "La matriz de features profesional" (equipos de 3)

- [ ] **T4.1 Selección:** elegir las 6 columnas numéricas y 2 categóricas; justificar la exclusión de `id_cliente`, `fecha_contrato` y `ciudad`.
- [ ] **T4.2 Escalado:** `StandardScaler` sobre las numéricas; verificar medias ≈ 0 y desviaciones ≈ 1. **Recordatorio:** en producción, `fit()` solo con datos de entrenamiento (evitar fuga).
- [ ] **T4.3 Codificación:** `get_dummies(dtype=int)` sobre `tipo_plan` y `pago_automatico`; concatenar con las numéricas escaladas.
- [ ] **T4.4 Discretización:** `edad` en 3 rangos (cuartiles) con etiquetas de negocio (joven/adulto/mayor); discutir versión preferida.
- [ ] **T4.5 Reportar** shape final de `X`; guardar `X` e `y` **por separado** (nunca incluir `fuga` dentro de `X`); subir el notebook.

### 5.2 Cuestionario de salida (6 preguntas)

- [ ] **T4.6** Repasar: `RobustScaler`, nº de columnas del one-hot (3), riesgo de `LabelEncoder` en nominal, primera componente de PCA, PCA 10→2 con 85% acumulado, pipeline limpiar→codificar→escalar.

### 5.3 Trabajo independiente (→ sesión 5) · ~6 h

- [ ] **T4.7 Lectura (2 h):** Han, Kamber & Pei §2.4 + docs oficiales de `StandardScaler` y `PCA`.
- [ ] **T4.8 Práctica (2 h):** replicar `transformaciones.py` con experimentos: `n_bins=5` en discretización y `RobustScaler` en lugar de `StandardScaler`; anotar cómo cambian los resultados.
- [ ] **T4.9 Proyecto (2 h):** construir la **matriz de features de AutoGest** documentando decisiones de escalado/codificación:
  - [ ] Features: vehículo (año, kilometraje), servicio (tipo, duración, costo, urgencia), clima (precipitación, `es_lluvia_extrema`).
  - [ ] Target: demanda alta de servicio / fuga (definida en T1.3/T2.9).
  - [ ] Guardar `X_autogest` e `y_autogest` y registrar decisiones en el notebook (bitácora).

### 5.4 Instrumento de evaluación

- Cuestionario de salida (6 preguntas, 01:46 – 01:54).

---

## 6. Ruta al Avance 1 (sesiones 1–6) · 30%

Criterios del dataset: ≥ 500 filas, variable objetivo clara o pregunta de agrupación, datos comprensibles.
AutoGest cumple con el dataset 2M+ (fuente A) y NOAA (fuente B).

| # | Entregable acumulado | Tarea fuente | Estado |
|---|----------------------|--------------|--------|
| 1 | Cuaderno Colab ejecutado + acta de constitución (pregunta de negocio y objetivo analítico) | T1.1–T1.5 | [ ] |
| 2 | Las 2 fuentes definitivas documentadas (una API/BD pública) | T2.9 | [ ] |
| 3 | Dataset limpio `telecom_limpio_propio.csv` validado vs. canónico + bitácora de limpieza | T3.1–T3.5 + T3.8 | [ ] |
| 4 | Matriz de features `X` (2400×11) e `y` guardadas por separado | T4.1–T4.5 + T4.9 | [ ] |
| 5 | *(próx.)* EDA con visualizaciones | Sesión 5 | [ ] |
| 6 | *(próx.)* Consolidación del Avance 1 | Sesión 6 | [ ] |

---

## 7. Orden de ejecución y dependencias

1. **Semana 1 (Sesión 1):** T1.1→T1.5 en clase; T1.6–T1.8 fuera. Hito: acta + pregunta/objetivo (alimenta `FASE_1`).
2. **Semana 2 (Sesión 2):** T2.1–T2.6 clase; T2.7–T2.9 fuera. Hito: fuentes definitivas AutoGest (alimenta `FASE_3` / `data_pipeline/data/raw`).
3. **Semana 3 (Sesión 3):** T3.1–T3.5 clase; T3.6–T3.8 fuera. Hito: pipeline de limpieza + IQR por categoría (alimenta `reglas_iqr_servicio`).
4. **Semana 4 (Sesión 4):** T4.1–T4.6 clase; T4.7–T4.9 fuera. Hito: `X` e `y` finales (alimenta el modelo de `FASE_5`).
5. **Sesiones 5–6:** EDA (sesión 5) → consolidación y entrega del Avance 1 (sesión 6).

> **Dependencias clave:** no pasar a T4.x sin cerrar T3.8 (datos limpios) · la variable `y` se fija en T1.3 y se confirma en T2.9 antes de construir `X` · las reglas IQR de T3.8 condicionan la bandera `es_outlier_costo` usada en `FASE_4`.

---

## 8. Recordatorios transversales (aplicar en todo el plan)

- Originales intocables: trabajar siempre sobre copias (`data/raw` se excluye en `.gitignore`).
- `fit()` del escalador solo con datos de entrenamiento.
- Nunca incluir la variable objetivo dentro de `X`.
- Cada decisión de limpieza/transformación queda documentada (bitácora).
- Cero credenciales o llaves en el repositorio.