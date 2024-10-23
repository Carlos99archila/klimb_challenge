from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional, List
import uuid
from decimal import Decimal


# --- Esquema para la tabla Users ---
class UserBase(BaseModel):
    username: str
    role: str  # 'operador' o 'inversor'


class UserCreate(UserBase):
    password: str  # Necesitamos la contraseña solo en la creación


class User(UserBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Esquema para la tabla Bids ---
class OperationBase(BaseModel):
    amount_required: float
    interest_rate: float
    deadline: date


class OperationCreate(OperationBase):
    pass


class Operation(OperationBase):
    id: int
    operator_id: uuid.UUID
    amount_collected: float = 0.0
    is_closed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Esquema para la tabla Bids ---
class BidBase(BaseModel):
    amount: float
    interest_rate: float


class BidCreate(BidBase):
    operation_id: int


class Bid(BidBase):
    id: int
    bid_date: datetime

    model_config = ConfigDict(from_attributes=True)


class BidResponse(BaseModel):
    id: int
    operation_id: int
    investor_id: str
    amount: Decimal
    interest_rate: Decimal
    bid_date: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Esquemas para actualización ---
# Esquema para actualizar usuarios
class UserUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None


# Esquema para actualizar operaciones
class OperationUpdate(BaseModel):
    amount_required: Optional[float] = None
    interest_rate: Optional[float] = None
    deadline: Optional[date] = None
    is_closed: Optional[bool] = None


# Esquema para actualizar pujas
class BidUpdate(BaseModel):
    amount: Optional[float] = None
    interest_rate: Optional[float] = None
