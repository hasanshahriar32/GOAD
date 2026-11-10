"""Falsify declared clock/audit-delay assumptions using controlled operations.

The operation must be known to occur inside the host request/response bracket.
Matching a log to that operation and trusting both clocks remain assumptions.
This check diagnoses inconsistency; it does not identify its physical cause.
"""

import math


def audit_operation_bracket(event_timestamp, host_before, host_after,
                            offset_lower, offset_upper, max_audit_delay=None):
    values = (event_timestamp, host_before, host_after, offset_lower, offset_upper)
    if not all(math.isfinite(v) for v in values) or host_before > host_after or offset_lower > offset_upper:
        raise ValueError("Invalid finite time/offset bounds")
    if max_audit_delay is not None and (not math.isfinite(max_audit_delay) or max_audit_delay < 0):
        raise ValueError("Audit delay must be nonnegative or unknown")
    earliest_log = event_timestamp - offset_upper
    latest_log = event_timestamp - offset_lower
    # There must exist operation in [before, after] and log >= operation,
    # with log-operation <= delay when a maximum delay is supplied.
    not_before_operation = latest_log >= host_before
    not_too_late = max_audit_delay is None or earliest_log <= host_after + max_audit_delay
    return {
        "compatible": not_before_operation and not_too_late,
        "maximum_audit_delay_seconds": max_audit_delay,
        "corrected_log_time_range": [earliest_log, latest_log],
        "host_operation_bracket": [host_before, host_after],
        "log_must_precede_command_under_declared_clock_bound": not not_before_operation,
        "inferred_offset_range_if_audit_is_immediate": [event_timestamp - host_after, event_timestamp - host_before],
        "interpretation": "Incompatibility falsifies at least one clock, event-association, or synchronous-operation assumption; it does not by itself prove clock drift.",
    }
