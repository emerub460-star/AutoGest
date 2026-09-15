# Acta de Constitución Analítica — AutoGest
## Sesión 1 · Minería de Datos · 2026-2

**Dataset:** `enhanced_motor_vehicle_repair_towing_dataset.csv`
**Dimensiones:** 2,000,000 filas × 28 columnas

---

## 1. Dimensiones y tipos de datos

- Columnas: Service ID, Customer Name, Vehicle Type, Make and Model, Service Type, Service Description, Repair Date, Towing Date, Tow Location, Drop-off Location, Mechanic Name, Tow Truck Driver, Parts Used, Total Cost, Payment Method, Warranty Information, Service Status, Customer Feedback, Follow-up Needed, Urgency Level, Customer Type, Service Duration Hours, Estimated Cost, Mileage at Service, Insurance Claim Used, Technician Rating, Tow Distance Miles, Is Warranty Valid
- Numéricas (8) y categóricas/texto (20)
- Fechas: `Repair Date` y `Towing Date` (texto, no parseadas aún)

## 2. Problemas de calidad detectados

| # | Problema | Evidencia |
|---|----------|-----------|
| 1 | `Customer Feedback` 100 % nula | 100.0% sin ningún valor real — columna vacía |
| 2 | `Service Status` corrupta | 99.9999% contiene solo `'s'` (truncamiento ETL), solo 1 fila válida |
| 3 | Nulos estructurales en columnas de grúa (MAR) | `Towing Date`, `Tow Location`, `Drop-off Location`, `Tow Truck Driver` 85.71 % nulos, nulo = Service Type != Towing |
| 4 | Valor piso `$20.00` repetido en Total Cost | 5,098 filas (0.25%) — posible tarifa mínima o error |
| 5 | Incoherencias marca/modelo | Ej.: "Harley-Davidson Ram 1500", "BMW Corolla" |
| 6 | Filas duplicadas exactas | 0 duplicados |
| 7 | Fechas de grúa inconsistentes | Grúa puede ser posterior a reparación |

## 3. Pregunta de negocio

> ¿Cómo se relacionan el tipo y costo de los servicios de taller con la urgencia y la probabilidad de requerir seguimiento, para identificar clientes y vehículos de alto riesgo?

## 4. Objetivo analítico

> Clasificar servicios en función de la probabilidad de requerir seguimiento y/o presentar costos anómalos (outliers por tipo de servicio), usando variables numéricas (costo, duración, kilometraje, rating) y categóricas (tipo servicio, tipo vehículo, forma de pago).

## 5. Clasificación de la tarea de minería

> El proyecto es de CLASIFICACIÓN SUPERVISADA: la variable objetivo es 'Follow-up Needed' (Yes/No), binaria y supervisada por el historial de seguimiento real. Complementariamente, la detección de outliers de costo por tipo de servicio es análisis NO SUPERVISADO (clustering/estadística).

## 6. Segmento más preocupante

- Servicios con Follow-up Needed = Yes: 50.0%
- Servicios de Urgency = Emergency: 33.3%
- Servicio con mayor costo promedio: Transmission Repair
