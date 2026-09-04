from decimal import Decimal
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, model_validator

class PaymentMethod(str, Enum):
    UPI = "UPI"
    CARD = "CARD"
    NETBANKING = "NETBANKING"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class FailureCause(str, Enum):
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    PAYMENT_TIMEOUT = "TIMEOUT"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    BANK_DECLINED = "BANK_DECLINED"
    UNKNOWN = "UNKNOWN"


class PaymentEvent(BaseModel):
    payment_id: str
    timestamp: datetime
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    provider: str
    status: PaymentStatus
    failure_cause: FailureCause | None = None

    @model_validator(mode="after")
    def validate_failure_cause(self):
        if self.status == PaymentStatus.FAILED and self.failure_cause is None:
            raise ValueError("Failed payment must have a failure cause")
        
        if self.status != PaymentStatus.FAILED and self.failure_cause is not None:
            raise ValueError("Only failed payments can have a failure cause")

        return self