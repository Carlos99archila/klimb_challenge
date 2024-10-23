from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
import app.database.crud as crud
import app.models.py_schemas as py_schemas
from app.dependencies import get_db
from app.utils.token_generator import create_access_token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=["Usuarios"])


# ======================================================
# Crear un nuevo usuario
# ======================================================
@router.post(
    "/user",
    response_model=py_schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario.",
    description="""Esta ruta permite la creación de un nuevo usuario en el sistema. Recibe los datos necesarios para el registro, como el nombre de usuario y otra información relevante. 
        Antes de crear el usuario, verifica si el nombre de usuario ya está registrado. En caso afirmativo, devuelve un error con el código 400.
        Si ocurre algún error durante la creación del usuario, como un error en la base de datos o un error interno del servidor, se devuelve el código de error correspondiente.""",
)
async def create_user(
    user_create_data: py_schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
) -> py_schemas.User:

    if await crud.get_user_by_username(db, user_create_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already registered.",
        )

    try:
        user = await crud.create_user(db, user_create_data)
        return py_schemas.User.model_validate(user)

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )


# ======================================================
# Autenticar usuario mediante credenciales
# ======================================================
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Autenticar usuario mediante credenciales.",
    description="""Este endpoint permite a un usuario autenticarse en el sistema proporcionando su nombre de usuario y contraseña. 
        Si las credenciales son correctas, se genera un token de acceso (JWT) que se puede usar para autenticar futuras solicitudes. 
        En caso de error en las credenciales o problemas internos con la base de datos, se devolverán los códigos de estado HTTP correspondientes.""",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):

    user = await crud.get_user_by_username(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    try:
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )


# ======================================================
# Eliminar un usuario por su ID
# ======================================================
@router.delete(
    "/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un usuario por su ID.",
    description="""Esta ruta permite eliminar un usuario del sistema utilizando su ID. 
        Si el usuario no existe, se devuelve un error 404 (No encontrado). 
        En caso de un error en la base de datos o un error interno del servidor, se devuelve un error 500 (Error del servidor).""",
)
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):

    existing_user = await crud.get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    try:
        await crud.delete_user_by_id(db, user_id)

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )


# ======================================================
# Obtener información del usuario por ID
# ======================================================
@router.get(
    "/user/{user_id}",
    response_model=py_schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Obtener información del usuario por ID.",
    description="""Este endpoint permite obtener la información detallada de un usuario específico utilizando su identificador único. 
        Si el usuario no se encuentra en la base de datos, se devuelve un error 404 (No encontrado). 
        En caso de un error al acceder a la base de datos o un error interno, se devuelve un error 500 (Error interno del servidor).""",
)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):

    existing_user = await crud.get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    try:
        return py_schemas.User.model_validate(existing_user)

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )
