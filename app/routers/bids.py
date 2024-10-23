from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from decimal import Decimal
import app.database.crud as crud
import app.models.py_schemas as py_schemas
from app.dependencies import get_db, get_current_user


router = APIRouter(tags=["ofertas"])


# ======================================================
# Crear una nueva puja para una operación específica
# ======================================================
@router.post(
    "/bid",
    response_model=py_schemas.BidResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva puja para una operación específica.",
    description="""Este endpoint permite a los usuarios con rol de 'inversor' crear una nueva puja para una operación específica. 
        Se validan diversas condiciones antes de proceder con la creación de la puja, como la existencia de la operación, si esta está cerrada, 
        si la fecha de la operación ha expirado, si el usuario ya ha realizado una puja para la operación y si el monto de la puja es válido. 
        En caso de que todas las validaciones sean satisfactorias, se crea la puja y se actualiza el monto recaudado de la operación correspondiente.""",
)
async def create_bid(
    bid_data: py_schemas.BidCreate,
    db: AsyncSession = Depends(get_db),
    current_user: py_schemas.User = Depends(get_current_user),
) -> py_schemas.BidResponse:

    # Verifica el rol de inversor
    if current_user.role != "inversor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a bid.",
        )

    operation = await crud.get_operation_by_id(db, bid_data.operation_id)

    # Verifica existencia de la operación
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found."
        )

    # Verifica que este abierta la operación
    if operation.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Operation is closed"
        )

    # Compara la Fecha actual con la de cierre de la operación
    if datetime.now(timezone.utc).date() > operation.deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation expired by date and time",
        )

    existing_bid = await crud.get_bid_by_investor_and_operation(
        db, current_user.id, bid_data.operation_id
    )

    # Revisa si el mismo usuario ya hizo una oferta
    if existing_bid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has already bid this operation",
        )

    # Se asegura de que el monto no sea cero
    if Decimal(bid_data.amount) <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount of the bid must be greater than zero",
        )

    # Verifica que no se exeda el valor del monto
    if Decimal(operation.amount_required) < Decimal(bid_data.amount) + Decimal(
        operation.amount_collected
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount of the bid exceeds the value",
        )

    try:
        # Crea la oferta
        bid = await crud.create_bid(db, bid_data, current_user)
        bid_response = py_schemas.BidResponse.model_validate(bid)

        # Actualiza la operación con el monto colectado
        await crud.update_operation_amount_collected(
            db, bid_data.operation_id, bid_data.amount
        )

        return bid_response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {e}",
        )


# ======================================================
# Obtener oferta por ID
# ======================================================
@router.get(
    "/bid/{bid_id}",
    response_model=py_schemas.BidResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener oferta por ID.",
    description="""Esta ruta permite obtener los detalles de una oferta específica utilizando su identificador único (ID). 
        La solicitud requiere que el usuario esté autenticado y que sea el inversor asociado a la oferta. 
        Si la oferta no existe, se devolverá un error 404. 
        Si el usuario no tiene permiso para acceder a esta oferta, se devolverá un error 403.""",
)
async def get_bid_by_id(
    bid_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: py_schemas.User = Depends(get_current_user),
) -> py_schemas.BidResponse:

    bid = await crud.get_bid_by_id(db, bid_id)

    # Verifica la existencia
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found."
        )

    # Comprueba el rol y si esa oferta es del ususario
    if current_user.role != "inversor" or current_user.id != bid.investor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this bid.",
        )

    return py_schemas.BidResponse.model_validate(bid)


# ======================================================
# Elimina una oferta específica utilizando su ID
# ======================================================
@router.delete(
    "/bid/{bid_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina una oferta específica utilizando su ID.",
    description="""Este endpoint permite a los usuarios inversores eliminar una oferta existente. 
        La solicitud debe incluir el ID de la oferta a eliminar. Se verifica que la oferta exista y que el usuario tenga permisos para eliminarla. 
        Además, no se puede eliminar una oferta si la operación asociada está cerrada. 
        Si la oferta se elimina correctamente, se actualizará el monto recaudado de la operación correspondiente.""",
)
async def delete_bid(
    bid_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: py_schemas.User = Depends(get_current_user),
):

    bid = await crud.get_bid_by_id(db, bid_id)

    # Verifica la existencia
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found."
        )

    # Comprueba rol y que sea el mismo usuario que creo la oferta
    if current_user.role != "inversor" or current_user.id != bid.investor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this bid.",
        )

    operation = await crud.get_operation_by_id(db, bid.operation_id)

    # Verifica si esta cerrada
    if operation.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Operation is closed"
        )

    try:
        # Actualiza el valor del monto colectado en la operación
        await crud.update_operation_amount_collected(
            db, bid.operation_id, bid.amount, is_addition=False
        )

        # Eliminación
        await crud.delete_bid_by_id(db, bid_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {e}",
        )


# ======================================================
# Obtener todas las ofertas de una operación específica
# ======================================================
@router.get(
    "/operation/{operation_id}/bids",
    response_model=List[py_schemas.BidResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener todas las ofertas de una operación específica.",
    description="""Este endpoint permite a los usuarios obtener todas las ofertas (pujas) asociadas a una operación específica. 
        Solo los usuarios con el rol de 'inversor' pueden acceder a esta información. 
        Si el usuario no es un inversor o no está autorizado para ver las ofertas de la operación indicada, se devolverá un error 403 (Prohibido). 
        Si no hay ofertas disponibles para la operación, se devolverá un error 404 (No encontrado).""",
)
async def get_bids_by_operation_id(
    operation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: py_schemas.User = Depends(get_current_user),
) -> List[py_schemas.BidResponse]:

    if current_user.role != "inversor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view bids.",
        )

    bids = await crud.get_bids_by_operation_id(db, operation_id)

    # Verifica la existencia
    if not bids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No bids found for this operation.",
        )

    # Comprueba que el usuario actual esté en la lista de los que invirtieron en esa operación
    if not current_user.id in [item.investor_id for item in bids]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view bids for this operation.",
        )

    return [py_schemas.BidResponse.model_validate(bid) for bid in bids]
