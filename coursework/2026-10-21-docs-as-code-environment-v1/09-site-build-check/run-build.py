"""Record real strict-build exit codes without running application commands."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent/'08-sphinx-site/project-docs'
ART=ROOT/'artifacts'
ART.mkdir(parents=True,exist_ok=True)
phase=sys.argv[1]
assert phase in {'initial','final'}
paths=sorted(p for p in (PROJECT/'docs').rglob('*') if p.is_file())
hashes={str(p.relative_to(PROJECT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
if phase=='initial':
    (ART/'source-before.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2)+'\n')
command=[str(PROJECT/'.venv/bin/python'),'-m','sphinx','-b','html','-n','-W',
         '--keep-going','-E','-a','-N','-w',str(ART/(phase+'-warnings.log')),'docs','site']
start=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
p=subprocess.run(command,cwd=PROJECT,text=True,capture_output=True)
log=p.stdout+p.stderr
(ART/(phase+'-build.log')).write_text(log)
result={'phase':phase,'started_at':start,'finished_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'cwd':str(PROJECT),'command':command,'exit_code':p.returncode,
        'summary':'build succeeded.' if 'build succeeded.' in log else log.splitlines()[-1],
        'warning_bytes':(ART/(phase+'-warnings.log')).stat().st_size}
if phase=='final':
    before=json.loads((ART/'source-before.json').read_text())
    result['changed_document_sources']=[x for x in sorted(set(before)|set(hashes)) if before.get(x)!=hashes.get(x)]
    check=subprocess.run([str(PROJECT/'.venv/bin/python'),'verify.py'],cwd=PROJECT,text=True,capture_output=True)
    result['delivery_check_exit_code']=check.returncode
    (ART/'delivery-check.log').write_text(check.stdout+check.stderr)
    shutil.copy2(PROJECT/'artifacts/verification.json',ART/'delivery-verification.json')
(ART/(phase+'-build.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(p.returncode)
