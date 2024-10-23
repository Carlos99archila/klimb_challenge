# Klimb Challenge - Sistema de Subastas para Operaciones Financieras

Este proyecto es una solución para el challenge de un sistema de subastas en tiempo real para operaciones financieras. Está construido utilizando FastAPI y SQLAlchemy, con una base de datos MySQL.

<div align="center">
    <a href="https://youtu.be/6ocFro_jHXw">Ver el tutorial de implementación y ejecución</a>
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
- Abre `phpMyAdmin`, crea una base de datos llamada `klimb_challenge` e ingresa en ella.
- Copia y pega el contenido del archivo `docs/create_tables.sql` en la sección de `SQL de phpMyAdmin` y ejecútalo. Esto creará las tablas necesarias para el proyecto.

<div align="center">
    <figure style="display: inline-block; text-align: center;">
        <a href="./docs/db_wamp_server.png">
            <img src="./docs/db_wamp_server.png" width="100%" />
        </a>
        <figcaption>Base de datos con las tablas.</figcaption>
    </figure>
</div>



### 4. Crear un entorno virtual
Crea un entorno virtual con Python 3.11.9:

``` bash
.venv\Scripts\activate
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

<div align="center">
    <figure style="display: inline-block; text-align: center;">
        <a href="./docs/API.png">
            <img src="./docs/API.png" width="100%"/>
        </a>
        <figcaption>API cargada y documentada</figcaption>
    </figure>
</div>

<br>

Luego de realizar pruebas, la base de datos deberia lucir algo asi.
<div align="center">
    <figure style="display: inline-block; text-align: center;">
        <a href="./docs/database.png">
            <img src="./docs/database.png" width="100%" />
        </a>
        <figcaption>Database con las pruebas realizadas en el video</figcaption>
    </figure>
</div>

### 7. Ejecutar Pruebas
Para ejecutar las pruebas unitarias:
```bash
pytest tests/test_users.py
```

## Tecnologías Utilizadas
- FastAPI: Para la creación de la API.
- SQLAlchemy: Para interactuar con la base de datos MySQL.
- JWT: Para la autenticación de usuarios y roles.
- MySQL: Base de datos utilizada.
- Uvicorn: Servidor ASGI para ejecutar la API.
- pytest: Para las pruebas unitarias.
  
## Funcionalidades
Rutas de usuarios:
- `POST` _/users_: Crear un nuevo usuario.
- `POST` _/login_: Autenticar usuario mediante credenciales.
- `GET` _/user/{user_id}_: Obtener información del usuario por ID.
- `DELETE` _/user/{user_id}_: Eliminar un usuario por su ID.
  
Rutas de operaciones:
- `POST` _/operation_: Crear una nueva operación (solo para operadores).
- `GET` _/operations_: Listar operaciones activas.
- `GET` _/operation/{operation_id}_: Obtener información de una operación específica por su ID.
- `PUT` _/operations/update-expired_: Actualizar operaciones expiradas diariamente.
- `DELETE` _/operation/{operation_id}_: Eliminar una operación específica por ID.
  
Rutas de pujas:
- `POST` _/bid_: Crear una nueva puja para una operación específica (solo para inversores).
- `GET` _/bid/{bid_id}_: Obtener información de una oferta por ID.
- `GET` _/operation/{operation_id}/bids_: Obtener todas las ofertas de una operación específica.
- `DELETE` _/bid/{bid_id}_: Elimina una oferta específica utilizando su ID.

## Decisiones de Diseño
- FastAPI: Se eligió por su rendimiento superior, soporte para asincronía y su documentación interactiva integrada.
- Autenticación JWT: Se implementó para asegurar rutas sensibles y manejar de forma eficiente la autenticación basada en roles (Operador e Inversor).
- SQLAlchemy con MySQL: Facilita el ORM para gestionar las consultas a la base de datos, asegurando la escalabilidad y portabilidad del código.
- Separación de roles: Los permisos se manejan a nivel de API, permitiendo que los operadores creen operaciones y los inversores hagan pujas.

## Escalabilidad y Trabajo Futuro
- Escalabilidad: El sistema puede escalar fácilmente implementando balanceadores de carga y usando una base de datos distribuida. Además, al estar construido con FastAPI y SQLAlchemy, se puede optimizar para manejar mayor concurrencia con servicios en la nube como AWS o GCP.

- Trabajo Futuro:
    - Implementar WebSockets para subastas en tiempo real.
    - Añadir paginación y filtros avanzados en las rutas de operaciones.
    - Mejorar la seguridad con monitoreo de actividad sospechosa y protección contra ataques de fuerza bruta.
