"""Physical certificate histories projected into incomplete audit records.

Truth comes from the latent certificate selected by the simulator, not from
running the detector's matching predicate. This remains synthetic evidence.
"""

from dataclasses import dataclass, field, replace
import hashlib
import random

from .engine import Observation, TimeRange, MutationWindow


FAMILIES = (
    "clean", "issuer_collision", "conflicting_fields", "reused_skid",
    "missing_bridge", "late_bridge", "clock_overlap", "failed_auth",
    "preceding_auth", "long_delay", "unrelated_template", "boundary_overlap",
    "conflicting_bridge", "missing_issuer", "request_namespace_collision",
    "missing_competitor", "outside_model_forgery", "randomized_mix",
)


@dataclass(frozen=True)
class Case:
    case_id: str
    seed: int
    family: str
    records: tuple[Observation, ...]
    windows: tuple[MutationWindow, ...]
    auth_id: str
    truth_issuance_id: str | None
    truth_exposure: bool
    assumption_violation: bool = False
    latent_truth: dict = field(default_factory=dict)


def generate_case(seed: int, family: str, index: int) -> Case:
    if family not in FAMILIES:
        raise ValueError(family)
    if family == "randomized_mix":
        return generate_random_case(seed, index)
    rng = random.Random(f"lineage-v1:{seed}:{family}:{index}")
    prefix = f"s{seed}:{family}:{index}"

    def digest(label):
        return hashlib.sha256(f"{prefix}:{label}:{rng.getrandbits(128)}".encode()).hexdigest()[:40]

    issuer = f"issuer-{rng.randrange(1, 5)}"
    other_issuer = issuer + "-other"
    serial = f"{rng.randrange(1, 1 << 80):x}"
    fingerprint = digest("physical-certificate")
    public_key_id = digest("public-key")
    physical_issue_time = rng.uniform(100, 1000)
    physical_auth_time = physical_issue_time + rng.uniform(5, 60)
    physical_window_start = physical_issue_time - 3
    physical_window_end = physical_issue_time + 3
    template = f"template-{rng.randrange(3)}"
    principal = f"user-{rng.randrange(1, 500)}@domain.test"
    target = principal if rng.random() < 0.5 else "administrator@domain.test"
    issuance = Observation(prefix + ":issuance", "issuance", TimeRange.around(physical_issue_time),
                          issuer, "7", serial, fingerprint, public_key_id, template, principal)
    auth = Observation(prefix + ":auth", "authentication", TimeRange.around(physical_auth_time),
                       issuer=issuer, serial=serial, thumbprint=fingerprint, skid=public_key_id, principal=target)
    records = [issuance]
    truth = issuance.record_id
    truth_exposure = True
    violation = False

    if family == "issuer_collision":
        # RFC 5280 uniqueness is per issuer, not global.
        records.insert(0, replace(issuance, record_id=prefix + ":other", issuer=other_issuer,
                                  thumbprint=digest("other-cert"), skid=digest("other-key")))
        auth = replace(auth, thumbprint="", skid="")
    elif family == "conflicting_fields":
        # Audit corruption: one field conflicts although another still matches.
        auth = replace(auth, serial=f"{int(serial, 16) + 1:x}")
    elif family == "reused_skid":
        # Two physical certificates legitimately reuse one public key.
        records.append(replace(issuance, record_id=prefix + ":renewal", request_id="8",
                               serial=f"{int(serial, 16) + 1:x}", thumbprint=digest("renewal")))
        auth = replace(auth, serial="", thumbprint="")
    elif family in ("missing_bridge", "late_bridge", "request_namespace_collision"):
        records[0] = replace(issuance, serial="", thumbprint="", skid="")
        if family != "missing_bridge":
            records.append(Observation(prefix + ":bridge", "bridge", TimeRange.around(physical_auth_time + 120),
                                       issuer, "7", serial, fingerprint, public_key_id, template, principal))
        if family == "request_namespace_collision":
            records.insert(1, Observation(prefix + ":other-bridge", "bridge", TimeRange.around(0),
                                          other_issuer, "7", "ff", digest("other"), digest("other-key")))
    elif family == "clock_overlap":
        physical_auth_time = physical_issue_time + 0.2
        records[0] = replace(issuance, time=TimeRange.around(physical_issue_time + 0.5, 1))
        auth = replace(auth, time=TimeRange.around(physical_auth_time - 0.5, 1))
    elif family == "failed_auth":
        auth = replace(auth, success=False)
        truth = None
        truth_exposure = False
    elif family == "preceding_auth":
        # The observed issuance cannot explain an earlier use. The actual
        # issuance is outside the captured history, so no observed true edge.
        auth = replace(auth, time=TimeRange.around(physical_issue_time - 100))
        truth = None
        truth_exposure = False
    elif family == "long_delay":
        auth = replace(auth, time=TimeRange.around(physical_issue_time + rng.uniform(86400, 864000)))
    elif family == "unrelated_template":
        template += "-other"
        truth_exposure = False
    elif family == "boundary_overlap":
        # Actual issuance precedes the change. A biased point timestamp puts
        # it inside; the supplied interval still contains the actual time.
        physical_window_start = physical_issue_time + 0.2
        physical_window_end = physical_issue_time + 5
        records[0] = replace(issuance, time=TimeRange.around(physical_issue_time + 0.5, 1))
        truth_exposure = False
    elif family == "conflicting_bridge":
        records.append(Observation(prefix + ":bad-bridge", "bridge", TimeRange.around(physical_auth_time + 10),
                                   issuer, "7", serial, digest("conflicting-export"), public_key_id))
    elif family == "missing_issuer":
        auth = replace(auth, issuer="", thumbprint="", skid="")
        records.append(replace(issuance, record_id=prefix + ":other", issuer=other_issuer,
                               thumbprint=digest("other-cert"), skid=digest("other-key")))
    elif family == "missing_competitor":
        records.append(replace(issuance, record_id=prefix + ":unidentified", request_id="8",
                               serial="", thumbprint="", skid="", time=TimeRange.around(physical_issue_time - 2)))
    elif family == "outside_model_forgery":
        # Explicit negative control: trusted-record assumptions are violated.
        # An internally consistent forged record replaces the true issuance.
        records[0] = replace(issuance, record_id=prefix + ":forged")
        truth = None
        truth_exposure = False
        violation = True

    window = MutationWindow(prefix + ":window", template,
                            TimeRange.around(physical_window_start), TimeRange.around(physical_window_end),
                            (prefix + ":open", prefix + ":close"))
    # Arrival order differs from event time; a late bridge always arrives last.
    records.append(auth)
    rng.shuffle(records)
    if family in ("late_bridge", "request_namespace_collision"):
        records.sort(key=lambda r: r.kind == "bridge")
    return Case(prefix, seed, family, tuple(records), (window,), auth.record_id, truth, truth_exposure, violation)


def generate_random_case(seed: int, index: int) -> Case:
    """Variable-size histories with independently sampled logging omissions.

    Serials remain unique inside each issuing CA; keys can be reused. All true
    physical event times are retained only by the simulator, while the detector
    receives jittered intervals containing them. Mixture rates are experimental
    choices, not estimates of real ADCS workloads.
    """
    rng = random.Random(f"random-lineage-v1:{seed}:{index}")
    prefix = f"s{seed}:randomized_mix:{index}"
    count = rng.randint(2, 9)
    target_index = rng.randrange(count)
    physical = []
    records = []
    for j in range(count):
        issuer = f"ca-{j // 3}"
        serial = f"{j % 3 + 1:x}"
        fingerprint = hashlib.sha256(f"{prefix}:cert:{j}".encode()).hexdigest()[:40]
        skid = hashlib.sha256(f"{prefix}:reused-key:{j % 2}".encode()).hexdigest()[:40]
        stamp = rng.uniform(100, 160)
        template = f"template-{rng.randrange(3)}"
        principal = f"user-{j}@domain.test"
        physical.append((issuer, serial, fingerprint, skid, stamp, template, principal))
        error = rng.choice([0.0, 0.5, 2.0, 5.0])
        reported = stamp + rng.uniform(-error, error)
        issue = Observation(f"{prefix}:issuance:{j}", "issuance", TimeRange.around(reported, error),
                            issuer, str(j + 1), serial if rng.random() > 0.25 else "",
                            fingerprint if rng.random() > 0.4 else "", skid if rng.random() > 0.3 else "",
                            template, principal)
        records.append(issue)
        if rng.random() < 0.65:
            bridge_fingerprint = fingerprint
            if rng.random() < 0.05:
                bridge_fingerprint = hashlib.sha256(f"{prefix}:bad-export:{j}".encode()).hexdigest()[:40]
            records.append(Observation(f"{prefix}:bridge:{j}", "bridge", TimeRange(0, 0),
                                       issuer, str(j + 1), serial, bridge_fingerprint, skid, template, principal))
    issuer, serial, fingerprint, skid, actual_issue, template, principal = physical[target_index]
    actual_auth = actual_issue + rng.choice([rng.uniform(0.1, 3), rng.uniform(5, 60), rng.uniform(86400, 172800)])
    auth_error = rng.choice([0.0, 0.5, 2.0, 5.0])
    auth = Observation(prefix + ":auth", "authentication",
                       TimeRange.around(actual_auth + rng.uniform(-auth_error, auth_error), auth_error),
                       issuer=issuer if rng.random() > 0.15 else "",
                       serial=serial if rng.random() > 0.2 else "",
                       thumbprint=fingerprint if rng.random() > 0.4 else "",
                       skid=skid if rng.random() > 0.5 else "", principal=principal,
                       success=rng.random() > 0.1)
    records.append(auth)
    window_template = template if rng.random() > 0.2 else template + "-other"
    window_start = actual_issue + rng.uniform(-3, 3)
    window_end = window_start + rng.uniform(0.2, 6)
    window_error = rng.choice([0.0, 0.5, 1.0])
    window = MutationWindow(prefix + ":window", window_template,
                            TimeRange.around(window_start, window_error), TimeRange.around(window_end, window_error),
                            (prefix + ":open", prefix + ":close"))
    truth_id = f"{prefix}:issuance:{target_index}" if auth.success else None
    truth_exposure = bool(auth.success and window_template == template and window_start <= actual_issue <= window_end)
    rng.shuffle(records)
    latent = {
        "physical_certificates": [
            {"record_id": f"{prefix}:issuance:{j}", "issuer": c[0], "serial": c[1], "thumbprint": c[2],
             "skid": c[3], "issued_at": c[4], "template": c[5], "principal": c[6]}
            for j, c in enumerate(physical)
        ],
        "selected_issuance_id": f"{prefix}:issuance:{target_index}",
        "authenticated_at": actual_auth, "authentication_succeeded": auth.success,
        "mutation_window": {"template": window_template, "opened_at": window_start, "closed_at": window_end},
    }
    return Case(prefix, seed, "randomized_mix", tuple(records), (window,), auth.record_id, truth_id, truth_exposure,
                latent_truth=latent)
