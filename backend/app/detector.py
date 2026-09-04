import random

from decimal import Decimal
from .data.simulation import generate_dataset
from .data.generator import PROVIDERS
from .models.payment import FailureCause, PaymentStatus
from .razorpay_client import fetch_payment_events

WINDOW_FAILURE_THRESHOLD = 0.20
RECOVERY_RATE = 0.60

def calculate_failure_rate(payments, provider):
    total = 0
    failed = 0

    for payment in payments:
        if payment.provider == provider:
            total += 1

            if payment.status == PaymentStatus.FAILED:
                failed += 1

    if total == 0:
        return 0

    return failed/total

def calculate_failed_amount(payments, provider):
    failed_amount = Decimal("0")

    for payment in payments:
        if payment.provider == provider:
            if payment.status == PaymentStatus.FAILED:
                failed_amount += payment.amount
    
    return failed_amount

def get_time_window(payments, start_minute, end_minute):

    window = []

    for payment in payments:
        if start_minute <= payment.timestamp.minute <= end_minute:
            window.append(payment)

    return window

def get_provider_payments(payments, provider):
    provider_payments = []

    for payment in payments:
        if payment.provider == provider:
            provider_payments.append(payment)

    return provider_payments

def calculate_failed_amount_in_window(payments, provider, start_minute, end_minute):
    window = get_time_window(
        payments,
        start_minute,
        end_minute
    )

    return calculate_failed_amount(
        window,
        provider
    )

def is_recoverable(payment):
    if payment.status != PaymentStatus.FAILED:
        return False

    if payment.failure_cause in[
        FailureCause.PAYMENT_TIMEOUT ,
        FailureCause.PROVIDER_ERROR
    ]:
        return True

    return False

def get_recovery_action(payment):
    if not is_recoverable(payment):
        return "NO_ACTION"

    if payment.failure_cause == FailureCause.PAYMENT_TIMEOUT:
        return "RETRY"

    if payment.failure_cause == FailureCause.PROVIDER_ERROR:
        return "ROUTE_TO_ALTERNATIVE_PROVIDER"

    return "NO_ACTION"

def calculate_recoverable_amount(payments, provider, start_minute, end_minute):
    recoverable_amount = Decimal("0")
    recoverable_count = 0

    window = get_time_window(
        payments,
        start_minute,
        end_minute
    )

    for payment in window:
        if payment.provider == provider:
            if is_recoverable(payment):
                recoverable_amount += payment.amount
                recoverable_count += 1
    return recoverable_amount, recoverable_count


def get_recovery_recommendations(payments, provider, start_minute, end_minute):
    recommendations = []

    window = get_time_window(
        payments,
        start_minute,
        end_minute
    )

    for payment in window:
        if payment.provider == provider:
            action = get_recovery_action(payment)

            if action != "NO_ACTION":
                recommendations.append((payment, action))

    return recommendations

def execute_recovery(payment, action):
    if action == "RETRY":
        if random.random() < 0.70:
            return "SUCCESS"
        return "FAILED"

    if action == "ROUTE_TO_ALTERNATIVE_PROVIDER":
        if random.random() < 0.80:
            return "SUCCESS"
        return "FAILED"

    return "FAILED"

def run_analysis(payments=None):
    random.seed(42)
    audit_log = []
    if payments is None:
        payments = generate_dataset()
    providers = sorted(set(payment.provider for payment in payments))

    normal_payments = []
    current_payments = []

    for payment in payments:
        if payment.timestamp.minute < 30:
            normal_payments.append(payment)
        else:
            current_payments.append(payment)

    most_degraded_provider = None
    largest_change = 0

    for provider in providers:
        normal_failure_rate = calculate_failure_rate(
            normal_payments,
            provider
        )

        current_failure_rate = calculate_failure_rate(
            current_payments,
            provider
        )

        failure_rate_change = current_failure_rate - normal_failure_rate

        print(
            f"{provider}: "
            f"normal = {normal_failure_rate: .2%}, "
            f"current = {current_failure_rate: .2%}, "
            f"change = {failure_rate_change: }"
        )

        if failure_rate_change > largest_change:
            largest_change = failure_rate_change
            most_degraded_provider = provider
        
    target_provider = most_degraded_provider

    print()
    print("Most degraded provider:", most_degraded_provider)
    print(f"Largest failure-rate increase: {largest_change: .2%}")

    DEGRADATION_THRESHOLD = 0.20

    if largest_change >= DEGRADATION_THRESHOLD:
        print("Provider is degraded:", most_degraded_provider)
    else:
        print("No significant degradation detected")

    consecutive_bad_windows = {}

    for provider in providers:
        consecutive_bad_windows[provider] = 0

    degraded_failed_amount = Decimal("0")

    for start_minute in range(0, 60, 5):
        end_minute = start_minute + 4

        window = get_time_window(
            payments,
            start_minute,
            end_minute
        )

        for provider in providers:
            failure_rate = calculate_failure_rate(
                window,
                provider
            )

            if failure_rate >= WINDOW_FAILURE_THRESHOLD:
                if provider == target_provider:
                    degraded_failed_amount += calculate_failed_amount(
                        window,
                        provider
                    )

            print(
                f"{provider} "
                f"{start_minute:02d}-{end_minute:02d}: "
                f"{failure_rate:.2%}"
            )

            if failure_rate >= WINDOW_FAILURE_THRESHOLD:
                consecutive_bad_windows[provider] += 1
            else:
                consecutive_bad_windows[provider] = 0

    for provider in providers:
        if consecutive_bad_windows[provider] >= 3:
            print(provider, "has persistent degradation")

    failed_amount = calculate_failed_amount(
        payments,
        target_provider
    )

    print(target_provider, "failed amount:", failed_amount)

    provider_payments = get_provider_payments(
        payments,
        target_provider
    )

    print(target_provider, "payments:", len(provider_payments))

    failed_amount = calculate_failed_amount_in_window(
        payments,
        target_provider,
        30,
        34
    )

    print(
    target_provider,
    "failed amount (30-34):",
    failed_amount
    )

    print(
    target_provider,
    "degraded-period failed amount:",
    degraded_failed_amount
    )

    recoverable_revenue = degraded_failed_amount * Decimal(str(RECOVERY_RATE))

    print(
    target_provider,
    "estimated recoverable amount:",
    recoverable_revenue
    )

    recoverable_amount, recoverable_count = calculate_recoverable_amount(
        payments,
        target_provider,
        30,
        59
    )

    print(
    target_provider,
    "recoverable payments:",
    recoverable_count
    )

    recommendations = get_recovery_recommendations(
        payments,
        target_provider,
        30,
        59
    )

    retry_count = 0
    reroute_count = 0

    for payment, action in recommendations:
        if action == "RETRY":
            retry_count += 1

        if action == "ROUTE_TO_ALTERNATIVE_PROVIDER":
            reroute_count += 1

    print("Recovery recommendations:", len(recommendations))
    print("Recommended retries:", retry_count)
    print("Recommended reroutes:", reroute_count)

    successful_recoveries = 0
    failed_recoveries = 0
    escalated_recoveries = 0
    recovered_amount = Decimal("0")

    for payment, action in recommendations:
        result = execute_recovery(payment, action)
        audit_log.append({
            "payment_id": payment.payment_id,
            "provider": payment.provider,
            "action": action,
            "result": result,
            "amount": payment.amount,
        })

        if result == "SUCCESS":
            successful_recoveries += 1
            recovered_amount += payment.amount
        else:
            failed_recoveries += 1
            escalated_recoveries += 1

    print("Successful recoveries:", successful_recoveries)
    print("Failed recoveries:", failed_recoveries)
    print("Escalated recoveries:", escalated_recoveries)
    print("Recovered amount:", recovered_amount)
    print("Audit trail entries:", len(audit_log))
    if audit_log:
        print("Sample audit entry:", audit_log[0])

    return {
    "detection": {
        "provider": most_degraded_provider,
        "failure_rate_increase": largest_change,
        "failure_rate_increase_percent": round(largest_change * 100, 2),
    },

    "revenue": {
        "degraded_failed_amount": degraded_failed_amount,
        "estimated_recoverable_amount": round(recoverable_revenue),
        "recoverable_amount": recoverable_amount,
    },

    "recovery": {
        "recoverable_payments": recoverable_count,
        "recovery_recommendations": len(recommendations),
        "recommended_retries": retry_count,
        "recommended_reroutes": reroute_count,
    },

    "execution": {
        "successful_recoveries": successful_recoveries,
        "failed_recoveries": failed_recoveries,
        "escalated_recoveries": escalated_recoveries,
        "recovered_amount": recovered_amount,
    },

    "audit": {
        "audit_trail_entries": len(audit_log),
    },
}

def run_razorpay_analysis():
    payments = fetch_payment_events()

    return {
        "payment_count": len(payments),
        "payments": payments,
    }