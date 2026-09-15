
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