"""Independent certificate/XML/count/arithmetic checks for the collection pilot."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET

from cryptography import x509
from cryptography.hazmat.primitives import hashes


def hexid(value):return ''.join((value or '').split()).replace(':','').lower().removeprefix('0x').lstrip('0') or '0'


def run(directory,output):
    if output.exists():raise FileExistsError(output)
    manifest=json.loads((directory/'manifest.json').read_text())
    for name,digest in manifest.items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=digest:raise ValueError('Artifact hash differs')
    raw=(directory/'seed_certificate/issued_certificate.cer').read_bytes()
    try:cert=x509.load_der_x509_certificate(raw)
    except ValueError:cert=x509.load_pem_x509_certificate(raw)
    serial=hexid(format(cert.serial_number,'x'));thumb=hexid(cert.fingerprint(hashes.SHA1()).hex())
    summary=json.loads((directory/'results.json').read_text());checked=0;auths=0
    inventory=json.loads(json.loads(Path(json.loads((directory/'inventory_origin.json').read_text())['path']).read_text())['stdout'])
    sid=next(u['sid'] for u in inventory['users'] if u['SamAccountName']=='q1.reader')
    for row in summary['arms']:
        arm=directory/row['id'];latencies=[json.loads(p.read_text())['elapsed_ns']/1e9 for p in sorted(arm.glob('auth_*.json'))]
        if latencies!=row['authentication_process_envelopes_seconds'] or statistics.median(latencies)!=row['median_authentication_seconds']:raise AssertionError('Latency arithmetic differs')
        records=[]
        for event in ET.parse(arm/'ground_truth_events.xml').getroot():
            code=next((c.text for c in event.iter() if c.tag.rsplit('}',1)[-1]=='EventID'),None)
            fields={c.attrib['Name']:c.text or '' for c in event.iter() if c.tag.rsplit('}',1)[-1]=='Data' and 'Name' in c.attrib}
            if (code=='4768' and hexid(fields.get('CertSerialNumber'))==serial and hexid(fields.get('CertThumbprint'))==thumb and
                    fields.get('Status') in ('0','0x0','0x00000000') and fields.get('TargetSid')==sid and
                    fields.get('TargetUserName','').casefold()=='q1.reader' and fields.get('TargetDomainName','').casefold()==inventory['dns_root'] and
                    fields.get('CertIssuerName','').casefold()==inventory['ca_name'].casefold() and fields.get('PreAuthType') in ('15','16','17')):
                rid=next(c.text for c in event.iter() if c.tag.rsplit('}',1)[-1]=='EventRecordID');records.append(rid)
        if len(records)!=row['expected_authentications'] or len(set(records))!=len(records):raise AssertionError('Incomplete or duplicated exact-certificate outcomes')
        if row['raw_successful_exact_certificate_kdc_records']!=len(records):raise AssertionError('Reported KDC count differs')
        samples=json.loads((arm/'rss_samples.json').read_text())
        if max(s['rss_kib'] for s in samples)!=row['collector_rss_peak_kib']:raise AssertionError('RSS arithmetic differs')
        polls=json.loads((arm/'polls.json').read_text())
        if len(polls)!=row['polls']:raise AssertionError('Poll count differs')
        if sum(p['new_security_events'] for p in polls)!=row['new_security_events_exported']:raise AssertionError('Event count differs')
        if row['arm']=='idle' and polls:raise AssertionError('Idle arm has periodic collection')
        checked+=1;auths+=len(records)
    for pair in summary['paired']:
        arms={r['arm']:r for r in summary['arms'] if r['pair']==pair['pair']}
        difference=arms['polling']['median_authentication_seconds']-arms['idle']['median_authentication_seconds']
        if difference!=pair['median_envelope_difference_seconds']:raise AssertionError('Paired arithmetic differs')
    report={'status':'passed','paired_arms_checked':checked,'successful_exact_certificate_authentications_checked':auths,
        'scope':'Checks saved process envelopes, certificate-bound raw KDC outcomes, RSS/event counts and paired arithmetic. Does not establish production interference or reproduce wall-clock timing.',
        'input_manifest_sha256':hashlib.sha256((directory/'manifest.json').read_bytes()).hexdigest(),
        'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');output.with_suffix('.source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('output',type=Path);a=p.parse_args();run(a.directory,a.output)
