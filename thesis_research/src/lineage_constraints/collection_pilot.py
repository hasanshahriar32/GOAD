"""Paired isolated-lab collection/inference and authentication-envelope pilot.

The unit is an arm in one VM, not a production domain or a packet-level KDC
latency measurement. The idle arm has no periodic collector; both arms have a
postmeasurement ground-truth export. Private credentials/keys are not retained.
"""
import argparse
from collections import Counter
import csv
from dataclasses import replace
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import random
import statistics
import threading
import time
import xml.etree.ElementTree as ET

from asn1crypto.core import UTF8String
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID,ObjectIdentifier

from .adjudicate_policy_matrix import events,hexkey
from .engine import LineageEngine,Observation,TimeRange
from .goad import read_trace
from .transfer_workload import Runner,request_trial,authenticate,manifest,dump,sha,ROOT,DOMAIN,CA,USERS,EVENT_IDS,ORIGINAL
from scripts.capture_trace7_split_actor_delayed_pkinit import get_current_event_record_id,export_events_since


def freeze(path):
    if path.exists():raise FileExistsError(path)
    arms=[]
    for pair in range(3):
        values=['idle','polling'];random.Random(84011+pair).shuffle(values)
        for arm in values:arms.append({'id':f'p{pair+1:02d}_{arm}','pair':pair+1,'arm':arm})
    sources=[Path(__file__),Path(__file__).with_name('transfer_workload.py'),Path(__file__).with_name('engine.py'),Path(__file__).with_name('goad.py'),
        Path(__file__).with_name('independent_policy_2019.py'),Path(__file__).parent/'lab/transfer_2019.py',Path(__file__).with_name('adjudicate_policy_matrix.py'),
        ROOT/'scripts/capture_trace7_split_actor_delayed_pkinit.py']
    dump(path,{'schema':1,'declared_utc':datetime.now(timezone.utc).isoformat(),'arms':arms,'authentications_per_arm':8,
        'auth_start_period_seconds':3,'poll_target_period_seconds':2,'warmup_authentications':2,
        'collection':'Incremental filtered Security export plus full CA export; canonical identity-reference updates; snapshots retained',
        'memory':'Current Python collector process VmRSS from /proc/self/status, excludes Certipy children and Windows VM',
        'latency':'Host process envelope for actual Certipy certificate authentication, including startup/network; not packet-only KDC latency',
        'scope':'Three paired arm orders in one isolated updated Windows2019 forest; exploratory pilot, not production interference certification',
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sources}})


def export_security(runner,boundary,path):
    raw=export_events_since(runner.admin,boundary,EVENT_IDS)
    ET.ElementTree(ET.fromstring('<Events>'+raw+'</Events>')).write(path,encoding='utf-8',xml_declaration=True)


def ca_export(runner,name):
    return runner.ps(runner.admin,name,"certutil.exe -view -restrict 'Disposition=20' -out 'RequestID,RequesterName,SerialNumber,CertificateHash,CertificateTemplate' csv;if($LASTEXITCODE -ne 0){throw 'CA export failed'};exit 0")


def update_reference(engine,path,ca):
    observations,_=read_trace(path,CA)
    for record in observations:engine.add(replace(record,time=TimeRange(0,0)))
    for row in csv.DictReader(io.StringIO(ca['stdout'])):
        request=row.get('Issued Request ID')
        if request:
            record=Observation('bridge:'+CA+':'+request,'bridge',TimeRange(0,0),CA,request,
                row.get('Serial Number',''),row.get('Certificate Hash',''),template=row.get('Certificate Template',''),principal=row.get('Requester Name',''))
            engine.add(record)


def rss_kib():
    for line in Path('/proc/self/status').read_text().splitlines():
        if line.startswith('VmRSS:'):return int(line.split()[1])


def run(protocol_path,inventory_path,output,certipy):
    protocol=json.loads(protocol_path.read_text())
    for name,expected in protocol['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('Frozen source changed: '+name)
    output.mkdir(parents=True,exist_ok=False);dump(output/'protocol.json',protocol)
    sources=output/'sources';sources.mkdir()
    for name in protocol['source_sha256']:(sources/Path(name).name).write_bytes((ROOT/name).read_bytes())
    context=json.loads(json.loads(inventory_path.read_text())['stdout'])
    dump(output/'inventory_origin.json',{'path':str(inventory_path),'sha256':sha(inventory_path)})
    runner=Runner(output,certipy,context=context)
    runner.ps(runner.admin,'00_preflight',"$d=Get-ADDomain;$v=Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion';if($d.DNSRoot -ne '"+DOMAIN+"' -or $v.UBR -ne 9376){throw 'Wrong forest/build'};@{utc=[DateTime]::UtcNow.ToString('o');domain_sid=$d.DomainSID.Value}|ConvertTo-Json -Compress")
    states={t:runner.state('initial_'+t,t) for t in USERS}
    if any(json.loads(s['stdout'])['name_flag']!=ORIGINAL for s in states.values()):raise RuntimeError('Pilot requires restored templates')
    alias={json.loads(s['stdout'])['template_oid']:t for t,s in states.items()}
    user='q1.reader';sid=next(u['sid'] for u in context['users'] if u['SamAccountName']==user)
    selected={k:v for k,v in context.items() if k!='users'};selected.update(enroller_name=user,enroller_sid=sid,template_name='Q1TransferA')
    seed=output/'seed_certificate';seed.mkdir();key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    request=x509.CertificateSigningRequestBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,user)])).add_extension(
        x509.SubjectAlternativeName([x509.OtherName(ObjectIdentifier('1.3.6.1.4.1.311.20.2.3'),UTF8String(user+'@'+DOMAIN).dump())]),False).sign(key,hashes.SHA256()).public_bytes(serialization.Encoding.PEM)
    baseline=get_current_event_record_id(runner.admin)
    trial={'id':'operational_self','block':'operational','template':'Q1TransferA','enroller':user,'target':'self'}
    cert,identity=request_trial(trial,seed,selected,certipy,key,request)
    for i in range(protocol['warmup_authentications']):authenticate(cert,key,certipy,user,seed/f'warmup_{i}.json')
    export_security(runner,baseline,output/'seed_events.xml');seed_ca=ca_export(runner,'seed_ca')
    arms=[]
    for arm in protocol['arms']:
        directory=output/arm['id'];directory.mkdir();r=Runner(directory,certipy,context=context)
        boundary=get_current_event_record_id(r.admin)
        dump(directory/'boundary.json',{'start_security_record_id':boundary})
        engine=LineageEngine(alias);update_reference(engine,output/'seed_events.xml',seed_ca)
        stop=threading.Event();polls=[];errors=[];samples=[]
        def sample():
            while not stop.wait(0.1):samples.append({'monotonic_ns':time.monotonic_ns(),'rss_kib':rss_kib()})
        def collect():
            cursor=boundary;index=0;worker=Runner(directory,certipy,context=context)
            while not stop.is_set():
                started=time.monotonic();path=directory/f'poll_{index:03d}.xml'
                try:
                    export_security(worker,cursor,path)
                    ca=ca_export(worker,f'poll_{index:03d}_ca')
                    received=time.monotonic();update_reference(engine,path,ca)
                    parsed=ET.parse(path).getroot()
                    ids=[int(c.text) for event in parsed for c in event.iter() if c.tag.rsplit('}',1)[-1]=='EventRecordID']
                    if ids:cursor=max(ids)
                    checkpoint=engine.checkpoint();(directory/f'poll_{index:03d}_checkpoint.json').write_text(checkpoint)
                    polls.append({'index':index,'started_monotonic':started,'export_envelope_seconds':received-started,
                        'collection_and_reasoning_seconds':time.monotonic()-started,'new_security_events':len(parsed),
                        'retained_reference_records':len(engine.records),'checkpoint_bytes':len(checkpoint.encode()),'rss_kib':rss_kib()})
                    index+=1
                except Exception as error:errors.append(type(error).__name__+': '+str(error));return
                stop.wait(max(0,protocol['poll_target_period_seconds']-(time.monotonic()-started)))
        sampler=threading.Thread(target=sample);sampler.start()
        collector=threading.Thread(target=collect) if arm['arm']=='polling' else None
        if collector:collector.start()
        start=time.monotonic();latencies=[]
        try:
            for i in range(protocol['authentications_per_arm']):
                delay=start+i*protocol['auth_start_period_seconds']-time.monotonic()
                if delay>0:time.sleep(delay)
                path=directory/f'auth_{i:02d}.json';authenticate(cert,key,certipy,user,path)
                latencies.append(json.loads(path.read_text())['elapsed_ns']/1e9)
        finally:
            measured_seconds=time.monotonic()-start;stop.set();sampler.join()
            if collector:collector.join()
        if errors:dump(directory/'collection_errors.json',errors);raise RuntimeError('Collector failed during pilot')
        export_security(r,boundary,directory/'ground_truth_events.xml')
        matching=[e for e in events(directory/'ground_truth_events.xml') if e['event_id']==4768 and
            hexkey(e['fields'].get('CertSerialNumber'))==hexkey(identity['serial']) and
            hexkey(e['fields'].get('CertThumbprint'))==hexkey(identity['sha1']) and e['fields'].get('Status') in ('0','0x0','0x00000000') and e['fields'].get('TargetSid')==sid]
        row={**arm,'authentication_process_envelopes_seconds':latencies,'median_authentication_seconds':statistics.median(latencies),
            'raw_successful_exact_certificate_kdc_records':len(matching),'expected_authentications':protocol['authentications_per_arm'],
            'measured_arm_seconds':measured_seconds,'polls':len(polls),'collector_rss_peak_kib':max((s['rss_kib'] for s in samples),default=rss_kib()),
            'retained_reference_records':len(engine.records),'scope':protocol['scope']}
        dump(directory/'rss_samples.json',samples);dump(directory/'polls.json',polls);dump(directory/'result.json',row);manifest(directory)
        arms.append(row);dump(output/'progress.json',arms);print(json.dumps({k:row[k] for k in ('id','raw_successful_exact_certificate_kdc_records','median_authentication_seconds','polls')}),flush=True)
    paired=[]
    for pair in range(1,4):
        values={r['arm']:r for r in arms if r['pair']==pair}
        paired.append({'pair':pair,'median_envelope_difference_seconds':values['polling']['median_authentication_seconds']-values['idle']['median_authentication_seconds']})
    dump(output/'results.json',{'arms':arms,'paired':paired,'scope':protocol['scope'],'latency_definition':protocol['latency'],'memory_definition':protocol['memory'],
        'all_expected_kdc_counts_match':all(r['raw_successful_exact_certificate_kdc_records']==r['expected_authentications'] for r in arms)})
    manifest(output)


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    f=s.add_parser('freeze');f.add_argument('protocol',type=Path)
    r=s.add_parser('run');r.add_argument('protocol',type=Path);r.add_argument('inventory',type=Path);r.add_argument('output',type=Path);r.add_argument('--certipy',required=True)
    a=p.parse_args()
    if a.action=='freeze':freeze(a.protocol)
    else:run(a.protocol,a.inventory,a.output,a.certipy)
