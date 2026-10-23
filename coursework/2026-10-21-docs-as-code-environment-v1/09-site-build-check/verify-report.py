"""Validate task-five evidence and the editable bilingual handoff."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent;ART=ROOT/'artifacts'
checks=[]
def check(label,ok):checks.append({'check':label,'passed':bool(ok)})
for phase in ['initial','final']:
 b=json.loads((ART/(phase+'-build.json')).read_text())
 check(phase+' strict options',all(x in b['command'] for x in ['-n','-W','-E','-a']))
 check(phase+' exit code and warning log',b['exit_code']==0 and b['warning_bytes']==0 and (ART/(phase+'-warnings.log')).read_bytes()==b'')
 check(phase+' real success log','build succeeded.' in (ART/(phase+'-build.log')).read_text())
final=json.loads((ART/'final-build.json').read_text())
check('document sources unchanged',not final['changed_document_sources'])
project=ROOT.parent/'08-sphinx-site/project-docs'
before=json.loads((ART/'source-before.json').read_text())
check('all source hashes still match',all(hashlib.sha256((project/k).read_bytes()).hexdigest()==v for k,v in before.items()))
browser=json.loads((ART/'browser-check.json').read_text());rows=browser['checks'];byid={x['id']:x for x in rows}
check('all 13 browser checks passed',len(rows)==13 and all(x['passed'] for x in rows))
check('minimum five links resources or transitions',sum(x['id'].startswith('L') for x in rows)==8)
check('all four pages clicked from contents',all(byid['L0'+str(i)]['passed'] for i in range(1,5)))
check('heading anchor inspected',byid['L05']['passed'] and bool(byid['L05']['result']['hash']))
check('image loaded and directly opened',byid['L06']['result']['complete'] and byid['L06']['result']['naturalWidth']==1000 and byid['L07']['passed'])
check('commands tables warnings inspected',all(byid[x]['passed'] for x in ['R01','R02','R03']))
old=json.loads((ART/'browser-check-initial.json').read_text())
check('initial tooling error retained',any('operation timed out' in x['output'] for x in old['records']))
check('final tooling commands succeeded',all(x['exit_code']==0 for x in browser['records']))
delivery=json.loads((ART/'delivery-verification.json').read_text())
check('88 existing delivery checks',delivery['passed']==delivery['total']==88)
check('250 local links no break',delivery['local_link_checks']==250 and not delivery['broken_links'])
check('22 original materials preserved',delivery['preserved_originals']==22)
name='StudySpace_任务五网站与构建检查_中俄双语_v1'
md=(ROOT/(name+'.md')).read_text()
check('application verification boundary','NOT_RUN' in md and '应用命令没有在本轮执行' in md)
check('error fix and repeated result recorded','CHK-01' in md and '复测' in md and 'DOM' in md)
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(ROOT/(name+'.docx')) as z:
 check('docx zip integrity',z.testzip() is None)
 xml=ET.fromstring(z.read('word/document.xml'));content=''.join(xml.itertext())
 model=json.loads((ART/'report-content.json').read_text())
 check('paired headings and paragraphs in Word',all(b['zh'] in content and b['ru'] in content for b in model if b['type'] in {'heading','pair'}))
 check('seven editable tables',len(xml.findall('.//w:tbl',ns))==7)
 check('no decorative paragraph borders',not xml.findall('.//w:pBdr',ns))
check('four final page renders',len(list((ART/'report-render-final').glob('page-*.png')))==4)
check('input image and six requirements',(ART/'task-input.json').is_file() and len(json.loads((ART/'task-input.json').read_text())['requirements'])==6)
report={'checks':checks,'passed':sum(c['passed'] for c in checks),'total':len(checks),'report_pages':4,
        'browser_checks':13,'link_resource_checks':8,'application_commands':'NOT_RUN','business_tests':'NOT_RUN'}
(ART/'report-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False))
for c in checks:
 if not c['passed']:print('FAIL',c['check'])
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
