
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