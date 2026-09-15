# FASE_1_Planificacion_y_Requisitos.md

# AutoGest — Fase 1: Planificación y Requisitos

## 1. Visión General del Sistema
AutoGest es una plataforma híbrida Web y Móvil orientada a la gestión de servicios de taller automotriz, mantenimientos preventivos y auxilio mecánico mediante grúas. El sistema integra el análisis de un dataset de más de 2,000,000 de registros reales de reparación y remolque con datos meteorológicos de la estación NOAA `COM00080214` (PERALES) para relacionar eventos de clima extremo (>7.5 mm de lluvia) con la demanda de servicios.

## 2. Roles del Sistema
* **Cliente / Conductor:** Administra sus vehículos, consulta historiales, programa citas, solicita grúas de emergencia y accede a su ficha técnica QR.
* **Mecánico:** Registra diagnósticos, reparaciones, repuestos instalados y consulta resúmenes ejecutivos del historial generados por IA.
* **Personal de Recepción:** Gestiona el flujo de ingreso de vehículos, agenda de citas, asignación de turnos y despacho de grúas.
* **Administrador:** Administra usuarios, sedes, reglas de negocio (límites IQR por categoría de servicio) y analiza las métricas operativas vs. clima[cite: 1, 3, 5].

## 3. Módulos Funcionales del MVP
* **Autenticación y RBAC:** Registro, inicio de sesión seguro y control de acceso basado en roles[cite: 3, 5].
* **Gestión de Vehículos:** Registro de ficha técnica (marca, modelo, año, VIN, placa, kilometraje) y seguimiento de desgaste.
* **Historial de Servicios y Repuestos:** Registro de reparaciones, costos de mano de obra, piezas sustituidas y validación de costos atípicos mediante regla IQR $[Q1 - 1.5 \cdot \text{IQR}, Q3 + 1.5 \cdot \text{IQR}]$.
* **Servicios de Grúa (Towing):** Solicitud y seguimiento con geolocalización GPS, aplicando tratamiento de vacíos MAR ("No aplica") para servicios que no requirieron remolque.
* **Citas y Agenda de Taller:** Reserva, confirmación, reprogramación self-service y tablero diario para recepción.
* **Integración Climática (NOAA):** Registro de precipitaciones diarias y detección de eventos de lluvia extrema (>7.5 mm)[cite: 1].
* **Módulo de Inteligencia Artificial:** Evaluación preventiva de fallas, auditoría de costos atípicos y generación de resúmenes para mecánicos.
* **Auxilio QR y Localización:** Ficha técnica pública para emergencias y mapa interactivas de talleres/grúas.
* **Panel Administrativo:** Dashboard de KPIs, gestión de usuarios y visualización del cruce de datos taller vs. clima NOAA[cite: 1, 3, 5].

## 4. Requisitos Funcionales Principales (RF)
* **RF-01:** El sistema debe permitir registrar la aplicación de reparaciones y repuestos con tipo de servicio, costo, duración y mecánico asignado.
* **RF-02:** El sistema debe calcular si el costo total de un servicio es una anomalía aplicando los límites IQR específicos de la categoría de reparación.
* **RF-03:** El sistema debe registrar la solicitud de grúa con coordenadas GPS o asignar la bandera "No aplica" en servicios regulares sin remolque.
* **RF-04:** El sistema debe emitir alertas automáticas cuando la estación meteorológica registre precipitación superior a 7.5 mm.
* **RF-05:** El sistema debe permitir a los clientes confirmar, cancelar o reprogramar sus citas de taller desde la app móvil[cite: 3, 4].

## 5. Requisitos No Funcionales (RNF)
* **RNF-01 (Usabilidad):** Los flujos de confirmación de cita y solicitud de grúa urgente deben completarse en un máximo de 3 pasos[cite: 3, 4].
* **RNF-02 (Seguridad):** Toda contraseña debe ser almacenada mediante hash seguro y la comunicación debe realizarse bajo HTTPS con tokens JWT[cite: 3, 4].
* **RNF-03 (Calidad de Datos):** Ningún dato omitido en campos de grúa debe ser inventado; debe marcarse explícitamente como "No aplica" (MAR)[cite: 1].