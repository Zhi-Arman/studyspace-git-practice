"""Check delivery requirements, source preservation and built local links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from zipfile import ZipFile
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
checks=[]
def check(label, ok):
    checks.append({'check':label, 'passed':bool(ok)})

required=['requirements-docs.txt','docs/conf.py','docs/index.md','docs/user-guide.md',
          'docs/admin-guide.md','docs/release-notes.md','docs/document-register.md',
          'docs/images/development-chain.svg','build-evidence.md','review.md','site/index.html']
for name in required:check('file: '+name,(ROOT/name).is_file())
admin=(ROOT/'docs/admin-guide.md').read_text()
for number, zh,ru in [(1,'用途与组成','Назначение и состав'),(2,'要求与访问','Требования и доступ'),
 (3,'安装与验证','Установка и проверка'),(4,'配置','Конфигурация'),(5,'启动停止与观察','Запуск остановка и наблюдение'),
 (6,'备份与恢复','Резервное копирование и восстановление'),(7,'更新与回滚','Обновление и откат'),
 (8,'诊断','Диагностика'),(9,'限制与未验证说明','Ограничения и непроверенные инструкции')]:
    check(f'bilingual chapter {number}',f'## {number} {zh} / {number} {ru}' in admin)
for n, start, stop in [('01','### AG-P01','## 4 '),('02','### AG-P02','### 5.5 AG-P03'),
                     ('03','### 5.5 AG-P03','## 6 '),('04','### AG-P04','## 7 '),('05','### AG-P05','## 8 ')]:
    segment=admin.split(start,1)[1].split(stop,1)[0]
    for label in ['用途','前置条件','操作','预期结果','失败处理','验证记录']:
        check(f'AG-P{n} field {label}',label in segment)
check('warning before restoration command',admin.index('警告：禁止覆盖')<admin.index('.venv/bin/python 07-admin-guide/sqlite-backup-restore.py'))
check('schema rollback limitation','回滚应用不会自动回滚数据库模式' in admin)
check('backup suitability before update','更新前先备份，并通过恢复到新文件验证备份可用性' in admin)
check('business status retained','38 个业务用例仍 NOT_RUN' in admin)
manifest=json.loads((ROOT/'artifacts/source-manifest.json').read_text())
for item in manifest:
    orig=hashlib.sha256(Path(item['source']).read_bytes()).hexdigest()
    copy=hashlib.sha256((ROOT/item['copy']).read_bytes()).hexdigest()
    check('unchanged original and copy: '+item['copy'],orig==copy==item['sha256'])
user_orig=next(Path(x['source']).read_text() for x in manifest if x['copy'].endswith('candidates/user-guide.md'))
check('user steps and relative links retained',user_orig[user_orig.index('读者：'):] in (ROOT/'docs/user-guide.md').read_text())

ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
word=ROOT/'StudySpace_管理员手册_中俄双语_v0.2.docx'
with ZipFile(word) as z:
    check('docx zip integrity',z.testzip() is None)
    xml=ET.fromstring(z.read('word/document.xml'))
    text=''.join(xml.itertext())
    model=json.loads((ROOT/'artifacts/admin-content.json').read_text())
    check('docx bilingual paragraph parity',all(b['zh'] in text and b['ru'] in text for b in model['blocks'] if b['type'] in {'pair','heading'}))
    check('docx tables',len(xml.findall('.//w:tbl',ns))==3)
    check('docx no paragraph borders',not xml.findall('.//w:pBdr',ns))

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=set();self.links=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.add(attrs['id'])
        key='href' if tag in {'a','link'} else 'src' if tag in {'img','script'} else None
        if key and attrs.get(key):self.links.append(attrs[key])
site=ROOT/'site'
pages={p:Page() for p in site.rglob('*.html')}
for path,parser in pages.items():parser.feed(path.read_text())
broken=[];local_count=0;external=set()
for path,parser in pages.items():
    for link in parser.links:
        u=urlsplit(link)
        if u.scheme or u.netloc:
            external.add(link);continue
        local_count+=1
        target=(path.parent/unquote(u.path)).resolve() if u.path else path
        if target.is_dir():target=target/'index.html'
        if not target.is_relative_to(site) or not target.is_file():
            broken.append({'from':str(path.relative_to(site)),'link':link,'reason':'missing file'})
        elif u.fragment and target.suffix=='.html' and unquote(u.fragment) not in pages[target].ids:
            broken.append({'from':str(path.relative_to(site)),'link':link,'reason':'missing anchor'})
check('all local links resources and anchors',not broken)
for name in ['index','user-guide','admin-guide','release-notes','document-register']:
    check('html page '+name,(site/(name+'.html')).is_file())
check('zero sphinx warnings',(ROOT/'artifacts/sphinx-warnings.log').read_text().strip()=='')
report={'date':'2026-10-21','timezone':'Asia/Shanghai','checks':checks,
        'passed':sum(x['passed'] for x in checks),'total':len(checks),
        'local_link_checks':local_count,'broken_links':broken,'external_links_not_crawled':sorted(external),
        'preserved_originals':len(manifest),'business_tests':'NOT_RUN','human_acceptance':'PENDING'}
(ROOT/'artifacts/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['passed','total','local_link_checks','broken_links','preserved_originals']},ensure_ascii=False))
for item in checks:
    if not item['passed']:print('FAIL:',item['check'])
raise SystemExit(0 if all(x['passed'] for x in checks) else 1)
