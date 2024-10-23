from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import app.database.crud as crud
import app.models.py_schemas as py_schemas
from app.dependencies import get_db, get_current_user


router = APIRouter(tags=["Operaciones"])


# ======================================================
# Crear una nueva operación (solo para operadores)
# ======================================================
@router.post(
    "/operation",
    response_model=py_schemas.Operation,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva operación (solo para operadores).",
    description="""Este endpoint permite a los operadores crear una nueva operación. 
        Solo los usuarios con el rol de "operador" tienen permiso para utilizar este endpoint. 
        Se valida que el monto requerido sea mayor que cero antes de proceder con la creación de la operación. 
        En caso de un error en la base de datos o un error interno, se retornará un mensaje correspondiente.""",
)
async def create_operation(
    operation_data: py_schemas.OperationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: py_schemas.User = Depends(get_current_user),
) -> py_schemas.Operation:

    if current_user.role != "operador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create an operation.",
        )

    if operation_data.amount_required <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The amount must be greater than zero.",
        )

    try:
        operation = await crud.create_operation(db, operation_data, current_user)
        return operation

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
# Eliminar una operación específica por ID
# ======================================================
# --- Eliminar operación (solo operadores) ---
@router.delete(
    "/operation/{operation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una operación específica por ID.",
    description="""Esta ruta permite a los operadores eliminar una operación específica, identificada por su operation_id. 
        Solo los usuarios con el rol de "operador" y que son el propietario de la operación pueden realizar esta acción. 
        Si la operación no se encuentra, se devolverá un error 404. 
        Si el usuario no tiene permisos suficientes, se devolverá un error 403. En caso de fallos en la base de datos o errores internos, se devolverá un error 500.""",
)
async def delete_operation(
    operation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: py_schemas.User = Depends(get_current_user),
):
    operation = await crud.get_operation_by_id(db, operation_id)

    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found."
        )

    if current_user.role != "operador" or current_user.id != operation.operator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this operation.",
        )

    try:
        await crud.delete_operation_by_id(db, operation_id)

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
# Listar operaciones activas
# ======================================================
@router.get(
    "/operations",
    response_model=List[py_schemas.Operation],
    status_code=status.HTTP_200_OK,
    summary="Listar operaciones activas.",
    description="""Este endpoint permite obtener una lista de todas las operaciones activas en el sistema. 
        Devuelve un conjunto de datos que incluye información relevante sobre cada operación, 
        como su estado, fecha de inicio y detalles asociados. Este endpoint es útil para 
        monitorear las operaciones que están actualmente en curso.""",
)
async def list_active_operations(
    db: AsyncSession = Depends(get_db),
) -> List[py_schemas.Operation]:

    operations = await crud.get_active_operations(db)
    return operations


# ======================================================
# Obtener información de una operación específica por su ID
# ======================================================
@router.get(
    "/operation/{operation_id}",
    response_model=py_schemas.Operation,
    status_code=status.HTTP_200_OK,
    summary="Obtener información de una operación específica por su ID.",
    description="""Este endpoint permite obtener los detalles de una operación existente en el sistema. 
        Se debe proporcionar el ID de la operación como parámetro en la URL. 
        Si la operación no se encuentra, se devolverá un error 404 con un mensaje indicando que la operación no fue encontrada.""",
)
async def get_operation(
    operation_id: int, 
    db: AsyncSession = Depends(get_db)
) -> py_schemas.Operation:

    operation = await crud.get_operation_by_id(db, operation_id)
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found."
        )

    return operation


# ======================================================
# Actualizar operaciones expiradas diariamente
# ======================================================
@router.put(
    "/operations/update-expired",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Actualizar operaciones expiradas diariamente.",
    description="""Esta ruta actualiza las operaciones que han expirado en el sistema. 
        Se ejecuta diariamente para asegurarse de que todas las operaciones vencidas sean gestionadas correctamente. 
        Si se produce un error en la base de datos o un error interno, se devuelve un código de error 500.""",
)
async def update_expired_operations(
    db: AsyncSession = Depends(get_db)
):
    try:
        await crud.update_expired_operations(db)

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )
