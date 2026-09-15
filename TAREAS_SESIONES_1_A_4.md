# Tareas por sesión · Minería de Datos · Sesiones 1 a 4

> Materia: Minería de Datos · UNIMINUTO Ibagué · 2026-2
> Cubre: ejercicios en clase, instrumentos de evaluación y trabajo independiente de las sesiones 1 a 4.

---

## Sesión 1 · Introducción a la Minería de Datos

### Ejercicio en clase — "Acta de constitución analítica" (equipos de 3)

1. Abrir el dataset en Colab (`pd.read_csv`) y registrar: dimensiones, tipos de datos y al menos 3 problemas de calidad detectados.
2. Calcular la tasa global de fuga y la tasa por `tipo_plan` y por `num_quejas >= 3`. Identificar el segmento más preocupante.
3. Redactar la pregunta de negocio y el objetivo analítico del proyecto en lenguaje no técnico (máx. 3 líneas cada uno).
4. Clasificar el proyecto según las tareas de minería vistas (¿clasificación? ¿clustering?) y justificar en 2 líneas.
5. Subir el cuaderno `.ipynb` + acta al espacio del curso. Portavoz socializa en 60 segundos.

### Trabajo independiente (para sesión 2) — ~6 horas

1. **Lectura (2 h):** Han, Kamber & Pei, cap. 1. Anotar 3 ideas y 2 dudas.
2. **Práctica (2 h):** completar tutorial "Intro to Pandas" de Kaggle Learn y reproducir la demo desde cero sin mirar el cuaderno.
3. **Proyecto (2 h):** cada equipo lista 2 datasets candidatos alternativos (uno de datos.gov.co) con enlace, número de filas y posible variable objetivo.

### Instrumento de evaluación

- Taller de ejercicios: cuaderno Colab ejecutado (50%), acta del proyecto (30%), socialización (20%).

---

## Sesión 2 · Fuentes y Tipos de Datos

### Ejercicio en clase — "Un dato, tres puertas de entrada" (equipos de 3)

1. Ubicar los tres archivos en `sesion2/datasets/` (`ventas_tienda.csv`, `.json`, `.db`) y abrirlos "con los ojos" (editor de texto / DB Browser).
2. Cargar los tres con `read_csv`, `read_json` y `read_sql`; imprimir `shape` y `dtypes` de cada uno.
3. Construir tabla comparativa de tipos por columna. Explicar por qué `fecha` quedó igual en los tres formatos y qué implica.
4. Calcular ingresos por categoría dos veces: con SQL (`GROUP BY`) y con pandas (`groupby`). Verificar que coinciden.
5. Redactar 3 líneas: ¿qué fuente elegirían si la tienda crece a 50 sedes?, ¿por qué? Subir el cuaderno.

### Quiz simulacro (prueba escrita corta)

1. Clasificar tabla SQL (estructurado), JSON de una API (semiestructurado) y audio de call center (no estructurado); justificar.
2. `edad` con 123 nulos → dtype en pandas (`float64`, por los NaN).
3. Datos actualizados cada hora: CSV por correo vs API REST (elegir API: frescura + control de acceso).
4. CSV del DANE con "BogotÃ¡" y una sola columna: `encoding="latin-1"` y `sep=";"`.
5. Qué hace `pd.read_sql` y qué necesita para funcionar.

### Trabajo independiente (para sesión 3) — ~6 horas

1. **Lectura (2 h):** guía de tipos y formatos + Han, Kamber & Pei, sección 2.1. Anotar 2 dudas para el foro.
2. **Práctica (2 h):** descargar 2 datasets de datos.gov.co, cargarlos en Colab y documentar parámetros necesarios (`sep`, `encoding`, ...) y dtypes resultantes.
3. **Proyecto (2 h):** el equipo define sus 2 fuentes definitivas (al menos una API o BD pública) y documenta formato, tamaño y posible variable objetivo.

### Instrumento de evaluación

- Prueba escrita corta: comprensión conceptual (40%), lectura crítica de JSON/API (25%), aplicación práctica (25%), precisión terminológica (10%).

---

## Sesión 3 · Limpieza de Datos

### Ejercicio en clase — "Dejar TelecomUNO impecable" (equipos de 3)

Objetivo: producir `telecom_limpio_propio.csv` comparable con el canónico (2.400 filas, 0 nulos).

1. Diagnosticar con `isna().sum()`, `duplicated().sum()` y `describe()`; listar los 5 problemas principales con cifras.
2. Resolver duplicados y categorías (strip, tildes, mapeo). Verificar: 2.400 filas, 5 ciudades, 3 planes.
3. Imputar nulos columna por columna, escribiendo un comentario con el método elegido y su justificación (mediana/moda/bandera).
4. Aplicar IQR a `gb_datos` y corregir edades/facturación/minutos imposibles. Reportar cuántos valores tocó.
5. Validar contra `telecom_clientes_limpio.csv` (filas y nulos) y exportar el CSV. Subir el notebook ejecutado.

### Trabajo independiente (para sesión 4) — ~6 horas

1. **Lectura (2 h):** Han, Kamber & Pei, sección 2.3 + artículo breve de MCAR/MAR/MNAR.
2. **Práctica (2 h):** completar el ejercicio hasta la validación verde y redactar informe de máx. 1 página: qué imputó, con qué método y por qué.
3. **Proyecto (2 h):** el equipo aplica el pipeline a su dataset alternativo y documenta en qué difieren los problemas de calidad.

### Instrumento de evaluación

- Rúbrica de código: funcionalidad (40%), justificación técnica (30%), documentación (20%), reproducibilidad (10%).

---

## Sesión 4 · Transformación y Reducción de Datos

### Ejercicio en clase — "La matriz de features profesional" (equipos de 3)

Objetivo: construir `X` (predictores) e `y` (objetivo) desde `telecom_clientes_limpio.csv`.

1. Seleccionar las 6 numéricas y 2 categóricas; justificar por qué se excluyen `id_cliente`, `fecha_contrato` y `ciudad`.
2. Escalar las numéricas con `StandardScaler` y verificar en pantalla: medias ≈ 0, desviaciones ≈ 1.
3. Aplicar `get_dummies(dtype=int)` a `tipo_plan` y `pago_automatico` y concatenar con las numéricas escaladas.
4. Discretizar `edad` en 3 rangos con etiquetas de negocio (joven/adulto/mayor) usando cuartiles; discutir qué versión prefieren y por qué.
5. Reportar shape final de `X`, guardar `X` e `y`, y subir el notebook ejecutado.

### Cuestionario de salida (6 preguntas)

1. Escalador con outliers reales a conservar → `RobustScaler`.
2. Columnas que produce one-hot de `tipo_plan` (3 categorías) → 3.
3. Riesgo de `LabelEncoder` sobre variable nominal → inventa orden falso.
4. Primera componente de PCA → dirección de máxima varianza.
5. PCA 10 → 2 componentes con 85% acumulado → se puede reducir perdiendo ~15% de información.
6. Orden correcto del pipeline → limpiar → codificar → escalar.

### Trabajo independiente (para sesión 5) — ~6 horas

1. **Lectura (2 h):** Han, Kamber & Pei, sección 2.4 + documentación oficial de scikit-learn (`StandardScaler` y `PCA`).
2. **Práctica (2 h):** replicar `transformaciones.py` variando experimentos: `n_bins=5` en la discretización y `RobustScaler` en lugar de `StandardScaler`. Anotar cómo cambian los resultados.
3. **Proyecto (2 h):** construir la matriz de features del dataset alternativo documentando decisiones de escalado/codificación en el notebook.

### Instrumento de evaluación

- Cuestionario de salida (6 preguntas, 01:46 – 01:54).

---

## Proyecto integrador · Avance 1 (sesiones 1 a 6)

| Corte | Avance | Fases CRISP-DM | Sesiones |
|-------|--------|----------------|----------|
| Avance 1 (30%) | Dataset preprocesado y documentado | Negocio · Datos · Preparación | 1 – 6 |

- Equipos de 3 estudiantes. También pueden proponer dataset propio de datos abiertos colombianos con aprobación del docente.
- Criterios de dataset alternativo: mínimo 500 filas, variable objetivo clara (o pregunta de agrupación), datos comprensibles.

### Checklist de entrega del Avance 1 (acumulado sesiones 1–4)

- [ ] Sesión 1: cuaderno Colab ejecutado + acta de constitución analítica (pregunta de negocio y objetivo analítico).
- [ ] Sesión 2: las 2 fuentes definitivas del equipo documentadas (una API/BD pública).
- [ ] Sesión 3: dataset limpio (`telecom_limpio_propio.csv`) validado contra el canónico + bitácora de limpieza.
- [ ] Sesión 4: matriz de features `X` (2400×11) e `y` guardadas por separado.
- [ ] Sesión 5 (próx.): EDA con visualizaciones.
- [ ] Sesión 6 (próx.): consolidación del avance 1.

---

## Recordatorios transversales

- Originales intocables: trabaje siempre sobre copias.
- En producción: `fit()` del escalador solo con datos de entrenamiento (evitar fuga de datos).
- Nunca incluir la variable objetivo (`fuga`) dentro de `X`.
- Cada decisión de limpieza/transformación debe quedar documentada (bitácora).
- Cero credenciales o llaves en el repositorio.