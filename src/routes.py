from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import stripe
from src.models import Transaction
from src.database import SessionLocal

stripe.api_key = "your_stripe_secret_key"

router = APIRouter()

class PaymentRequest(BaseModel):
    amount: float
    currency: str
    description: str = None

@router.post('/pay')
async def create_payment(payment: PaymentRequest):
    try:
        charge = stripe.Charge.create(
            amount=int(payment.amount * 100),  # amount in cents
            currency=payment.currency,
            description=payment.description,
            source='tok_visa'  # test token, replace with real token from client
        )
        db = SessionLocal()
        transaction = Transaction(
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description,
            stripe_charge_id=charge.id,
            status=charge.status
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return {"transaction_id": transaction.id, "status": transaction.status}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
