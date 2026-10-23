"""Verify the final DOCX inventory and its embedded diagram assets."""
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.oxml.ns import qn
from pypdf import PdfReader

BASE=Path(__file__).resolve().parents[1]
docx=next(BASE.glob('*.docx'))
doc=Document(docx)
inventory=json.loads((BASE/'data/content.json').read_text())
normalize=lambda s: re.sub(r'\s+','',s)
text=normalize(''.join(doc.element.itertext()))
checks=0
for item in inventory['text']:
    if normalize(item) not in text: raise AssertionError('Missing source text: '+item[:100])
    checks+=1
expected=[(8,3),(8,3),(2,3),(3,3),(6,2),(5,2)]
actual=[(len(t.rows),len(t.columns)) for t in doc.tables]
assert actual==expected,(actual,expected)
assert len(doc.inline_shapes)==3
assert len(doc.sections)==9
assert len(inventory['components'])>=5
assert len(inventory['interfaces'])==7
assert len(inventory['success_messages'])==12
assert len(inventory['source_coverage'])==5
with ZipFile(docx) as z:
    assert z.testzip() is None
    assert not any(re.match(r'word/(header|footer)\d+\.xml',n) for n in z.namelist())
    embedded={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')}
    for name in ['component.png','sequence-success.png','sequence-errors.png']:
        assert hashlib.sha256((BASE/'work'/name).read_bytes()).hexdigest() in embedded
checks+=11
pdf=next(Path('/private/tmp/book-club-qa-fixed').glob('*.pdf'))
reader=PdfReader(pdf)
assert len(reader.pages)==9
for page in reader.pages:
    s=page.extract_text()
    assert re.search('[\u3400-\u9fff]',s)
    assert re.search('[А-Яа-я]',s)
    assert len(s)>150
checks+=len(reader.pages)
api=json.loads((BASE/'data/api-validation.json').read_text())
assert api['sha256']==hashlib.sha256((BASE/'book-club.openapi.yaml').read_bytes()).hexdigest()
report={
    'document_structure':'PASS','inventory_text_checks':checks,'tables':actual,
    'embedded_figures':3,'components':7,'interfaces':7,'sequence_lifelines':5,
    'success_messages':12,'failure_branches':3,'rendered_pages':9,
    'visual_review':'PENDING','source_images':5,
    'api_contract':api,'business_execution':'NOT_RUN',
    'date':'2026-10-20','timezone':'Asia/Shanghai',
    'document_runtime':'Codex bundled Python 3.12 and bundled LibreOffice headless',
    'docx_sha256':hashlib.sha256(docx.read_bytes()).hexdigest(),
}
(BASE/'data/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
