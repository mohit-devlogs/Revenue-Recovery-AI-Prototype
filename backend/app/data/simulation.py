from datetime import datetime, timedelta

from .generator import generate_payment


def generate_dataset():
    payments = []

    start_time = datetime(2026, 8, 28, 10, 0, 0)

    for minute in range(60):
        timestamp = start_time + timedelta(minutes=minute)

        if minute >= 30:
            degraded_provider = "Provider_C"
        else:
            degraded_provider = None

        for _ in range(100):
            payment = generate_payment(timestamp, degraded_provider)
            payments.append(payment)

    return payments

if __name__ == "__main__":
    payments = generate_dataset()

    print("Total payments:", len(payments))
    print("First payment:", payments[0])
    print("Last payment:", payments[-1])