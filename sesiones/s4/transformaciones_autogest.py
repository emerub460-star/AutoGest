"""
Sesión 4 · Minería de Datos · UNIMINUTO Ibagué
AutoGest — Matriz de features X e y desde motor_vehicle_limpio_propio.csv
 1. Seleccionar variables y justificar exclusiones
 2. Escalar con StandardScaler (verificar media~0, desv~1)
 3. One-hot encoding de categóricas (get_dummies dtype=int)
 4. Discretizar por cuartiles
 5. PCA (reducción exploratoria)
 6. Guardar X e y por separado
Ejecutar: python sesiones/s4/transformaciones_autogest.py
"""
from pathlib import Path
import warnings
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import KBinsDiscretizer, RobustScaler, StandardScaler

warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parents[2]
RUTA_LIMPIO = RAIZ / "data_pipeline" / "data" / "processed" / "motor_vehicle_limpio_propio.csv"
RUTA_OUT = RAIZ / "data_pipeline" / "data" / "processed"

NUMERICAS = ["Total Cost", "Service Duration Hours", "Estimated Cost",
             "Mileage at Service", "Technician Rating", "Tow Distance Miles"]
CATEGORICAS = ["Service Type", "Urgency Level"]

# ── 1. Carga y selección
print("Cargando dataset limpio…")
df = pd.read_csv(RUTA_LIMPIO, low_memory=False)
print(f"Dataset limpio: {df.shape}")

print("\n1 · SELECCIÓN DE VARIABLES")
print(f"Numéricas ({len(NUMERICAS)}): {NUMERICAS}")
print(f"Categóricas ({len(CATEGORICAS)}): {CATEGORICAS}")
print("Excluidas: id (Service ID), fechas (Repair/Towing Date), texto libre")
print("(Make and Model, Parts Used, nombres y ubicaciones) y banderas de auditoría")
print("por ser identificadores, texto no estructurado o derivadas del propio costo.")

# ── 2. Escalado
print("\n2 · StandardScaler sobre las numéricas")
X_num = df[NUMERICAS].astype(float)
scaler = StandardScaler()
X_std = pd.DataFrame(scaler.fit_transform(X_num), columns=NUMERICAS)
print("Medias tras escalar:", X_std.mean().round(4).to_dict())
print("Desv. estándar     :", X_std.std().round(4).to_dict())
assert (X_std.mean().abs() < 1e-6).all() and (X_std.std() - 1).abs().max() < 1e-4, "Escalado falló"

# ── 3. One-hot
print("\n3 · One-hot encoding (get_dummies dtype=int)")
X_cat = pd.get_dummies(df[CATEGORICAS].astype(str), columns=CATEGORICAS, dtype=int)
print(f"Columnas codificadas: {len(X_cat.columns)}")

# ── 4. Matriz final X
X = pd.concat([X_std, X_cat], axis=1)
print(f"\nMatriz X final: {X.shape}")

# ── 5. Variable objetivo y
print("\n4 · Variable objetivo (y)")
y = (df["Follow-up Needed"].eq("Yes")).astype(int).rename("requiere_seguimiento")
print("Distribución:")
print(y.value_counts(normalize=True).round(3).to_string())

# ── 6. Discretización (respaldada en cuartiles, rótulos de negocio)
print("\n5 · Discretización de Total Cost en 3 rangos (cuartiles)")
precio_bins = pd.qcut(df["Total Cost"], q=3, labels=["económico", "medio", "costoso"], duplicates="drop")
print(precio_bins.value_counts().to_string())

# ── 7. PCA exploratorio sobre numéricas estandarizadas
print("\n6 · PCA sobre numéricas estandarizadas")
pca = PCA()
componentes = pca.fit_transform(X_std)
razones = pca.explained_variance_ratio_
acum = razones.cumsum()
for i, r in enumerate(acum, 1):
    print(f"  {i} componente(s) explican {r*100:.1f}% acumulado")

# ── 8. Guardar X, y y scaler
X.to_csv(RUTA_OUT / "X_features.csv", index=False)
y.to_csv(RUTA_OUT / "y_objetivo.csv", index=False)
print(f"\nX guardada: {RUTA_OUT / 'X_features.csv'} ({X.shape})")
print(f"y guardada: {RUTA_OUT / 'y_objetivo.csv'} ({y.shape})")
print("FIN SESIÓN 4")