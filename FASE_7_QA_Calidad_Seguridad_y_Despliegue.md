
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