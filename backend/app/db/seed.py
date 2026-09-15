"""Seeder de la base de datos PostgreSQL de AutoGest.

Carga desde el pipeline de datos (data_pipeline/):
  - reglas IQR por tipo de servicio (completas)
  - clima diario de Ibagué (open-meteo, 1.827 días)
  - muestra determinista de servicios del dataset limpio
  - accidentes vehiculares (Colombia) y tráfico por peajes (INVIAS)

Ejecutar:  python -m app.db.seed [--reset] [--sample-size N]
"""
from __future__ import annotations

import argparse
import hashlib
import random
import re
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data_pipeline" / "data" / "raw"
PROCESSED = ROOT / "data_pipeline" / "data" / "processed"
OUTPUTS = ROOT / "data_pipeline" / "outputs"

SAMPLE_SIZE = 25_000
SAMPLE_SEED = 42

DEMO_USUARIOS = [
    ("Administrador AutoGest", "admin@autogest.co", "Admin.123", "ADMIN", "3150000001"),
    ("Recepcion AutoGest", "recepcion@autogest.co", "Recep.123", "RECEPCION", "3150000002"),
    ("Mecanico AutoGest", "mecanico@autogest.co", "Mecan.2026", "MECANICO", "3150000003"),
    ("Cliente Demo", "cliente@autogest.co", "Client.123", "CLIENTE", "3150000004"),
]


def now_str() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log(msg: str) -> None:
    print(f"[seed {now_str()}] {msg}", flush=True)


def _fixed(seed: int) -> random.Random:
    return random.Random(seed)


def derivar_placa(service_id: int) -> str:
    return f"AG{service_id:07d}"


def derivar_vin(service_id: int) -> str:
    h = hashlib.sha1(f"autogest-{service_id}".encode()).hexdigest().upper()
    return ("AGZ" + h[:14])[:17]


def derivar_anio(service_id: int) -> int:
    return 2015 + (service_id % 10)


def split_marca_modelo(make_and_model: str) -> tuple[str, str]:
    partes = str(make_and_model).strip().split()
    if len(partes) >= 2:
        return " ".join(partes[:-1]), partes[-1]
    if partes:
        return partes[0], partes[0]
    return "GENERICO", "AUTO"


def email_cliente(nombre: str, idx: int) -> str:
    slug = re.sub(r"[^a-z0-9]", "", nombre.lower())[:20] or "cliente"
    return f"{slug}.{idx:04d}@cliente.autogest.co"


def limpiar_miles(val: str) -> str:
    return str(val).replace(",", "").replace("$", "").strip()


def cargar_reglas(session_factory) -> None:
    from app.models.regla import ReglaIQR

    csv = OUTPUTS / "reglas_iqr_servicio.csv"
    df = pd.read_csv(csv)
    df = df[df["columna_costo"] == "Total_Cost"]

    session = session_factory()
    try:
        if session.query(ReglaIQR).count() > 0:
            log(f"reglas_iqr_servicio ya cargadas ({session.query(ReglaIQR).count()}); omitiendo")
            return
        session.bulk_insert_mappings(
            ReglaIQR,
            [
                {
                    "tipo_servicio": r["tipo_servicio"],
                    "q1_costo": Decimal(str(r["q1_costo"])),
                    "q3_costo": Decimal(str(r["q3_costo"])),
                    "iqr_costo": Decimal(str(r["iqr_costo"])),
                    "limite_inferior": Decimal(str(r["limite_inferior"])),
                    "limite_superior": Decimal(str(r["limite_superior"])),
                }
                for r in df.to_dict("records")
            ],
        )
        session.commit()
        log(f"reglas_iqr_servicio -> {len(df)} reglas (Total_Cost)")
    finally:
        session.close()


def cargar_clima(session_factory) -> None:
    from app.models.clima import ClimaNOAA

    csv = RAW / "clima_ibague_openmeteo.csv"
    df = pd.read_csv(csv, parse_dates=["fecha"])
    df["precipitacion_mm"] = df["precipitacion_mm"].map(lambda v: Decimal(str(v)))

    session = session_factory()
    try:
        if session.query(ClimaNOAA).count() > 0:
            log(f"clima_noaa ya cargado ({session.query(ClimaNOAA).count()} días); omitiendo")
            return
        session.bulk_insert_mappings(
            ClimaNOAA,
            [
                {
                    "fecha": r["fecha"].date(),
                    "estacion_id": "COM00080214",
                    "precipitacion_mm": r["precipitacion_mm"],
                    "temp_max_c": Decimal(str(r["temp_max_c"])),
                    "temp_min_c": Decimal(str(r["temp_min_c"])),
                    "imputado_mediana": False,
                }
                for r in df.to_dict("records")
            ],
        )
        session.commit()
        log(f"clima_noaa -> {len(df)} registros diarios")
    finally:
        session.close()


def cargar_accidentes(session_factory) -> None:
    from app.models.accidente import Accidente

    csv = RAW / "accidentes_vehiculares.csv.csv"
    df = pd.read_csv(csv, dtype={"COD_MUNI": str, "COD_DEPTO": str})
    df["FECHA HECHO"] = pd.to_datetime(df["FECHA HECHO"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["FECHA HECHO"])
    df["COD_DEPTO"] = df["COD_DEPTO"].str.zfill(2)
    df["COD_MUNI"] = df["COD_MUNI"].str.zfill(5)
    df["DEPARTAMENTO"] = df["DEPARTAMENTO"].str.upper().str.strip()
    df["MUNICIPIO"] = df["MUNICIPIO"].str.upper().str.strip()
    df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="coerce").fillna(0).astype(int)

    session = session_factory()
    try:
        if session.query(Accidente).count() > 0:
            log(f"accidentes ya cargados ({session.query(Accidente).count()}); omitiendo")
            return
        rows = [
            {
                "fecha_hecho": r["FECHA HECHO"].date(),
                "cod_depto": r["COD_DEPTO"],
                "departamento": r["DEPARTAMENTO"],
                "cod_muni": r["COD_MUNI"],
                "municipio": r["MUNICIPIO"],
                "cantidad": r["CANTIDAD"],
            }
            for r in df.to_dict("records")
        ]
        for i in range(0, len(rows), 10_000):
            session.bulk_insert_mappings(Accidente, rows[i : i + 10_000])
        session.commit()
        log(f"accidentes -> {len(rows)} registros")
    finally:
        session.close()


def cargar_trafico(session_factory) -> None:
    from app.models.trafico import TraficoVehicular

    csv = RAW / "trafico_vehicular.csv.csv"
    df = pd.read_csv(csv)
    df["Desde"] = pd.to_datetime(df["Desde"].map(limpiar_miles))
    df["Hasta"] = pd.to_datetime(df["Hasta"].map(limpiar_miles))
    df["ValorTarifa"] = df["ValorTarifa"].map(lambda v: Decimal(limpiar_miles(v)))
    df["CantidadTrafico"] = pd.to_numeric(df["CantidadTrafico"].map(limpiar_miles), errors="coerce").fillna(0).astype(int)
    df["CantidadEvasores"] = pd.to_numeric(df["CantidadEvasores"].map(limpiar_miles), errors="coerce").fillna(0).astype(int)
    df["CantidadExentos787"] = pd.to_numeric(df["CantidadExentos787"].map(limpiar_miles), errors="coerce").fillna(0).astype(int)
    df["Peaje"] = df["Peaje"].str.upper().str.strip()

    session = session_factory()
    try:
        if session.query(TraficoVehicular).count() > 0:
            log(f"trafico_vehicular ya cargado ({session.query(TraficoVehicular).count()}); omitiendo")
            return
        rows = [
            {
                "id_peaje": r["IdPeaje"],
                "peaje": r["Peaje"],
                "categoria_tarifa": r["CategoriaTarifa"],
                "periodo_desde": r["Desde"].date(),
                "periodo_hasta": r["Hasta"].date(),
                "valor_tarifa_cop": r["ValorTarifa"],
                "cantidad_trafico": r["CantidadTrafico"],
                "cantidad_evasores": r["CantidadEvasores"],
                "cantidad_exentos787": r["CantidadExentos787"],
            }
            for r in df.to_dict("records")
        ]
        for i in range(0, len(rows), 10_000):
            session.bulk_insert_mappings(TraficoVehicular, rows[i : i + 10_000])
        session.commit()
        log(f"trafico_vehicular -> {len(rows)} registros")
    finally:
        session.close()


def _leer_muestra(sample_size: int) -> pd.DataFrame:
    """Reservoir sampling determinista sobre el dataset limpio (2M filas)."""
    usecols = [
        "Service ID",
        "Customer Name",
        "Car",
        "Make and Model",
        "Service Type",
        "Service Description",
        "Repair Date",
        "Tow Location",
        "Tow Truck Driver",
        "Total Cost",
        "Estimated Cost",
        "Service Duration Hours",
        "Urgency Level",
        "Mileage at Service",
        "Total_Cost_Outlier_IQR",
        "Tow Location_es_no_aplica",
        "Tow Truck Driver_es_no_aplica",
    ]
    csv = PROCESSED / "motor_vehicle_limpio_propio.csv"

    try:
        cols_check = pd.read_csv(csv, nrows=0)
        usecols = [c for c in usecols if c in cols_check.columns]
    except Exception:
        pass

    rng = random.Random(SAMPLE_SEED)
    reservoir: list[pd.DataFrame] = []
    n_seen = 0

    for chunk in pd.read_csv(csv, usecols=usecols, chunksize=50_000):
        for i in range(len(chunk)):
            n_seen += 1
            if len(reservoir) < sample_size:
                reservoir.append(chunk.iloc[i])
            else:
                j = rng.randint(0, n_seen - 1)
                if j < sample_size:
                    reservoir[j] = chunk.iloc[i]

    return pd.concat(reservoir, axis=1).T if reservoir else pd.DataFrame()


def cargar_usuarios_y_vehiculos(session_factory, muestra: pd.DataFrame) -> tuple[dict, dict, list[int]]:
    """Crea usuarios demo + clientes reales de la muestra y vehículos."""
    from app.models.usuario import Usuario
    from app.models.vehiculo import Vehiculo

    from app.core.security import hash_password

    session = session_factory()
    try:
        for u in session.query(Usuario).all():
            session.delete(u)
        session.query(Vehiculo).delete()
        session.flush()

        id_mezcla: dict[str, int] = {}
        for nombre, email, pwd, rol, tel in DEMO_USUARIOS:
            u = Usuario(
                nombre_completo=nombre, email=email, password_hash=hash_password(pwd), telefono=tel, rol=rol
            )
            session.add(u)
            session.flush()
            id_mezcla[f"demo:{rol}"] = u.id_usuario
        log("usuarios demo -> " + ", ".join(f"{rol.lower()}@autogest.co" for _, _, _, rol, _ in DEMO_USUARIOS))

        clientes = muestra.groupby("Customer Name")["Service ID"].count().sort_values(ascending=False)
        top_clientes = clientes.iloc[:150]
        id_general: int | None = None
        map_cliente: dict[str, int] = {}
        for idx, (nombre, conteo) in enumerate(top_clientes.items()):
            u = Usuario(
                nombre_completo=str(nombre),
                email=email_cliente(str(nombre), idx),
                password_hash=hash_password("Client.123"),
                rol="CLIENTE",
                telefono=None,
            )
            session.add(u)
            session.flush()
            map_cliente[str(nombre)] = u.id_usuario
            if id_general is None:
                id_general = u.id_usuario

        session.commit()
        log(f"clientes de muestra -> {len(map_cliente)} cuentas (resto -> cliente general)")

        def cliente_id(nombre: object) -> int:
            key = str(nombre)
            return map_cliente.get(key, id_general)

        vehiculos_rows: dict[str, dict] = {}
        for r in muestra.to_dict("records"):
            placa = derivar_placa(int(r["Service ID"]))
            if placa not in vehiculos_rows:
                marca, modelo = split_marca_modelo(r["Make and Model"])
                vehiculos_rows[placa] = {
                    "vin": derivar_vin(int(r["Service ID"])),
                    "placa": placa,
                    "id_cliente": cliente_id(r["Customer Name"]),
                    "marca": marca,
                    "modelo": modelo,
                    "anio": derivar_anio(int(r["Service ID"])),
                    "tipo_combustible": "GNC" if marca == "GENERICO" else None,
                    "kilometraje_actual": int(r["Mileage at Service"] or 0),
                    "__sid": int(r["Service ID"]),
                }
        rows_veh = list(vehiculos_rows.values())
        for i in range(0, len(rows_veh), 5_000):
            session.bulk_insert_mappings(Vehiculo, rows_veh[i : i + 5_000])
        session.commit()
        log(f"vehiculos -> {len(rows_veh)} (placa derivada determinística, dataset sin placa raw)")

        mapa_placa: dict[str, int] = {}
        for id_v, placa in session.query(Vehiculo.id_vehiculo, Vehiculo.placa):
            mapa_placa[placa] = id_v
        ids_mecanicos = [u.id_usuario for u in session.query(Usuario).filter(Usuario.rol == "MECANICO")]
        return mapa_placa, ids_mecanicos, [id_general]
    finally:
        session.close()


def cargar_servicios_y_gruas(
    session_factory, muestra: pd.DataFrame, mapa_placa: dict[str, int], ids_mecanicos: list[int]
) -> None:
    from app.models.grua import ServicioGrua
    from app.models.servicio import ServicioReparacion
    from app.models.sede import SedeTaller

    session = session_factory()
    try:

        sede_id = session.query(SedeTaller.id_sede).first()[0]
        fecha_ok: set[date] = set()
        from app.models.clima import ClimaNOAA

        for (f,) in session.query(ClimaNOAA.fecha):
            fecha_ok.add(f)

        semilla = _fixed(SAMPLE_SEED)
        rows_serv, rows_grua = [], []
        for r in muestra.to_dict("records"):
            placa = derivar_placa(int(r["Service ID"]))
            vid = mapa_placa.get(placa)
            if vid is None:
                continue
            fserv = pd.to_datetime(r["Repair Date"]).date()
            if fserv not in fecha_ok:
                continue
            tipo = str(r["Service Type"] or "").strip()
            requiere_grua = tipo.lower() == "towing"
            mecanico_id = ids_mecanicos[semilla.randrange(len(ids_mecanicos))] if ids_mecanicos else None
            costo_total = Decimal(str(round(float(r["Total Cost"] or 0), 2)))
            costo_mano = Decimal(str(round(float(r["Estimated Cost"] or 0), 2)))
            dur = float(r["Service Duration Hours"] or 0)
            rows_serv.append(
                {
                    "id_vehiculo": vid,
                    "id_mecanico": mecanico_id,
                    "id_sede": sede_id,
                    "fecha_servicio": fserv,
                    "tipo_servicio": tipo,
                    "nivel_urgencia": str(r["Urgency Level"] or "MEDIA"),
                    "duracion_horas": Decimal(str(round(dur, 2))),
                    "costo_mano_obra": costo_mano,
                    "costo_total": costo_total,
                    "requirio_grua": requiere_grua,
                    "estado": "COMPLETADO",
                    "es_outlier_costo": bool(r["Total_Cost_Outlier_IQR"]),
                    "observaciones_tecnicas": str(r["Service Description"] or "")[:500] or None,
                }
            )
            if requiere_grua:
                conductor = (
                    "No aplica"
                    if bool(r["Tow Truck Driver_es_no_aplica"])
                    else str(r["Tow Truck Driver"] or "No aplica")
                )
                ubicacion = (
                    "No aplica"
                    if bool(r["Tow Location_es_no_aplica"])
                    else str(r["Tow Location"] or "No aplica")
                )
                rows_grua.append(
                    {
                        "conductor_grua": conductor,
                        "ubicacion_origen": ubicacion,
                        "latitud_origen": None,
                        "longitud_origen": None,
                        "estado": "FINALIZADA",
                    }
                )

        for i in range(0, len(rows_serv), 5_000):
            session.bulk_insert_mappings(ServicioReparacion, rows_serv[i : i + 5_000])
        session.flush()

        if rows_grua:
            ids_serv_grua = [sv.id_servicio for sv in session.query(ServicioReparacion).filter(ServicioReparacion.requirio_grua.is_(True))]
            for row, sid in zip(rows_grua, ids_serv_grua):
                row["id_servicio"] = sid
            for i in range(0, len(rows_grua), 5_000):
                session.bulk_insert_mappings(ServicioGrua, rows_grua[i : i + 5_000])

        session.commit()
        log(f"servicios_reparacion -> {len(rows_serv)} | servicios_grua -> {len(rows_grua)}")
    finally:
        session.close()


def cargar_citas(session_factory, ids_clientes: list[int]) -> None:
    from app.models.cita import Cita

    if not ids_clientes:
        return
    random.seed(7)
    session = session_factory()
    try:
        from app.models.sede import SedeTaller

        sede_id = session.query(SedeTaller.id_sede).first()[0]
        rows = []
        hoy = datetime.combine(date.today(), datetime.min.time())
        for i in range(60):
            cliente = random.choice(ids_clientes)
            delta = random.randint(-15, 30)
            estado = random.choices(
                ["CONFIRMADA", "PENDIENTE", "CANCELADA", "REPROGRAMADA", "FINALIZADA"],
                weights=[4, 3, 1, 1, 1],
            )[0]
            rows.append(
                {
                    "id_cliente": cliente,
                    "id_vehiculo": None,
                    "id_sede": sede_id,
                    "fecha_hora": hoy + timedelta(days=delta, hours=random.randint(8, 18)),
                    "motivo": random.choice(
                        [
                            "Cambio de aceite",
                            "Revisión de frenos",
                            "Diagnóstico motor",
                            "Rotación de llantas",
                            "Servicio preventivo",
                        ]
                    ),
                    "estado": estado,
                }
            )
        session.bulk_insert_mappings(Cita, rows)
        session.commit()
        log(f"citas -> {len(rows)} (extensión RF-05)")
    finally:
        session.close()


def crear_tablas(engine) -> None:
    from app.db.database import Base  # noqa: F401
    import app.models  # noqa: F401  (registra modelos en Base.metadata)

    Base.metadata.create_all(bind=engine)


def reset_bd(engine) -> None:
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE TABLE citas, servicios_grua, servicios_reparacion, vehiculos, "
                "reglas_iqr_servicio, clima_noaa, accidentes, trafico_vehicular, "
                "usuarios, sedes_taller RESTART IDENTITY CASCADE"
            )
        )


def crear_sedes(session_factory) -> None:
    from app.models.sede import SedeTaller

    session = session_factory()
    try:
        if session.query(SedeTaller).count() == 0:
            session.add_all(
                [
                    SedeTaller(
                        nombre="AutoGest Centro - Ibagué",
                        direccion="Cra 5a # 15-30, Centro, Ibagué (Tolima)",
                        latitud=Decimal("4.42190000"),
                        longitud=Decimal("-75.13310000"),
                    ),
                    SedeTaller(
                        nombre="AutoGest Norte - Ibagué",
                        direccion="Av. Ambalá Kim 6, Ibagué (Tolima)",
                        latitud=Decimal("4.45600000"),
                        longitud=Decimal("-75.21000000"),
                    ),
                ]
            )
            session.commit()
            log("sedes_taller -> 2 (Centro y Norte Ibagué)")
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seeder AutoGest / PostgreSQL")
    parser.add_argument("--reset", action="store_true", help="TRUNCATE todas las tablas antes de cargar")
    parser.add_argument("--sample-size", type=int, default=SAMPLE_SIZE)
    args = parser.parse_args()

    from app.db.database import SessionLocal, engine

    crear_tablas(engine)
    if args.reset:
        reset_bd(engine)
    crear_sedes(SessionLocal)
    cargar_reglas(SessionLocal)
    cargar_clima(SessionLocal)
    cargar_accidentes(SessionLocal)
    cargar_trafico(SessionLocal)

    log(f"leyendo muestra determinista de {args.sample_size} servicios (dataset limpio)...")
    if args.sample_size > 0:
        from app.models.servicio import ServicioReparacion

        with SessionLocal() as s:
            ya_cargados = s.query(ServicioReparacion).count()
        if ya_cargados:
            log(f"servicios_reparacion ya cargados ({ya_cargados}); omitiendo muestra")
        else:
            muestra = _leer_muestra(args.sample_size)
            mapa_placa, ids_mecanicos, ids_clientes = cargar_usuarios_y_vehiculos(SessionLocal, muestra)
            cargar_servicios_y_gruas(SessionLocal, muestra, mapa_placa, ids_mecanicos)
            cargar_citas(SessionLocal, ids_clientes)
    else:
        # Solo tablas estáticas (reglas, clima, accidentes, tráfico)
        log("sin muestra de servicios (--sample-size 0)")
    log("SEED COMPLETADO")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "backend"))
    main()