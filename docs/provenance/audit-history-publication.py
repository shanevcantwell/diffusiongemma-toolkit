#!/usr/bin/env python3
"""Read-only inventory generator for filtered refs/heads/main; writes evidence outside checkout.

Coverage patterns: private-key/PGP headers; major provider token prefixes; AWS key IDs;
JWTs; Authorization headers; credential-bearing or credential-query URLs; generic
secret/token/password/api-key assignments; netrc-style passwords; private filesystem
paths; and high-entropy base64/hex candidates. This is deterministic pattern/entropy
screening, not a substitute for provider-side token validation, revoked-secret history,
steganography/OCR, compressed/encrypted payload inspection, or undisclosed proprietary
secret formats. It collects candidates but does not classify them or certify PASS; manual
assessment is required. Exit status 0 means collection succeeded only.
"""
from __future__ import annotations
import argparse, collections, csv, datetime, hashlib, json, math, mimetypes, os, re, statistics, subprocess, sys
from pathlib import Path

MACHINE_STATUS = {
    'collection_status': 'COMPLETE',
    'assessment_status': 'NOT_ASSESSED',
}

p=argparse.ArgumentParser(
    description='Collect a deterministic history inventory; do not interpret exit 0 as an audit PASS.',
    epilog='Successful stdout JSON reports collection_status=COMPLETE and assessment_status=NOT_ASSESSED; manual classification is required.',
)
p.add_argument('--repo', required=True)
p.add_argument('--source', required=True)
p.add_argument('--main', required=True)
p.add_argument('--baseline', required=True)
p.add_argument('--allowlist', required=True)
p.add_argument('--commit-map', required=True)
p.add_argument('--out', required=True)
a=p.parse_args()
repo, source, out = Path(a.repo), Path(a.source), Path(a.out)
out.mkdir(parents=True, exist_ok=True)

def git(cwd, *args, input=None, text=False):
    r=subprocess.run(['git','-C',str(cwd),*args], input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return r.stdout.decode('utf-8','surrogateescape') if text else r.stdout

def sha256(b): return hashlib.sha256(b).hexdigest()
def write_tsv(path, header, rows):
    with open(path,'w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_MINIMAL)
        w.writerow(header); w.writerows(rows)
def esc(s): return s.replace('\\','\\\\').replace('\t','\\t').replace('\r','\\r').replace('\n','\\n')

def ls_tree(cwd, commit):
    raw=git(cwd,'ls-tree','-r','-z','--full-tree',commit)
    rows=[]
    for rec in raw.split(b'\0'):
        if not rec: continue
        meta,path=rec.split(b'\t',1)
        mode,typ,oid=meta.decode().split()
        rows.append((path.decode('utf-8','surrogateescape'),mode,typ,oid))
    return rows

allow_raw=Path(a.allowlist).read_bytes()
allow=allow_raw.decode().splitlines()
allow_set=set(allow)
if len(allow)!=67 or len(allow_set)!=67: raise SystemExit('allowlist is not 67 unique entries')
if git(repo,'rev-parse','refs/heads/main',text=True).strip()!=a.main: raise SystemExit('main moved before audit')
if git(source,'cat-file','-t',a.baseline,text=True).strip()!='commit': raise SystemExit('source baseline absent')

# Point-in-time ref inventory; object traversal below is explicitly main-only.
refs=[]
for line in git(repo,'for-each-ref','--format=%(refname)%09%(objecttype)%09%(objectname)',text=True).splitlines():
    ref,typ,oid=line.split('%09') if '%09' in line else line.split('\t')
    refs.append((ref,typ,oid,oid==a.main))
write_tsv(out/'audit-refs.tsv',['ref','object_type','object_id','equals_audited_main'],refs)

commits=git(repo,'rev-list','--reverse','--topo-order',a.main,text=True).splitlines()
source_commits=set(git(source,'rev-list',a.baseline,text=True).splitlines())
# old -> new filter map and exact retained inverse
cmap={}
with open(a.commit_map,encoding='utf-8') as f:
    next(f)
    for line in f:
        old,new=line.split()
        cmap[old]=new
inverse=collections.defaultdict(list)
for old,new in cmap.items():
    if new!='0'*40: inverse[new].append(old)

all_entries=[]; unique_blob_paths=set(); historical_paths=collections.defaultdict(list)
commit_rows=[]; message_records=[]; provenance=[]
for idx,c in enumerate(commits,1):
    entries=ls_tree(repo,c)
    for path,mode,typ,oid in entries:
        all_entries.append((idx,c,path,mode,typ,oid,path in allow_set))
        historical_paths[path].append((c,oid))
        if typ=='blob': unique_blob_paths.add((oid,path))
    raw=git(repo,'cat-file','commit',c)
    head,msg=(raw.split(b'\n\n',1)+[b''])[:2]
    headers=head.decode('utf-8','surrogateescape').splitlines()
    def vals(prefix): return [x[len(prefix):] for x in headers if x.startswith(prefix)]
    parents=vals('parent ')
    author=(vals('author ')+[''])[0]; committer=(vals('committer ')+[''])[0]
    enc=(vals('encoding ')+[''])[0]
    mtext=msg.decode('utf-8','surrogateescape')
    subject=mtext.splitlines()[0] if mtext.splitlines() else ''
    old_list=inverse.get(c,[])
    source_oid=old_list[0] if len(old_list)==1 else ''
    commit_rows.append((idx,c,source_oid,' '.join(parents),author,committer,enc,len(msg),sha256(msg),esc(subject)))
    message_records.append({'index':idx,'commit':c,'source_commit':source_oid,'message_utf8_surrogateescaped':mtext})
    if len(old_list)!=1:
        provenance.append((c,','.join(old_list),'FAIL','retained commit does not have exactly one source-map origin'))
        continue
    old=old_list[0]
    if old not in source_commits:
        provenance.append((c,old,'FAIL','mapped source commit not reachable from baseline'))
        continue
    selected=[e for e in ls_tree(source,old) if e[0] in allow_set]
    projection_ok=sorted(entries)==sorted(selected)
    # Author/committer identity+timestamps should survive filtering. Messages may have hash rewrites.
    sraw=git(source,'cat-file','commit',old)
    shead,smsg=(sraw.split(b'\n\n',1)+[b''])[:2]
    sh=shead.decode('utf-8','surrogateescape').splitlines()
    sa=[x[7:] for x in sh if x.startswith('author ')]
    sc=[x[10:] for x in sh if x.startswith('committer ')]
    meta_ok=(sa==vals('author ') and sc==vals('committer '))
    status='PASS' if projection_ok and meta_ok else 'FAIL'
    details=f'tree_projection={projection_ok};author_committer={meta_ok};message_equal={smsg==msg}'
    provenance.append((c,old,status,details))

write_tsv(out/'audit-tree-entries.tsv',['commit_index','commit','path','mode','type','object_id','allowlisted'],all_entries)
write_tsv(out/'audit-historical-paths.tsv',['path','allowlisted','commit_tree_occurrences','first_commit','last_commit'],
          [(path,path in allow_set,len(v),v[0][0],v[-1][0]) for path,v in sorted(historical_paths.items())])
write_tsv(out/'audit-commits.tsv',['index','filtered_commit','source_commit','filtered_parents','author_raw','committer_raw','encoding','message_bytes','message_sha256','subject_escaped'],commit_rows)
with open(out/'audit-commit-messages.jsonl','w',encoding='utf-8',errors='surrogateescape') as f:
    for r in message_records: f.write(json.dumps(r,ensure_ascii=True)+'\n')
write_tsv(out/'audit-commit-provenance.tsv',['filtered_commit','source_commit','status','details'],provenance)

# Unique reachable objects inventory from rev-list --objects (tree/commit/blob, deduped).
obj_ids=[]
for line in git(repo,'rev-list','--objects',a.main,text=True).splitlines():
    oid=line.split(' ',1)[0]
    if oid not in obj_ids: obj_ids.append(oid)
info={}
batch=(''.join(x+'\n' for x in obj_ids)).encode()
for line in git(repo,'cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)',input=batch,text=True).splitlines():
    oid,typ,size=line.split(); info[oid]=(typ,int(size))
write_tsv(out/'audit-reachable-objects.tsv',['object_id','type','size_bytes'],[(o,*info[o]) for o in obj_ids])

blob_paths=collections.defaultdict(set)
for oid,path in unique_blob_paths: blob_paths[oid].add(path)
blob_rows=[]; blob_data={}
text_count=binary_count=0
for oid in sorted(blob_paths):
    b=git(repo,'cat-file','blob',oid); blob_data[oid]=b
    paths=sorted(blob_paths[oid])
    has_nul=b'\x00' in b
    try: b.decode('utf-8'); utf8=True
    except UnicodeDecodeError: utf8=False
    cls='text' if (not has_nul and utf8) else 'binary'
    if cls=='text': text_count+=1
    else: binary_count+=1
    guesses=sorted(set((mimetypes.guess_type(x)[0] or ('text/plain' if cls=='text' else 'application/octet-stream')) for x in paths))
    exts=sorted(set(Path(x).suffix.lower() or '[none]' for x in paths))
    blob_rows.append((oid,len(b),cls,utf8,has_nul,','.join(guesses),','.join(exts),len(paths),json.dumps(paths,ensure_ascii=True)))
write_tsv(out/'audit-blobs.tsv',['blob_id','size_bytes','content_class','valid_utf8','contains_nul','mime_guesses_from_paths','extensions','path_count','historical_paths_json'],blob_rows)
write_tsv(out/'audit-blob-paths.tsv',['blob_id','path'],sorted(unique_blob_paths))

# Byte regexes run over every blob, including binary blobs. Matches are stored redacted.
# The generic assignment expression accepts quoted and unquoted keys across common
# config/code syntax. It is deliberately a byte heuristic, not a JSON/Python/YAML parser.
patterns=[
 ('private_key_header',rb'-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----'),
 ('pgp_private_key',rb'-----BEGIN PGP PRIVATE KEY BLOCK-----'),
 ('github_token',rb'(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{20,255}|github_pat_[A-Za-z0-9_]{20,255})(?![A-Za-z0-9_])'),
 ('gitlab_token',rb'(?<![A-Za-z0-9_-])glpat-[A-Za-z0-9_-]{20,255}'),
 ('slack_token',rb'(?<![A-Za-z0-9-])xox[baprs]-[A-Za-z0-9-]{10,255}'),
 ('google_api_key',rb'(?<![A-Za-z0-9_-])AIza[0-9A-Za-z_-]{35}(?![A-Za-z0-9_-])'),
 ('aws_access_key_id',rb'(?<![A-Z0-9])(?:AKIA|ASIA|AIDA|AROA|AIPA|ANPA|ANVA|ASCA)[A-Z0-9]{16}(?![A-Z0-9])'),
 ('stripe_live_key',rb'(?<![A-Za-z0-9_])(?:sk|rk)_live_[A-Za-z0-9]{16,255}'),
 ('npm_token',rb'(?<![A-Za-z0-9_])npm_[A-Za-z0-9]{20,255}'),
 ('pypi_token',rb'(?<![A-Za-z0-9_-])pypi-[A-Za-z0-9_-]{40,255}'),
 ('huggingface_token',rb'(?<![A-Za-z0-9_])hf_[A-Za-z0-9]{20,255}'),
 ('jwt',rb'(?<![A-Za-z0-9_-])eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}(?![A-Za-z0-9_-])'),
 ('authorization_header',rb'(?i)\bAuthorization\s*[:=]\s*(?:Bearer|Basic)\s+[A-Za-z0-9+/_.=-]{8,}'),
 ('credential_url_userinfo',rb'(?i)\b(?:https?|ssh|git|postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|amqps?)://[^\s/@:]+:[^\s/@]+@[^\s/]+'),
 ('credential_url_query',rb'(?i)\bhttps?://[^\s<>"\']{0,500}[?&](?:access_token|api[_-]?key|token|password|passwd|secret)=[^&\s<>"\']{6,}'),
 ('generic_secret_assignment',rb'''(?ix)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|secret[_-]?key|password|passwd|credential)\b\s*["']?\s*[:=]\s*["']?([A-Za-z0-9+/_.:@-]{8,})'''),
 ('netrc_password',rb'(?i)\bmachine\s+\S+\s+(?:login\s+\S+\s+)?password\s+\S+'),
 ('private_posix_home',rb'(?<![A-Za-z0-9_])/(?:home|Users)/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._~+@%=-]+)+'),
 ('private_windows_home',rb'(?i)\b[A-Z]:\\Users\\[^\s<>:"|?*]+(?:\\[^\s<>:"|?*]+)+'),
 ('private_config_path',rb'(?<![A-Za-z0-9_])(?:~/(?:\.ssh|\.aws|\.config|\.cache|\.huggingface)|/(?:tmp|var/tmp)/)[^\s<>"\']*'),
 ('file_url',rb'(?i)\bfile://(?:localhost)?/[^\s<>"\']+'),
]
compiled=[(n,re.compile(x)) for n,x in patterns]

def entropy(bs):
    if not bs:return 0
    cc=collections.Counter(bs); n=len(bs)
    return -sum((v/n)*math.log2(v/n) for v in cc.values())
entropy_res=[
 ('high_entropy_hex',re.compile(rb'(?<![0-9A-Fa-f])[0-9A-Fa-f]{32,128}(?![0-9A-Fa-f])'),3.3),
 ('high_entropy_base64',re.compile(rb'(?<![A-Za-z0-9+/_=-])[A-Za-z0-9+/_-]{32,200}={0,2}(?![A-Za-z0-9+/_=-])'),4.3),
]

def redact(m):
    b=m.group(0); n=len(b)
    if n<=8: return f'<redacted:{n}b>'
    # Keep only tiny edges, never a usable credential.
    return (b[:3].decode('ascii','replace')+f'<redacted:{n-6}b>'+b[-3:].decode('ascii','replace'))
findings=[]
def scan_bytes(axis, oid, paths, b):
    seen=set()
    for name,rx in compiled:
        for m in rx.finditer(b):
            key=(name,m.start(),m.end())
            if key in seen: continue
            seen.add(key)
            line=b.count(b'\n',0,m.start())+1
            findings.append((axis,oid,json.dumps(paths,ensure_ascii=True),line,name,len(m.group(0)),sha256(m.group(0)),redact(m),'UNCLASSIFIED',''))
    for name,rx,minent in entropy_res:
        for m in rx.finditer(b):
            token=m.group(0)
            # SHA-1/SHA-256/SHA-512-like pure hex identifiers are tracked by explicit contextual patterns, not entropy.
            if name=='high_entropy_hex' and len(token) in (40,64,128): continue
            ent=entropy(token.rstrip(b'='))
            if ent < minent: continue
            key=(name,m.start(),m.end())
            if key in seen: continue
            seen.add(key)
            line=b.count(b'\n',0,m.start())+1
            findings.append((axis,oid,json.dumps(paths,ensure_ascii=True),line,name,len(token),sha256(token),redact(m),'UNCLASSIFIED',f'entropy={ent:.3f}'))
for oid,b in blob_data.items(): scan_bytes('blob',oid,sorted(blob_paths[oid]),b)
for r in message_records:
    mb=r['message_utf8_surrogateescaped'].encode('utf-8','surrogateescape')
    scan_bytes('commit_message',r['commit'],[],mb)
write_tsv(out/'audit-scan-findings-unclassified.tsv',['axis','object_id','paths_json','line','pattern','match_bytes','match_sha256','redacted_match','classification','notes'],findings)

weight_exts={'.safetensors','.ckpt','.pt','.pth','.bin','.onnx','.gguf','.ggml','.h5','.hdf5','.npz','.npy','.pickle','.pkl','.joblib','.tar','.tgz','.gz','.bz2','.xz','.zip','.7z','.rar','.zst','.parquet','.arrow'}
weight_hits=sorted(path for path in historical_paths if Path(path).suffix.lower() in weight_exts)
sizes=sorted((len(b),oid) for oid,b in blob_data.items())
median=statistics.median(x for x,_ in sizes) if sizes else 0
p95=sizes[max(0,math.ceil(len(sizes)*.95)-1)][0] if sizes else 0
summary={
 **MACHINE_STATUS,
 'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'audited_ref':'refs/heads/main','audited_main':a.main,'source_baseline':a.baseline,
 'allowlist_entries':len(allow),'allowlist_sha256':sha256(allow_raw),
 'refs_count':len(refs),'refs_all_equal_main':all(r[2]==a.main for r in refs),
 'commits':len(commits),'historical_unique_paths':len(historical_paths),'non_allowlisted_paths':sorted(set(historical_paths)-allow_set),
 'tip_paths':len(ls_tree(repo,a.main)),'tree_entry_occurrences':len(all_entries),
 'reachable_objects':len(obj_ids),'object_type_counts':dict(collections.Counter(info[o][0] for o in obj_ids)),
 'unique_blobs':len(blob_data),'text_blobs':text_count,'binary_blobs':binary_count,
 'total_unique_blob_bytes':sum(len(x) for x in blob_data.values()),'max_blob_bytes':sizes[-1][0] if sizes else 0,
 'median_blob_bytes':median,'p95_blob_bytes':p95,'blobs_over_100KiB':sum(x>102400 for x,_ in sizes),'blobs_over_1MiB':sum(x>1048576 for x,_ in sizes),
 'top_10_blobs_by_size':[{'bytes':s,'blob':o,'paths':sorted(blob_paths[o])} for s,o in reversed(sizes[-10:])],
 'weight_or_archive_extension_paths':weight_hits,
 'source_reachable_commits':len(source_commits),'mapped_retained_commits':sum(len(inverse.get(c,[]))==1 for c in commits),
 'provenance_failures':sum(r[2]!='PASS' for r in provenance),
 'message_equal_source':sum('message_equal=True' in r[3] for r in provenance),
 'message_rewritten_by_filter':sum('message_equal=False' in r[3] for r in provenance),
 'scan_patterns':[n for n,_ in patterns]+[n for n,_,_ in entropy_res],
 'scan_findings_unclassified':len(findings),
 'coverage_limitations':['No trusted secret scanner was installed; deterministic procedural scanner used.','No provider-side token validity/revocation checks.','No OCR/steganography or decompression/decryption of embedded payloads.','Unknown proprietary token formats may evade documented patterns.','MIME is content-class plus Python extension guess because libmagic/file was unavailable.'],
}
(out/'audit-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
if git(repo,'rev-parse','refs/heads/main',text=True).strip()!=a.main: raise SystemExit('main moved during audit')
print(json.dumps(summary,indent=2,sort_keys=True))
