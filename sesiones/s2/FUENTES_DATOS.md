# Fuentes de datos definitivas — AutoGest
## Sesión 2 · Minería de Datos · 2026-2

> Requisito del proyecto integrador (Avance 1): *definir 2 fuentes definitivas, al menos una API o BD pública, y documentar formato, tamaño y posible variable objetivo.*

---

## Fuente A · Dataset principal — reparaciones y remolque de taller

| Atributo | Valor |
|----------|-------|
| **Nombre** | `enhanced_motor_vehicle_repair_towing_dataset` |
| **Origen** | Kaggle (descarga local en `data_pipeline/data/raw/`) |
| **Formato** | CSV (delimitador coma, UTF-8) |
| **Tamaño** | 2,000,000 filas × 28 columnas (~483 MB) |
| **Temporalidad** | 2020-01-01 a 2024-12-31 |
| **Variable objetivo (candidata)** | `Follow-up Needed` (Yes/No) → clasificación de servicios que requieren seguimiento |
| **Complemento no supervisado** | detección de outliers de costo por tipo de servicio (Regla IQR → `reglas_iqr_servicio`) |
| **Columnas clave** | `Service Type`, `Total Cost`, `Service Duration Hours`, `Urgency Level`, `Payment Method`, `Repair Date`, `Towing Date` |
| **Problemas de calidad detectados** | `Customer Feedback` 100% nula; `Service Status` corrupta (99.9999% `'s'`); nulos MAR en columnas de grúa (1,714,262); valor piso `$20.00` (5,098) |

**Rol en el proyecto:** alimenta las tablas `servicios_reparacion` y `servicios_grua` de FASE_3 (esquema PostgreSQL) y el pipeline de limpieza/IQR de FASE_5.

---

## Fuente B · API pública climática — estación PERALES (Ibagué)

| Atributo | Valor |
|----------|-------|
| **Nombre** | Open-Meteo Archive API — clima histórico |
| **Origen** | API pública (sin clave) `https://archive-api.open-meteo.com` |
| **Coordenadas** | Lat 4.4219, Lon -75.1331 (Aeropuerto PERALES, estación NOAA `COM00080214`) |
| **Formato** | JSON vía HTTP GET → CSV (`clima_ibague_openmeteo.csv`) |
| **Tamaño** | 1,827 días (2020-01-01 a 2024-12-31) |
| **Variables** | `precipitacion_mm`, `temp_max_c`, `temp_min_c`, `es_lluvia_extrema` (>7.5 mm) |
| **Variable objetivo** | `es_lluvia_extrema` (definida en RF-04/FASE_1) |
| **Frescura** | Actualizable a demanda; API REST con control de acceso (sin credencial | para lectura básica) |

**Rol en el proyecto:** alimenta la tabla `clima_noaa` de FASE_3 y el cruce servicios × clima (señal de demanda por clima extremo usada por la IA preventiva de FASE_5).

---

## Criterio de selección (respuesta a "¿qué fuente elegirían si el taller crece a 50 sedes?")

> Elegiríamos **API REST centralizada + PostgreSQL** en lugar de intercambiar CSV por correo. Motivos: frescura de datos (actualización horaria/instantánea), control de acceso por token, auditoría de cambios y la capacidad de cruzar 2M de servicios con clima por fecha sin réplicas manuales.

---

## Datasets externos pendientes (Kaggle)

El pipeline está preparado para incorporar datasets externos de **accidentes y tráfico** descargados de Kaggle, cuando estén disponibles (requiere token de API Kaggle en `~/.kaggle/kaggle.json`). El enriquecimiento se haría por coordenadas y fecha vía `left join` en `data_pipeline/scripts/`.