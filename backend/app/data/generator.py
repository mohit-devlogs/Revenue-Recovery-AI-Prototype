import random

from decimal import Decimal

from ..models.payment import PaymentEvent, PaymentMethod, PaymentStatus, FailureCause


PROVIDERS = [
    "Provider_A",
    "Provider_B",
    "Provider_C",
    "Provider_D"
]

def generate_payment(timestamp, degraded_provider = None):
    payment_id = f"payment_{random.randint(1, 1000000)}"
    amount = Decimal(random.randint(100, 100000))
    payment_method = random.choice(list(PaymentMethod))
    status_rand = random.random()
    provider = random.choice(PROVIDERS)

    if provider == degraded_provider:
        success_probability = 0.50
    else:
        success_probability = 0.95

    if status_rand < success_probability:
        status = PaymentStatus.SUCCESS
    else:
        status = PaymentStatus.FAILED
    
    if status == PaymentStatus.FAILED:
        failure_cause = random.choice(list(FailureCause))
    else:
        failure_cause = None


    return PaymentEvent(
    payment_id=payment_id,
    timestamp=timestamp,
    amount=amount,
    currency="INR",
    payment_method=payment_method,
    provider=provider,
    status=status,
    failure_cause=failure_cause
    )