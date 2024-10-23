# Klimb Challenge - Sistema de Subastas para Operaciones Financieras

Este proyecto es una solución para el challenge de un sistema de subastas en tiempo real para operaciones financieras. Está construido utilizando FastAPI y SQLAlchemy, con una base de datos MySQL.

[Video Tutorial de ejecución](https://youtu.be/6ocFro_jHXw)
<div align="center">
    <a href="./">
        <img src="./docs/API.png" width="80%"/>
    </a>
</div>

## Requisitos

- Python 3.11.9
- WampServer (para MySQL)
- Entorno virtual (recomendado)

## Instalación

### 1. Instalación de WampServer
- Descarga e instala [WampServer](https://www.wampserver.com/en/).
- Abre WampServer y navega a `localhost` en tu navegador.
- Ve a `phpMyAdmin` y crea una base de datos MySQL llamada `klimb_challenge`.

### 2. Clonar el Repositorio
Clona este repositorio localmente:

```bash
git clone https://github.com/Carlos99archila/klimb_challenge.git
cd klimb_challenge
```

### 3. Crear la Base de Datos
- Abre phpMyAdmin y selecciona la base de datos klimb_challenge.
- Copia y pega el contenido del archivo docs/create_tables.sql en la sección de SQL de phpMyAdmin y ejecútalo. Esto creará las tablas necesarias para el proyecto.

### 4. Crear un entorno virtual
Crea un entorno virtual con Python 3.11.9:

``` bash
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# o
.\.venv\Scripts\activate  # En Windows
```

### 5. Instalar Dependencias
Instala las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

### 6. Ejecutar la Aplicación
Para ejecutar la API:

``` bash
uvicorn app.main:app --reload
```
Esto levantará el servidor en `http://127.0.0.1:8000/`. Puedes acceder a la documentación interactiva de la API en `http://127.0.0.1:8000/docs`.

### 7. Ejecutar Pruebas
Para ejecutar las pruebas unitarias:
```bash
pytest tests/test_users.py
```
