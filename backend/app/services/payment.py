"""Mock payment gateway service for demo purposes."""
import uuid
import random
import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import PaymentTransaction, Booking
from app.core.exceptions import ValidationError, PaymentError


class PaymentMethod(str, Enum):
    """Supported payment methods."""
    CARD = "card"
    WALLET = "wallet"
    CASH = "cash"


class PaymentStatus(str, Enum):
    """Payment transaction statuses."""
    INITIATED = "initiated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class MockPaymentGateway:
    """
    Mock payment gateway for demo purposes.
    Simulates realistic payment processing including failures.
    """
    
    def __init__(self):
        self.simulation_delay = 1.5  # seconds
        # Failure simulation rates (for realistic demo)
        self.card_decline_rate = 0.05  # 5%
        self.network_timeout_rate = 0.03  # 3%
        self.insufficient_funds_rate = 0.02  # 2%
        
    async def initiate_payment(
        self,
        db: AsyncSession,
        booking_id: uuid.UUID,
        amount: Decimal,
        payment_method: PaymentMethod,
        payment_intent_id: Optional[str] = None
    ) -> PaymentTransaction:
        """
        Initiate a payment transaction.
        
        Args:
            db: Database session
            booking_id: ID of the booking
            amount: Payment amount
            payment_method: Payment method (card/wallet/cash)
            payment_intent_id: Idempotency key (optional)
            
        Returns:
            PaymentTransaction object
            
        Raises:
            ValidationError: If inputs are invalid
            PaymentError: If payment initiation fails
        """
        # Validate amount
        if amount <= 0:
            raise ValidationError("Payment amount must be positive")
        if amount > Decimal("1000000"):
            raise ValidationError("Payment amount exceeds maximum allowed")
            
        # Check booking exists
        result = await db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()
        if not booking:
            raise ValidationError(f"Booking {booking_id} not found")
            
        # Generate idempotency key if not provided
        if not payment_intent_id:
            payment_intent_id = f"pi_{uuid.uuid4().hex}"
            
        # Check for duplicate payment intent (idempotency)
        result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.payment_intent_id == payment_intent_id
            )
        )
        existing_txn = result.scalar_one_or_none()
        if existing_txn:
            # Return existing transaction (idempotent)
            return existing_txn
            
        # Create transaction record
        transaction = PaymentTransaction(
            booking_id=booking_id,
            transaction_id=f"txn_{uuid.uuid4().hex}",
            payment_intent_id=payment_intent_id,
            amount=amount,
            currency="PKR",
            status=PaymentStatus.INITIATED,
            payment_method=payment_method.value,
            gateway_response={
                "initiated_at": datetime.utcnow().isoformat(),
                "gateway": "mock_payment_gateway"
            }
        )
        
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        
        return transaction
    
    async def process_payment(
        self,
        db: AsyncSession,
        transaction_id: uuid.UUID
    ) -> PaymentTransaction:
        """
        Process a payment transaction.
        
        Args:
            db: Database session
            transaction_id: Payment transaction ID
            
        Returns:
            Updated PaymentTransaction object
            
        Raises:
            PaymentError: If payment processing fails
        """
        # Get transaction
        result = await db.execute(
            select(PaymentTransaction).where(PaymentTransaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()
        if not transaction:
            raise PaymentError(f"Transaction {transaction_id} not found")
            
        # Check current status
        if transaction.status not in [PaymentStatus.INITIATED, PaymentStatus.PROCESSING]:
            raise PaymentError(
                f"Cannot process transaction in {transaction.status} status"
            )
            
        # Update status to processing
        transaction.status = PaymentStatus.PROCESSING
        await db.commit()
        
        # Simulate processing delay
        await asyncio.sleep(self.simulation_delay)
        
        # Simulate payment outcomes
        random_value = random.random()
        
        if random_value < self.card_decline_rate:
            # Card declined
            transaction.status = PaymentStatus.FAILED
            transaction.failure_reason = "Card declined by issuer"
            transaction.gateway_response = {
                **transaction.gateway_response,
                "error_code": "card_declined",
                "error_message": "Your card was declined",
                "failed_at": datetime.utcnow().isoformat()
            }
            
        elif random_value < (self.card_decline_rate + self.network_timeout_rate):
            # Network timeout
            transaction.status = PaymentStatus.FAILED
            transaction.failure_reason = "Network timeout during processing"
            transaction.gateway_response = {
                **transaction.gateway_response,
                "error_code": "network_timeout",
                "error_message": "Connection timed out",
                "failed_at": datetime.utcnow().isoformat()
            }
            
        elif random_value < (self.card_decline_rate + self.network_timeout_rate + 
                            self.insufficient_funds_rate):
            # Insufficient funds
            transaction.status = PaymentStatus.FAILED
            transaction.failure_reason = "Insufficient funds"
            transaction.gateway_response = {
                **transaction.gateway_response,
                "error_code": "insufficient_funds",
                "error_message": "Insufficient funds in account",
                "failed_at": datetime.utcnow().isoformat()
            }
            
        else:
            # Success
            transaction.status = PaymentStatus.COMPLETED
            transaction.completed_at = datetime.utcnow()
            transaction.gateway_response = {
                **transaction.gateway_response,
                "authorization_code": f"AUTH{random.randint(100000, 999999)}",
                "completed_at": datetime.utcnow().isoformat()
            }
            
            # Update booking payment status
            result = await db.execute(
                select(Booking).where(Booking.id == transaction.booking_id)
            )
            booking = result.scalar_one_or_none()
            if booking:
                booking.payment_status = "paid"
        
        await db.commit()
        await db.refresh(transaction)
        
        return transaction
    
    async def refund_payment(
        self,
        db: AsyncSession,
        transaction_id: uuid.UUID,
        refund_amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> PaymentTransaction:
        """
        Refund a completed payment.
        
        Args:
            db: Database session
            transaction_id: Payment transaction ID
            refund_amount: Amount to refund (None = full refund)
            reason: Refund reason
            
        Returns:
            Updated PaymentTransaction object
            
        Raises:
            PaymentError: If refund fails
        """
        # Get transaction
        result = await db.execute(
            select(PaymentTransaction).where(PaymentTransaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()
        if not transaction:
            raise PaymentError(f"Transaction {transaction_id} not found")
            
        # Check if refundable
        if transaction.status != PaymentStatus.COMPLETED:
            raise PaymentError(
                f"Cannot refund transaction in {transaction.status} status"
            )
            
        # Determine refund amount
        if refund_amount is None:
            refund_amount = transaction.amount
        else:
            if refund_amount <= 0:
                raise ValidationError("Refund amount must be positive")
            if refund_amount > transaction.amount:
                raise ValidationError("Refund amount exceeds transaction amount")
                
        # Check if already refunded
        current_refund = transaction.refund_amount or Decimal("0")
        if current_refund + refund_amount > transaction.amount:
            raise PaymentError(
                f"Total refund ({current_refund + refund_amount}) exceeds "
                f"transaction amount ({transaction.amount})"
            )
            
        # Simulate refund delay
        await asyncio.sleep(0.5)
        
        # Process refund
        new_refund_total = current_refund + refund_amount
        
        if new_refund_total >= transaction.amount:
            transaction.status = PaymentStatus.REFUNDED
        else:
            transaction.status = PaymentStatus.PARTIALLY_REFUNDED
            
        transaction.refund_amount = new_refund_total
        transaction.refunded_at = datetime.utcnow()
        transaction.gateway_response = {
            **transaction.gateway_response,
            "refund_amount": float(refund_amount),
            "total_refunded": float(new_refund_total),
            "refund_reason": reason or "Customer request",
            "refunded_at": datetime.utcnow().isoformat()
        }
        
        # Update booking payment status
        result = await db.execute(
            select(Booking).where(Booking.id == transaction.booking_id)
        )
        booking = result.scalar_one_or_none()
        if booking:
            booking.payment_status = "refunded"
            
        await db.commit()
        await db.refresh(transaction)
        
        return transaction
    
    async def get_transaction_status(
        self,
        db: AsyncSession,
        transaction_id: uuid.UUID
    ) -> PaymentTransaction:
        """
        Get current status of a payment transaction.
        
        Args:
            db: Database session
            transaction_id: Payment transaction ID
            
        Returns:
            PaymentTransaction object
            
        Raises:
            PaymentError: If transaction not found
        """
        result = await db.execute(
            select(PaymentTransaction).where(PaymentTransaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()
        if not transaction:
            raise PaymentError(f"Transaction {transaction_id} not found")
            
        return transaction


# Singleton instance
payment_gateway = MockPaymentGateway()
