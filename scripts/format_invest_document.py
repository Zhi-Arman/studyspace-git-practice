"""Apply the reviewed spacing change to document 04 only."""
from pathlib import Path
import json
from docx import Document
from docx.shared import Pt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'coursework/2026-10-14-product-backlog-v1'
f=OUT/'data/invest-v1.json'
i=json.loads(f.read_text())
display={
 'US-001':'US-001-R 查询空座 / Найти места',
 'US-002':'US-002-R 创建预约 / Создать бронь',
 'US-003':'US-003-R 本人取消 / Своя отмена',
 'US-004':'US-004-A 审核 / Проверить\nUS-004-B 停用 / Отключить\nUS-004-C 重核 / Перепроверить\nUS-004-D 角色 / Назначить роль',
 'US-005':'US-005-A 房间 / Помещения\nUS-005-B 座位 / Места\nUS-005-C 开放时间 / Часы\nUS-005-D 安全缩减 / Сократить доступ'
}
path=OUT/i['path']
doc=Document(path)
doc.styles['Normal'].paragraph_format.line_spacing=Pt(14)
doc.styles['Normal'].paragraph_format.space_after=Pt(2.5)
for r in i['rows']:r['result_display']=display[r['id']]
for n,row in enumerate(doc.tables[0].rows[1:]):
 row.cells[8].text=i['rows'][n]['result_display']
 for run in row.cells[8].paragraphs[0].runs:run.font.size=Pt(9.5)
for t in doc.tables:
 for row in t.rows:
  for c in row.cells:
   for p in c.paragraphs:
    p.paragraph_format.line_spacing=Pt(12.5)
for p in list(doc.paragraphs):
 if p.text.startswith(('原故事：','Исходная история:')):
  p._p.getparent().remove(p._p)
paragraphs=doc.paragraphs
for n,p in enumerate(paragraphs):
 if p.style.name=='Heading 2' and p.text.startswith('US-'):
  for a in paragraphs[n:]:
   a.paragraph_format.keep_with_next=not a.text.startswith('需求 / Требования')
   if a.text.startswith('需求 / Требования'):break
method_section=False
for p in paragraphs:
 if p.text.startswith('4 判断口径'):method_section=True
 if method_section and p.style.name=='Normal':
  p.paragraph_format.line_spacing=Pt(12.5)
  p.paragraph_format.space_after=Pt(1.5)
 if p.text.startswith('Bill Wake,'):
  p.text='Bill Wake, INVEST in Good Stories, and SMART Tasks, 2003-08-17. 查阅 / Дата обращения 2026-10-14.\nhttps://xp123.com/invest-in-good-stories-and-smart-tasks/'
  for run in p.runs:run.font.size=Pt(9)
method_heading=next(p for p in doc.paragraphs if p.text.startswith('4 判断口径'))
for p in list(doc.paragraphs):
 if p.text.startswith(('候选故事的验收条件','Условия приёмки кандидатов')):
  method_heading._p.addprevious(p._p)
doc.save(path)
f.write_text(json.dumps(i,ensure_ascii=False,indent=2))
# Rebuild the Markdown mirror from the reviewed DOCX in document order.
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
from docx.table import Table
from docx.text.paragraph import Paragraph
lines=[]
for node in doc.element.body:
 if node.tag.endswith('}p'):
  p=Paragraph(node,doc)
  if p.text:lines.append(p.text)
 elif node.tag.endswith('}tbl'):
  t=Table(node,doc)
  lines.append('| '+' | '.join(c.text.replace('\n','<br>') for c in t.rows[0].cells)+' |')
  lines.append('| '+' | '.join('---' for _ in t.columns)+' |')
  lines.extend('| '+' | '.join(c.text.replace('\n','<br>') for c in r.cells)+' |' for r in t.rows[1:])
path.with_suffix('.md').write_text('\n\n'.join(lines))
print('Updated spacing and bilingual result labels in document 04 only.')
