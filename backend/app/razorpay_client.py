import os
from dotenv import load_dotenv
import razorpay

from datetime import datetime
from .models.payment import PaymentEvent, PaymentMethod, PaymentStatus, FailureCause
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET"),
    )
)

print("Razorpay client initialized")
print("Key ID loaded:", bool(os.getenv("RAZORPAY_KEY_ID")))

def fetch_payments():
    return client.payment.all({"count": 10})

def normalize_payment(payment):
    return {
        "payment_id": payment["id"],
        "amount": payment["amount"],
        "currency": payment["currency"],
        "status": payment["status"],
        "method": payment["method"],
        "failure_code": payment.get("error_code"),
        "failure_description": payment.get("error_description"),
        "failure_source": payment.get("error_source"),
        "failure_step": payment.get("error_step"),
        "failure_reason": payment.get("error_reason"),
        "created_at": payment["created_at"]
    }

def to_payment_event(payment):
    if payment["status"] == "failed":
        if payment["failure_source"] == "bank":
            failure_cause = FailureCause.BANK_DECLINED
        elif payment["failure_source"] == "provider":
            failure_cause = FailureCause.PROVIDER_ERROR
        else:
            failure_cause = FailureCause.UNKNOWN
    else:
        failure_cause = None

    return PaymentEvent(
        payment_id=payment["payment_id"],
        timestamp=datetime.fromtimestamp(payment["created_at"]),
        amount=payment["amount"] / 100,
        currency=payment["currency"],
        payment_method=PaymentMethod(payment["method"].upper()),
        provider="RAZORPAY",
        status=PaymentStatus.SUCCESS if payment["status"] == "captured" else PaymentStatus(payment["status"].upper()),
        failure_cause=failure_cause,
    )

def fetch_payment_events():
    payments = fetch_payments()

    events = []

    for payment in payments["items"]:
        if payment["status"] not in ["failed", "captured"]:
            continue

        normalized = normalize_payment(payment)
        event = to_payment_event(normalized)
        events.append(event)

    return events