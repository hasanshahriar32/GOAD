"""Read-only Windows inventory and measured host/guest clock-offset brackets."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import time

import requests
import winrm


INVENTORY = r"""
$ErrorActionPreference = 'Stop'
$os = Get-CimInstance Win32_OperatingSystem
$svc = Get-Service CertSvc -ErrorAction SilentlyContinue
$active = Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration' -ErrorAction SilentlyContinue
$network = Get-NetIPAddress -AddressFamily IPv4 | Select-Object InterfaceAlias,IPAddress,PrefixLength
$out = [ordered]@{
  computer=$env:COMPUTERNAME; utc=(Get-Date).ToUniversalTime().ToString('o');
  os=$os.Caption; version=$os.Version; build=$os.BuildNumber;
  ca_service=if ($svc) {$svc.Status.ToString()} else {'absent'};
  ca_name=if ($active) {$active.Active} else {$null};
  network=@($network)
}
if (Get-Module -ListAvailable ActiveDirectory) {
  try {
  Import-Module ActiveDirectory
  $root = Get-ADRootDSE
  $base = 'CN=Certificate Templates,CN=Public Key Services,CN=Services,' + $root.configurationNamingContext
  $out.templates = @(Get-ADObject -SearchBase $base -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties msPKI-Cert-Template-OID,msPKI-Certificate-Name-Flag,msPKI-Enrollment-Flag,pKIExtendedKeyUsage | Select-Object Name,DistinguishedName,msPKI-Cert-Template-OID,msPKI-Certificate-Name-Flag,msPKI-Enrollment-Flag,pKIExtendedKeyUsage)
  } catch { $out.ad_inventory_error = $_.Exception.Message }
}
$out | ConvertTo-Json -Depth 7 -Compress
"""


def collect(output: Path):
    output.mkdir(parents=True, exist_ok=False)
    username = os.environ.get("GOAD_LAB_USER", r"ESSOS\vagrant")
    password = os.environ.get("GOAD_LAB_PASSWORD", "vagrant")
    result = {"scope": "Read-only inventory in new writable overlays of original read-only disk images", "hosts": {}}
    for name, port, variable in (("dc03", 55985, "GOAD_DC_URL"), ("srv03", 56985, "GOAD_CA_URL")):
        url = os.environ.get(variable, f"http://127.0.0.1:{port}/wsman")
        host_user = os.environ.get("GOAD_DC_USER" if name == "dc03" else "GOAD_CA_USER", username)
        host_password = os.environ.get("GOAD_DC_PASSWORD" if name == "dc03" else "GOAD_CA_PASSWORD", password)
        try:
            requests.get(url, timeout=3)
            session = winrm.Session(url, auth=(host_user, host_password), transport="ntlm", read_timeout_sec=35, operation_timeout_sec=25)
            remote = session.run_ps(INVENTORY)
            stdout = remote.std_out.decode("utf-8-sig", errors="replace")
            stderr = remote.std_err.decode("utf-8-sig", errors="replace")
            raw = {"returncode": remote.status_code, "stdout": stdout, "stderr": stderr}
            (output / f"{name}_inventory_raw.json").write_text(json.dumps(raw, indent=2) + "\n")
            host = {"inventory_returncode": remote.status_code}
            if remote.status_code == 0:
                host["inventory"] = json.loads(stdout)
            samples = []
            for _ in range(3):
                started = time.time()
                stamp = session.run_ps("[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()")
                finished = time.time()
                if stamp.status_code != 0:
                    raise RuntimeError("Remote clock sample failed")
                remote_seconds = int(stamp.std_out.strip()) / 1000
                samples.append({"local_before": started, "local_after": finished, "remote_utc": remote_seconds,
                                "offset_lower_seconds": remote_seconds - finished,
                                "offset_upper_seconds": remote_seconds - started})
            host["clock_samples"] = samples
            host["clock_offset_intersection_seconds"] = [max(s["offset_lower_seconds"] for s in samples),
                                                          min(s["offset_upper_seconds"] for s in samples)]
            host["clock_assumptions"] = "Constant guest-host offset during each request, trusted clocks, and timestamp evaluation inside the measured request/response bracket. Not an NTP drift guarantee."
            result["hosts"][name] = host
        except Exception as exc:
            result["hosts"][name] = {"error_type": type(exc).__name__, "error": str(exc)}
    result["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (output / "preflight.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    collect(parser.parse_args().output)
