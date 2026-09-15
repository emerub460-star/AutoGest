
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