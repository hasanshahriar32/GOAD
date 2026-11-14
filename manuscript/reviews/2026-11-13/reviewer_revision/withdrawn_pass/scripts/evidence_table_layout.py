"""Presentation rules shared by evidence generators; numerical cells are untouched."""
import re

WIDE = {'tab:stackelberg_results'}
HEADERS = {
 'tab:paired_live_policy':r'OS & Condition & Trials & Self & Admin & ESC1 & \makecell{Risky\\EKU}',
 'tab:current_patch_policy':r'\makecell{Request\\form} & Condition & Self & Admin & Reject & \makecell{ESC1\\pre} & \makecell{ESC1\\post}',
 'tab:hard_negatives':r'Implementation & Aug. & Correct & \makecell{False\\positive} & \makecell{False\\negative}',
 'tab:literal_bilinear':r'Model & Aug. & IID & \makecell{Long\\paths} & \makecell{Larger\\background}',
 'tab:lineage_confirmation':r'Method & \makecell{Definite\\links (\%)} & \makecell{Possible\\links (\%)} & \makecell{True\\overlap} & \makecell{False\\overlap}',
 'tab:order_component':r'\makecell{Order\\rate} & Method & \makecell{True\\overlaps} & Recovered & \makecell{False\\claims}',
 'tab:bridge_component':r'Method & \makecell{Retained\\true links} & \makecell{Certain\\true links} & \makecell{Wrong\\certain} & Hypotheses',
 'tab:sql_identity':r'Method & Resolved & Correct & Wrong & \makecell{True candidates\\retained}',
 'tab:transfer_workload':r'Condition & Cases & Self & Admin & \makecell{ESC1\\pre} & \makecell{ESC1\\post} & \makecell{Risky\\EKU}',
 'tab:collection_pilot':r'Pair & Arm & \makecell{Verified\\uses} & \makecell{Auth\\(ms)} & \makecell{CPU\\(ms)} & \makecell{RSS\\(MiB)}',
 'tab:scalability_bench':r'Nodes & \makecell{Queried\\pairs} & \makecell{Full\\(ms)} & \makecell{Projection +\\solve (ms)} & \makecell{Median\\ratio}',
}

def style_evidence_tables(text):
 def format_table(m):
  body=m[1];label=re.search(r'\\label\{([^}]+)\}',body)[1]
  wide=label in WIDE;env='table*' if wide else 'table'
  body=body.replace('\\small','\\evidencetable')
  captions={
   'tab:paired_live_policy':r'Matched policy interventions: three blocks per OS and three certificate uses per condition. The 2019 build is 17763.4974. Signed administrative CSR/key pairs are matched within blocks. ESC1 and risky EKU measure template configuration, not attack intent.',
   'tab:current_patch_policy':r'Certificate outcomes on Windows Server 2019 build 17763.9376: three trials per condition and request form. Reject denotes a certificate-bound KDC rejection. ESC1 pre/post are configuration findings before request and after rollback. Missing CA exports and later snapshot adjudication are described in Section~\ref{sec:evaluation}.',
   'tab:transfer_workload':r'Prospective new-forest workload: 24 certificates in six concurrent batches, two templates and two enrollers. Configuration columns count four template/batch/enroller units per condition, shared by eight certificate cases. The Windows image family is shared with the previous environment.',
   'tab:collection_pilot':r'Paired isolated-lab pilot; eight verified authentications per arm. Auth is the median Certipy process envelope (ms); CPU is Python collector CPU time (ms). RSS is Python collector MiB, excluding children and the Windows VM. Verification waits follow timing.',
   'tab:sql_identity':r'Identity projection on 1,410 histories, including 60 chronology-negative controls, with 1,241 true observed links. Event times are erased. The 60 wrong terminal claims per method are chronology controls; 60 separate forged-source controls also fool every method. These are identity-query outcomes, not full PIDS detection.',

   'tab:literal_bilinear':r'Literal two-layer attention: mean accuracy (\%) $\pm$ population SD over three seeds. Each test cohort contains 150 paired families per seed; initialization and augmentation are matched.',
   'tab:hard_negatives':r'Matched two-step diagnostic: 1,500 paired cases per arm (750 positive, 750 negative). Correct classification is a percentage; false positives and negatives are counts. Repeated training archetypes limit this synthetic diagnostic.',
   'tab:scalability_bench':r'Equal-query projection timing (ms), including projection construction. Three graph seeds and five alternating-order repetitions per seed; all severed-pair outcomes agree. Hierarchical synthetic graphs, shared host.',
  }
  if label in captions:
   start=body.index('\\caption{');pos=start+9;depth=1
   while depth:
    if body[pos]=='{':depth+=1
    elif body[pos]=='}':depth-=1
    pos+=1
   body=body[:start]+'\\caption{'+captions[label]+'}'+body[pos:]

  if label in HEADERS:
   a=body.index('\\toprule')+len('\\toprule');b=body.index('\\midrule',a)
   body=body[:a]+'\n'+HEADERS[label]+' \\\\\n'+body[b:]
  # Explicit wrapping retains readable type rather than scaling down the table.
  if not wide:
   for old,new in {
    'UPN + SID URL':r'\makecell[l]{UPN +\\SID URL}',
    'Baseline/admin request':r'\makecell[l]{Baseline/admin\\request}',
    'Rollback before request':r'\makecell[l]{Rollback before\\request}',
    'Legitimate self request':r'\makecell[l]{Legitimate self\\request}',
    'Subject bit enabled':r'\makecell[l]{Subject bit\\enabled}',
    'Feature-channel gate':r'\makecell[l]{Feature-channel\\gate}',
    'Additive attention':r'\makecell[l]{Additive\\attention}',
    'Bilinear attention':r'\makecell[l]{Bilinear\\attention}',
    'CIPG constraint reference':r'\makecell[l]{CIPG constraint\\reference}',
    'Intervals + observed order':r'\makecell[l]{Intervals +\\observed order}',
    'Ignore optional exports':r'\makecell[l]{Ignore optional\\exports}',
   }.items():body=body.replace(old,new)
  if label=='tab:stackelberg_results':
   body=body.replace(r'l@{\hspace{12pt}}c@{\hspace{18pt}}c@{\hspace{18pt}}c@{\hspace{18pt}}c','lcccc')
   body=body.replace('\\resizebox{\\textwidth}{!}{%','').replace('\\end{tabular}%\n}', '\\end{tabular}')
  return '\\begin{'+env+'}[tbp]\n'+body.strip()+'\n\\end{'+env+'}'
 return re.sub(r'\\begin\{table\*?\}\[[^\]]*\](.*?)\\end\{table\*?\}',format_table,text,flags=re.S)
