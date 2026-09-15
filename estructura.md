## 2. Stack Tecnológico Seleccionado
* **Frontend Web:** React.js con Tailwind CSS para una interfaz responsive en computadores de taller.
* **Aplicación Móvil:** React Native con Expo para soporte multiplataforma (iOS/Android) y acceso a cámara/GPS.
* **Backend API:** Python (FastAPI) por su integración nativa con librerías de análisis de datos (`pandas`, `numpy`)[cite: 1, 3].
* **Base de Datos:** PostgreSQL para almacenamiento relacional normalizado y soporte de consultas de geolocalización[cite: 1, 3].
* **IA & LLM:** LangChain e integración con API de OpenAI/Claude para prompts estructurados en JSON.
* **Mapas & QR:** Leaflet con OpenStreetMap para geolocalización y librería `qrcode` / `html5-qrcode`.

## 3. Estructura de Directorios del Repositorio
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