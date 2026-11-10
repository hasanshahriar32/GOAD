"""Executed local correlators; these do not impersonate commercial tools."""

from dataclasses import replace

from .engine import Observation, text


def enriched_issuances(records: tuple[Observation, ...]) -> list[Observation]:
    result = []
    for issue in records:
        if issue.kind != "issuance":
            continue
        values = {name: getattr(issue, name) for name in ("serial", "thumbprint", "skid", "template")}
        for bridge in records:
            if bridge.kind == "bridge" and text(bridge.issuer) == text(issue.issuer) and bridge.request_id == issue.request_id:
                for name in values:
                    if not values[name]:
                        values[name] = getattr(bridge, name)
        result.append(replace(issue, **values))
    return result


def predict(records, method):
    auth = next(r for r in records if r.kind == "authentication")
    identities = auth.identity()
    output = []
    for issue in enriched_issuances(records):
        fields = issue.identity()
        shared = {k for k in ("serial", "thumbprint", "skid") if identities[k] and identities[k] == fields[k]}
        if method == "legacy_or_keys":
            matched = bool(shared)
        elif method == "issuer_serial":
            matched = bool(identities["issuer"] and identities["issuer"] == fields["issuer"]
                           and identities["serial"] and identities["serial"] == fields["serial"])
        elif method in ("conjunctive_point", "conjunctive_window300"):
            strong = "thumbprint" in shared or ("serial" in shared and identities["issuer"] and fields["issuer"])
            conflicts = any(identities[k] and fields[k] and identities[k] != fields[k] for k in fields)
            issue_mid = (issue.time.lower + issue.time.upper) / 2
            auth_mid = (auth.time.lower + auth.time.upper) / 2
            matched = (auth.success is True and auth.preauth_type in (15, 16, 17) and bool(strong)
                       and not conflicts and issue_mid <= auth_mid)
            if method == "conjunctive_window300":
                matched &= auth_mid - issue_mid <= 300
        else:
            raise ValueError(method)
        if matched:
            output.append(issue.record_id)
    return sorted(set(output))
