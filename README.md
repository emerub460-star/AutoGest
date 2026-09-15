ARCHIVOS csv crudos, y limpios

https://drive.google.com/drive/folders/171LEWq4gbTWnYwt4YLRXASdoSgH9aXcq?usp=sharing

# FASE_1_Planificacion_y_Requisitos.md

AutoGest — Fase 1: Planificación y Requisitos

 1. Visión General del Sistema
AutoGest es una plataforma híbrida Web y Móvil orientada a la gestión de servicios de taller automotriz, mantenimientos preventivos y auxilio mecánico mediante grúas. El sistema integra el análisis de un dataset de más de 2,000,000 de registros reales de reparación y remolque con datos meteorológicos de la estación NOAA `COM00080214` (PERALES) para relacionar eventos de clima extremo (>7.5 mm de lluvia) con la demanda de servicios.

 2. Roles del Sistema
* **Cliente / Conductor:** Administra sus vehículos, consulta historiales, programa citas, solicita grúas de emergencia y accede a su ficha técnica QR.
* **Mecánico:** Registra diagnósticos, reparaciones, repuestos instalados y consulta resúmenes ejecutivos del historial generados por IA.
* **Personal de Recepción:** Gestiona el flujo de ingreso de vehículos, agenda de citas, asignación de turnos y despacho de grúas.
* **Administrador:** Administra usuarios, sedes, reglas de negocio (límites IQR por categoría de servicio) y analiza las métricas operativas vs. clima[cite: 1, 3, 5].

 3. Módulos Funcionales del MVP
* **Autenticación y RBAC:** Registro, inicio de sesión seguro y control de acceso basado en roles[cite: 3, 5].
* **Gestión de Vehículos:** Registro de ficha técnica (marca, modelo, año, VIN, placa, kilometraje) y seguimiento de desgaste.
* **Historial de Servicios y Repuestos:** Registro de reparaciones, costos de mano de obra, piezas sustituidas y validación de costos atípicos mediante regla IQR $[Q1 - 1.5 \cdot \text{IQR}, Q3 + 1.5 \cdot \text{IQR}]$.
* **Servicios de Grúa (Towing):** Solicitud y seguimiento con geolocalización GPS, aplicando tratamiento de vacíos MAR ("No aplica") para servicios que no requirieron remolque.
* **Citas y Agenda de Taller:** Reserva, confirmación, reprogramación self-service y tablero diario para recepción.
* **Integración Climática (NOAA):** Registro de precipitaciones diarias y detección de eventos de lluvia extrema (>7.5 mm)[cite: 1].
* **Módulo de Inteligencia Artificial:** Evaluación preventiva de fallas, auditoría de costos atípicos y generación de resúmenes para mecánicos.
* **Auxilio QR y Localización:** Ficha técnica pública para emergencias y mapa interactivas de talleres/grúas.
* **Panel Administrativo:** Dashboard de KPIs, gestión de usuarios y visualización del cruce de datos taller vs. clima NOAA[cite: 1, 3, 5].

 4. Requisitos Funcionales Principales (RF)
* **RF-01:** El sistema debe permitir registrar la aplicación de reparaciones y repuestos con tipo de servicio, costo, duración y mecánico asignado.
* **RF-02:** El sistema debe calcular si el costo total de un servicio es una anomalía aplicando los límites IQR específicos de la categoría de reparación.
* **RF-03:** El sistema debe registrar la solicitud de grúa con coordenadas GPS o asignar la bandera "No aplica" en servicios regulares sin remolque.
* **RF-04:** El sistema debe emitir alertas automáticas cuando la estación meteorológica registre precipitación superior a 7.5 mm.
* **RF-05:** El sistema debe permitir a los clientes confirmar, cancelar o reprogramar sus citas de taller desde la app móvil[cite: 3, 4].

 5. Requisitos No Funcionales (RNF)
* **RNF-01 (Usabilidad):** Los flujos de confirmación de cita y solicitud de grúa urgente deben completarse en un máximo de 3 pasos[cite: 3, 4].
* **RNF-02 (Seguridad):** Toda contraseña debe ser almacenada mediante hash seguro y la comunicación debe realizarse bajo HTTPS con tokens JWT[cite: 3, 4].
* **RNF-03 (Calidad de Datos):** Ningún dato omitido en campos de grúa debe ser inventado; debe marcarse explícitamente como "No aplica" (MAR)[cite: 1].




# FASE_2_Arquitectura_e_Infraestructura.md

 AutoGest — Fase 2: Arquitectura e Infraestructura

1. Arquitectura General del Sistema
AutoGest implementa una arquitectura cliente-servidor desacoplada basada en una API REST centralizada. Tanto la aplicación web de taller/administración como la aplicación móvil para conductores consumen los mismos endpoints de negocio y persistencia[cite: 3, 5].

┌─────────────────────────┐        ┌─────────────────────────┐
│   App Móvil (Cliente)   │        │   App Web (Taller/Admin)│
│ (React Native / Expo)   │        │     (React / Web)       │
└────────────┬────────────┘        └────────────┬────────────┘
│                                  │
└──────────────────┬───────────────┘
│ HTTPS / REST API (JSON)
▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend API REST (FastAPI)                  │
│  ┌──────────────────┬───────────────────┬────────────────┐  │
│  │ Auth (JWT / RBAC)│ Gestión Servicios │ Dispatcher Grúa│  │
│  └──────────────────┴───────────────────┴────────────────┘  │
└───────┬───────────────────┬───────────────────┬─────────────┘
│                   │                   │
▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌───────────────────────────┐
│ Base de Datos│    │ Motor de IA  │    │ Servicios Externos        │
│ Relacional    │    │ y Analytics  │    │ ├─ Leaflet / OpenStreetMap│
│ (PostgreSQL) │    │ (Python/IQR) │    │ ├─ NOAA Weather Station   │
└──────────────┘    └──────────────┘    │ └─ Firebase Notifications │
└───────────────────────────┘


2. Stack Tecnológico Seleccionado
* **Frontend Web:** React.js con Tailwind CSS para una interfaz responsive en computadores de taller.
* **Aplicación Móvil:** React Native con Expo para soporte multiplataforma (iOS/Android) y acceso a cámara/GPS.
* **Backend API:** Python (FastAPI) por su integración nativa con librerías de análisis de datos (`pandas`, `numpy`)[cite: 1, 3].
* **Base de Datos:** PostgreSQL para almacenamiento relacional normalizado y soporte de consultas de geolocalización[cite: 1, 3].
* **IA & LLM:** LangChain e integración con API de OpenAI/Claude para prompts estructurados en JSON.
* **Mapas & QR:** Leaflet con OpenStreetMap para geolocalización y librería `qrcode` / `html5-qrcode`.

 3. Estructura de Directorios del Repositorio
```text
AutoGest/
├── apps/
│   ├── web/                 # Panel Web Taller & Admin (React)
│   └── mobile/              # App Móvil Conductor (React Native)
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Routers HTTP (auth, vehiculos, servicios, ia)
│   │   ├── core/            # Configuración JWT y seguridad
│   │   ├── db/              # Conexión SQLAlchemy y sesiones
│   │   ├── models/          # ORM SQL
│   │   ├── schemas/         # Pydantic DTOs
│   │   └── services/        # Reglas IQR, clima e integración LLM
│   └── requirements.txt
├── data_pipeline/           # Pipeline de procesamiento de datos y clima
│   ├── data/
│   │   ├── raw/             # Excluido en .gitignore
│   │   └── processed/       # Excluido en .gitignore
│   └── scripts/             # Limpieza, cruce left join e IQR
└── .gitignore



# FASE_3_Datos_y_Backend_Base.md

# AutoGest — Fase 3: Datos y Backend Base

## 1. Esquema de Base de Datos Relacional (PostgreSQL SQL)

```sql
CREATE TYPE rol_usuario AS ENUM ('CLIENTE', 'MECANICO', 'RECEPCION', 'ADMIN');
CREATE TYPE estado_cita AS ENUM ('PENDIENTE', 'CONFIRMADA', 'REPROGRAMADA', 'CANCELADA', 'FINALIZADA');
CREATE TYPE estado_servicio AS ENUM ('EN_DIAGNOSTICO', 'EN_REPARACION', 'ESPERA_REPUESTOS', 'COMPLETADO', 'ENTREGADO');
CREATE TYPE estado_grua AS ENUM ('NO_APLICA', 'SOLICITADA', 'EN_CAMINO', 'REMOLCANDO', 'FINALIZADA');

CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(120) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    rol rol_usuario NOT NULL DEFAULT 'CLIENTE',
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sedes_taller (
    id_sede SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    latitud NUMERIC(10, 8),
    longitud NUMERIC(11, 8)
);

CREATE TABLE vehiculos (
    id_vehiculo SERIAL PRIMARY KEY,
    id_cliente INT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    vin VARCHAR(17) UNIQUE,
    placa VARCHAR(15) UNIQUE NOT NULL,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    anio INT NOT NULL,
    tipo_combustible VARCHAR(30),
    kilometraje_actual INT NOT NULL DEFAULT 0
);

CREATE TABLE clima_noaa (
    fecha DATE PRIMARY KEY,
    estacion_id VARCHAR(20) DEFAULT 'COM00080214',
    precipitacion_mm NUMERIC(6,2) NOT NULL DEFAULT 0.00,
    temp_max_c NUMERIC(4,1),
    temp_min_c NUMERIC(4,1),
    es_lluvia_extrema BOOLEAN GENERATED ALWAYS AS (precipitacion_mm > 7.5) STORED,
    imputado_mediana BOOLEAN DEFAULT FALSE
);

CREATE TABLE reglas_iqr_servicio (
    id_regla SERIAL PRIMARY KEY,
    tipo_servicio VARCHAR(80) UNIQUE NOT NULL,
    q1_costo NUMERIC(10,2) NOT NULL,
    q3_costo NUMERIC(10,2) NOT NULL,
    iqr_costo NUMERIC(10,2) NOT NULL,
    limite_inferior NUMERIC(10,2) NOT NULL,
    limite_superior NUMERIC(10,2) NOT NULL
);

CREATE TABLE servicios_reparacion (
    id_servicio SERIAL PRIMARY KEY,
    id_vehiculo INT NOT NULL REFERENCES vehiculos(id_vehiculo),
    id_mecanico INT REFERENCES usuarios(id_usuario),
    id_sede INT NOT NULL REFERENCES sedes_taller(id_sede),
    fecha_servicio DATE NOT NULL REFERENCES clima_noaa(fecha),
    tipo_servicio VARCHAR(80) NOT NULL,
    nivel_urgencia VARCHAR(20) NOT NULL,
    duracion_horas NUMERIC(4,2) NOT NULL,
    costo_mano_obra NUMERIC(10,2) NOT NULL,
    costo_total NUMERIC(10,2) NOT NULL,
    requirio_grua BOOLEAN NOT NULL DEFAULT FALSE,
    estado estado_servicio NOT NULL DEFAULT 'EN_DIAGNOSTICO',
    es_outlier_costo BOOLEAN DEFAULT FALSE,
    observaciones_tecnicas TEXT
);

CREATE TABLE servicios_grua (
    id_grua SERIAL PRIMARY KEY,
    id_servicio INT UNIQUE REFERENCES servicios_reparacion(id_servicio) ON DELETE CASCADE,
    aplica_grua BOOLEAN NOT NULL DEFAULT TRUE,
    conductor_grua VARCHAR(120) DEFAULT 'No aplica',
    ubicacion_origen TEXT DEFAULT 'No aplica',
    latitud_origen NUMERIC(10, 8),
    longitud_origen NUMERIC(11, 8),
    estado estado_grua NOT NULL DEFAULT 'SOLICITADA'
);






# FASE_4_Modulos_Operativos_Principales.md

# AutoGest — Fase 4: Módulos Operativos Principales

## 1. Módulo de Vehículos y Kilometraje
Permite el registro técnico de automóviles, garantizando el aislamiento de datos por usuario. Incluye actualización periódica de kilometraje con validación defensiva contra retrocesos arbitrarios.

```python
@router.patch("/{id_vehiculo}/kilometraje")
def actualizar_kilometraje(id_vehiculo: int, datos: LecturaKilometrajeCreate, db: Session = Depends(get_db), user: dict = Depends(require_roles(["CLIENTE", "MECANICO", "RECEPCION", "ADMIN"]))):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id_vehiculo == id_vehiculo).first()
    if user["rol"] == "CLIENTE" and vehiculo.id_cliente != user["sub"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    if datos.kilometraje < vehiculo.kilometraje_actual:
        raise HTTPException(status_code=400, detail="Kilometraje inferior al actual")
    vehiculo.kilometraje_actual = datos.kilometraje
    db.commit()
    return {"status": "ok", "kilometraje_actual": vehiculo.kilometraje_actual}



 # FASE_5_IA_y_Analisis_Climatico.md

# AutoGest — Fase 5: Módulo de IA y Análisis Climático

## 1. Evaluación Preventiva de Fallas e Impacto Climático
El módulo analiza los síntomas descritos por el conductor combinándolos con el registro más reciente de la estación meteorológica NOAA `COM00080214` (PERALES)[cite: 1, 3].

**Restricción de Seguridad:** La IA no realiza diagnósticos mecánicos definitivos ni aprueba cotizaciones; emite sugerencias de inspección y evalúa factores de riesgo por clima adverso[cite: 3].

```python
def evaluar_riesgo_preventivo(id_vehiculo: int, sintomas: str, db: Session) -> dict:
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id_vehiculo == id_vehiculo).first()
    clima = db.query(ClimaNOAA).order_by(ClimaNOAA.fecha.desc()).first()
    
    contexto = {
        "vehiculo": {"marca": vehiculo.marca, "modelo": vehiculo.modelo, "km": vehiculo.kilometraje_actual},
        "sintomas": sintomas,
        "clima": {"precipitacion_mm": float(clima.precipitacion_mm), "lluvia_extrema": clima.es_lluvia_extrema}
    }
    
    system_prompt = "Actúas como asistente preventivo de AutoGest. Genera recomendaciones en JSON sin dar diagnósticos definitivos."
    response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": json.dumps(contexto)}])
    return json.loads(response.choices[0].message.content)




# FASE_6_Emergencias_Geolocalizacion_y_Frontend.md

# AutoGest — Fase 6: Emergencias, Geolocalización y Frontend

## 1. Ficha Técnica y Código QR de Auxilio
Cada vehículo posee un código QR único que apunta a una vista pública optimizada[cite: 3]. Muestra datos de remolque (tracción, transmisión), contactos de emergencia y seguro, excluyendo intencionalmente información personal privada[cite: 3].

```python
def generar_qr_vehiculo(id_vehiculo: int, db: Session) -> str:
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id_vehiculo == id_vehiculo).first()
    url_publica = f"[https://autogest.app/auxilio/qr/](https://autogest.app/auxilio/qr/){vehiculo.vin}"
    img = qrcode.make(url_publica)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")




# FASE_7_QA_Calidad_Seguridad_y_Despliegue.md

# AutoGest — Fase 7: QA, Calidad, Seguridad y Despliegue

## 1. Plan de Pruebas QA
* **TC-001 (Auth):** Intento de login con credenciales inválidas. Retorna HTTP 401[cite: 3].
* **TC-002 (Vehículos):** Intento de registro con placa duplicada. Retorna HTTP 400[cite: 3].
* **TC-003 (IQR Costos):** Registro de servicio con costo fuera de rango. Asigna bandera `es_outlier_costo = True`[cite: 1, 3].
* **TC-004 (MAR Grúa):** Servicio regular sin remolque. Asigna `"No aplica"` en datos de grúa[cite: 1].
* **TC-005 (IA Clima):** Consulta de síntomas en día con lluvia > 7.5 mm. Retorna nivel de riesgo elevado y recomendaciones de seguridad[cite: 1, 3].

## 2. Depuración Frontend (`App.jsx`)
Resolución de error `Uncaught ReferenceError: Vehiculos is not defined`:
```jsx
// Correcta importación del componente en App.jsx
import Vehiculos from './pages/Vehiculos';

function App() {
  return (
    <Routes>
      <Route element="{<Vehiculos" path="/vehiculos"/>} />
    </Routes>
  );
}






