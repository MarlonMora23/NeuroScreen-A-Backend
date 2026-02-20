# NeuroScreen-A Backend

NeuroScreen-A es el backend para un sistema de detección temprana de alcoholismo. Proporciona servicios de procesamiento de datos EEG, inferencia de modelos de machine learning y gestión de usuarios y pacientes.

## Descripción
Este backend está diseñado para soportar la aplicación NeuroScreen-A, que ayuda en la detección temprana de alcoholismo mediante el análisis de registros EEG y la predicción basada en modelos de aprendizaje automático.

## Requisitos
- Docker
- Docker Compose

## Levantar el sistema con Docker
1. Asegúrate de tener Docker y Docker Compose instalados.
2. En la raíz del proyecto, ejecuta:

```
docker-compose up --build
```

Esto levantará todos los servicios necesarios.

## Ejecutar la aplicación manualmente
Si prefieres correr la aplicación sin Docker, instala las dependencias:

```
pip install -r requirements.txt
```

Luego ejecuta el backend:

```
python run.py
```

## Estructura del proyecto
- `app/`: Código fuente principal
- `dl_models/`: Modelos de machine learning
- `migrations/`: Migraciones de base de datos
- `tests/`: Pruebas unitarias

