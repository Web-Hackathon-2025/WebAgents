"""Payment API endpoints."""
from typing import Optional
from decimal import Decimal
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.client import get_db
from app.core.security.permissions import get_current_user
from app.db.models import User
from app.services.payment import payment_gateway, PaymentMethod
from app.core.exceptions import PaymentError, ValidationError
from app.utils.validators import validate_price


router = APIRouter(prefix="/payments", tags=["payments"])


class InitiatePaymentRequest(BaseModel):
    """Request to initiate payment."""
    booking_id: uuid.UUID
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    payment_method: PaymentMethod
    payment_intent_id: Optional[str] = None


class ProcessPaymentRequest(BaseModel):
    """Request to process payment."""
    transaction_id: uuid.UUID


class RefundRequest(BaseModel):
    """Request to refund payment."""
    transaction_id: uuid.UUID
    refund_amount: Optional[Decimal] = Field(None, gt=0, description="Amount to refund (null = full refund)")
    reason: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment transaction response."""
    id: uuid.UUID
    booking_id: uuid.UUID
    transaction_id: str
    payment_intent_id: str
    amount: Decimal
    currency: str
    status: str
    payment_method: Optional[str]
    failure_reason: Optional[str]
    refund_amount: Optional[Decimal]
    created_at: str
    completed_at: Optional[str]

    class Config:
        from_attributes = True


@router.post("/initiate", response_model=PaymentResponse)
async def initiate_payment(
    request: InitiatePaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initiate a payment transaction for a booking.
    
    - **booking_id**: ID of the booking to pay for
    - **amount**: Payment amount in PKR
    - **payment_method**: Payment method (card, wallet, cash)
    - **payment_intent_id**: Optional idempotency key
    
    Returns the created payment transaction.
    """
    try:
        # Validate amount
        validate_price(request.amount, min_price=Decimal("1"))
        
        # Initiate payment
        transaction = await payment_gateway.initiate_payment(
            db=db,
            booking_id=request.booking_id,
            amount=request.amount,
            payment_method=request.payment_method,
            payment_intent_id=request.payment_intent_id
        )
        
        return PaymentResponse(
            id=transaction.id,
            booking_id=transaction.booking_id,
            transaction_id=transaction.transaction_id,
            payment_intent_id=transaction.payment_intent_id,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            payment_method=transaction.payment_method,
            failure_reason=transaction.failure_reason,
            refund_amount=transaction.refund_amount,
            created_at=transaction.created_at.isoformat(),
            completed_at=transaction.completed_at.isoformat() if transaction.completed_at else None
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except PaymentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate payment: {str(e)}"
        )


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    request: ProcessPaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process a payment transaction.
    
    - **transaction_id**: ID of the transaction to process
    
    Returns the updated payment transaction with final status.
    May return status: completed, failed
    """
    try:
        # Process payment
        transaction = await payment_gateway.process_payment(
            db=db,
            transaction_id=request.transaction_id
        )
        
        return PaymentResponse(
            id=transaction.id,
            booking_id=transaction.booking_id,
            transaction_id=transaction.transaction_id,
            payment_intent_id=transaction.payment_intent_id,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            payment_method=transaction.payment_method,
            failure_reason=transaction.failure_reason,
            refund_amount=transaction.refund_amount,
            created_at=transaction.created_at.isoformat(),
            completed_at=transaction.completed_at.isoformat() if transaction.completed_at else None
        )
        
    except PaymentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process payment: {str(e)}"
        )


@router.post("/refund", response_model=PaymentResponse)
async def refund_payment(
    request: RefundRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Refund a completed payment (full or partial).
    
    - **transaction_id**: ID of the transaction to refund
    - **refund_amount**: Amount to refund (null for full refund)
    - **reason**: Reason for refund
    
    Returns the updated payment transaction.
    """
    try:
        # Validate refund amount if provided
        if request.refund_amount:
            validate_price(request.refund_amount, min_price=Decimal("1"))
        
        # Process refund
        transaction = await payment_gateway.refund_payment(
            db=db,
            transaction_id=request.transaction_id,
            refund_amount=request.refund_amount,
            reason=request.reason
        )
        
        return PaymentResponse(
            id=transaction.id,
            booking_id=transaction.booking_id,
            transaction_id=transaction.transaction_id,
            payment_intent_id=transaction.payment_intent_id,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            payment_method=transaction.payment_method,
            failure_reason=transaction.failure_reason,
            refund_amount=transaction.refund_amount,
            created_at=transaction.created_at.isoformat(),
            completed_at=transaction.completed_at.isoformat() if transaction.completed_at else None
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except PaymentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process refund: {str(e)}"
        )


@router.get("/{transaction_id}", response_model=PaymentResponse)
async def get_payment_status(
    transaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the current status of a payment transaction.
    
    - **transaction_id**: ID of the transaction
    
    Returns the payment transaction details.
    """
    try:
        transaction = await payment_gateway.get_transaction_status(
            db=db,
            transaction_id=transaction_id
        )
        
        return PaymentResponse(
            id=transaction.id,
            booking_id=transaction.booking_id,
            transaction_id=transaction.transaction_id,
            payment_intent_id=transaction.payment_intent_id,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            payment_method=transaction.payment_method,
            failure_reason=transaction.failure_reason,
            refund_amount=transaction.refund_amount,
            created_at=transaction.created_at.isoformat(),
            completed_at=transaction.completed_at.isoformat() if transaction.completed_at else None
        )
        
    except PaymentError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get payment status: {str(e)}"
        )
