# Live GOAD evidence

These scripts collect actual Windows/ADCS configuration and run actual Certipy. They are separate from synthetic benchmark labels.

`collect_adcs.ps1` reads templates, policy links, CA publication, DACLs, users, groups and OS build using Windows AD cmdlets. `collect_live.py` transports it over WinRM (compressed in memory to fit the Windows command-line limit) and saves the raw output plus hashes. It does not resolve all effective permissions or execute enrollment/authentication.

`run_certipy.py` executes a versioned `find` command, saves raw JSON/text/logs, records duration and a password-redacted command. Set `GOAD_COLLECTION_PASSWORD` securely in the shell; it is not written into manifests. `--dc-only` omits runtime CA collection and must be labeled accordingly. No detection accuracy should be computed without independent labels.

The first ESSOS collection on 2026-10-14 returned 0 templates, 0 enrollment-service CAs, 1 OID object, 56 groups and 13 users. Actual Certipy 5.0.4 returned the same empty ADCS inventory. Windows reported the ADCS CA role absent on BRAAVOS. These are observations of this lab at collection time, not a claim about every GOAD installation. Baseline files are retained in `data/live_adcs_2026-10-14/essos`. Any subsequent provisioned cases must be labeled as controlled lab experiments, not naturally occurring enterprise data.

Certipy 5.0.4 is installed in an isolated environment at `/tmp/certgraph-certipy5` (Python 3.14.7); the research environment retains Certipy 4.8.2. To reconstruct the isolated tool environment, use `uv venv --python /usr/bin/python3 <path>` then `uv pip install --python <path>/bin/python certipy-ad==5.0.4`. Version 5.0.4 requires Python >=3.12. Pin the complete dependency set from the saved installation record when reproducing exact behavior.
