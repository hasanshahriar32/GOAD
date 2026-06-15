# Post-GOAD Installation Actions & Progress Log

This document details the exact actions taken to interface with GOAD, resolve bugs, and successfully construct the graph machine learning tensors after the GOAD virtual environment was successfully built.

---

## 📋 Step-by-Step Actions Taken

### 1. VM Verification
- Verified that all 5 virtual machines (`GOAD-DC01`, `GOAD-DC02`, `GOAD-DC03`, `GOAD-SRV02`, `GOAD-SRV03`) were fully booted and active using the Vagrant `libvirt` provider on Linux.

### 2. Network Interface Mapping Discovery
- **Discovery**: We found that although the private network interface `192.168.56.10` responded to ICMP pings, all Active Directory services (including DNS on port 53) were listening exclusively on the libvirt management network interface IP `192.168.121.69`.
- **Resolution**: Configured all subsequent querying tools to point to the management network IPs (`192.168.121.x`) instead of the private IPs.

### 3. Upgrading & Patching `ldap3` in the virtual environment
- **Problem**: Running `bloodhound-python` threw a type mismatch crash:
  `TypeError: unsupported operand type(s) for -: 'bytes' and 'datetime.datetime'`
  inside the `ldap3` library's AD timestamp formatter.
- **Fix**: 
  1. Upgraded the `ldap3` dependency to `2.9.1`.
  2. Patched the file `ldap3/protocol/formatters/formatters.py` at line 352 to gracefully return `timedelta.max` if the Active Directory timestamp conversion fails:
     ```python
     t1 = format_ad_timestamp(raw_value)
     t0 = format_ad_timestamp(0)
     if isinstance(t1, bytes) or isinstance(t0, bytes):
         return timedelta.max
     return t1 - t0
     ```

### 4. Active Directory Data Collection via BloodHound
- **Action**: Ran `bloodhound-python` with the global Vagrant administrator credentials (`vagrant` / `vagrant`) to query the running domain controller `192.168.121.69`.
- **Result**: Successfully collected the AD domain graph topology and exported the node/edge JSON files (`*_users.json`, `*_computers.json`, `*_domains.json`, etc.) directly into `Thesis_Data/`.

### 5. Incorporating the Vulnerability Template Definition
- **Action**: Located the ADCS ESC13 vulnerability configuration (`ESC13.json`) within the Ansible directories and copied it to the location expected by the tensor builder:
  ```bash
  cp ansible/roles/adcs_templates/files/ESC13.json ad/GOAD/data/ESC13.json
  ```

### 6. Script Repair & Tensor Generation
- **Problem**: Running `build_tensors.py` threw a `KeyError: 'cn'` because the template configuration did not define a `cn` (Common Name) attribute.
- **Fix**: Patched `build_tensors.py` to retrieve `displayName` instead of `cn` from `ESC13.json`.
- **Verification**: Executed the script using the virtual environment's python. It loaded the 16 users from your BloodHound output and built the PyTorch Geometric `HeteroData` graph representation successfully.
