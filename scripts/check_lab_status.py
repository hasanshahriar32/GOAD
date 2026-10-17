#!/usr/bin/env python3
"""
check_lab_status.py — Service Readiness Prober for GOAD Lab on Connected Disk
"""

import socket
import time

TARGETS = {
    "GOAD-DC03 (LDAP)": ("127.0.0.1", 10389),
    "GOAD-DC03 (SMB)": ("127.0.0.1", 10445),
    "GOAD-DC03 (Kerberos)": ("127.0.0.1", 10088),
    "GOAD-DC03 (WinRM)": ("127.0.0.1", 55985),
    "GOAD-SRV03 (HTTP Web Enrollment)": ("127.0.0.1", 8080),
    "GOAD-SRV03 (WinRM)": ("127.0.0.1", 56985),
}

def probe(host, port, timeout=1.5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        res = s.connect_ex((host, port))
        if res == 0:
            if port == 10445:
                # SMB probe
                s.send(b'\x00\x00\x00\x45\xff\x53\x4d\x42\x72\x00\x00\x00\x00\x08\x01\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x22\x00\x02\x4e\x54\x20\x4c\x4d\x20\x30\x2e\x31\x32\x00\x02\x53\x4d\x42\x20\x32\x2e\x30\x30\x32\x00\x02\x53\x4d\x42\x20\x32\x2e\x3f\x3f\x3f\x00')
                resp = s.recv(128)
                return len(resp) > 0
            elif port == 10389:
                # LDAP probe
                req = bytes.fromhex('3025020101632004000a01000a0100020100020100010100870b6f626a656374436c6173733000')
                s.send(req)
                resp = s.recv(128)
                return len(resp) > 0
            elif port == 8080:
                s.send(b"GET /certsrv/ HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n")
                resp = s.recv(64)
                return len(resp) > 0
            return True
        return False
    except Exception:
        return False
    finally:
        s.close()

def main():
    print("="*65)
    print(" GOAD CONNECTED DISK SERVICE READINESS MONITOR")
    print("="*65)
    for name, (host, port) in TARGETS.items():
        ok = probe(host, port)
        status = "READY (ONLINE)" if ok else "BOOTING / STARTING UP..."
        print(f"{name:<35} [{host}:{port:<5}] -> {status}")
    print("="*65)

if __name__ == "__main__":
    main()
