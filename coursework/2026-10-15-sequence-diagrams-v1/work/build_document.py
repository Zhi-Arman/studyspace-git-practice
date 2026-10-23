from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
from zipfile import ZipFile
from html import escape
import hashlib
import json
import math
import re
import shutil
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.section import WD_SECTION_START, WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path('/Users/zhi/Documents/软件生命周期/studyspace')
OUT = ROOT / 'coursework/2026-10-15-sequence-diagrams-v1'
DATA = OUT / 'data'
FIG = OUT / 'diagrams'
WORK = OUT / 'work'
for d in [OUT, DATA, FIG, WORK, DATA / 'sources']:
    d.mkdir(parents=True, exist_ok=True)
STEM = 'StudySpace_双场景时序图与说明_中俄双语_v1'
DOCX = OUT / (STEM + '.docx')
DRAWIO = OUT / 'StudySpace_双场景时序图_中俄双语_v1.drawio'
SOURCES = {
    'components': ROOT.parent / 'StudySpace_组件交付/StudySpace_组件候选与组件图_中俄双语_v2.md',
    'component_diagram': ROOT.parent / 'StudySpace_组件交付/StudySpace_组件图_课堂任务2_中俄双语.drawio',
    'design_zh': ROOT / 'docs/zh-CN/04_System_Design.md',
    'design_ru': ROOT / 'docs/ru-RU/04_System_Design.md',
    'decisions': ROOT / 'docs/data/project-decisions.json',
    'requirements': ROOT / 'coursework/2026-10-13-requirements-v0.2/data/requirements-practice.json',
    'stories': ROOT / 'coursework/2026-10-14-product-backlog-v1/03_StudySpace_用户故事待办表_中俄双语_v1.md',
    'rules': ROOT / 'AGENTS.md',
}
FINGERPRINTS = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES.values()}
photo_names = [
    'codex-clipboard-66888e3d-5a4d-47e0-bd09-b2f0c753480e.jpg',
    'codex-clipboard-c781409c-a3a3-485b-9d9d-dac7c8c8936f.jpg',
    'codex-clipboard-9006110b-83bb-469f-8336-263fc660fd09.jpg',
    'codex-clipboard-cdebf69a-881a-4a7c-8919-fa2885540a78.jpg',
]
for i, n in enumerate(photo_names, 1):
    src = Path('/var/folders/ff/kqw394c93dd7krl0z2hcqqdh0000gn/T') / n
    shutil.copy2(src, DATA / 'sources' / f'classroom-{i:02d}.jpg')

COMPONENTS = [
    ('CMP-001', '学生与管理员界面', 'Интерфейс студента и администратора'),
    ('CMP-002', '账号认证与权限控制', 'Аутентификация и права доступа'),
    ('CMP-003', '校内身份审核与预约资格', 'Проверка принадлежности к вузу и допуск'),
    ('CMP-004', '房间座位与开放规则管理', 'Помещения места и правила работы'),
    ('CMP-006', '预约事务与冲突控制', 'Транзакции бронирования и конфликты'),
    ('CMP-008', '审计与数据生命周期', 'Аудит и жизненный цикл данных'),
    ('CMP-009', '数据访问与持久化', 'Доступ к данным и хранение'),
    ('CMP-010', '可信学校核验来源', 'Доверенный источник вуза'),
]

HEADERS = [
    ('用例 Use Case', 'Прецедент'),
    ('为什么重要', 'Почему важен'),
    ('参与者 组件与外部系统', 'Участники компоненты и внешние системы'),
    ('用于时序图的替代流程', 'Альтернативный поток для диаграммы'),
]
ROWS = [
    [
        ('US-002\n学生创建单座位预约', 'US-002\nСтудент бронирует одно место'),
        ('主要场景。实现项目的核心价值，并保护同学生与同座位的时段互斥，避免并发重复占用。',
         'Основной сценарий. Реализует цель проекта и исключает пересечения студента и места, включая конкурентные заявки.'),
        ('学生；CMP-001 界面；CMP-002 认证；CMP-003 资格；CMP-004 资源；CMP-006 预约；CMP-008 审计；CMP-009 数据。无外部系统。',
         'Студент; CMP-001 интерфейс; CMP-002 доступ; CMP-003 допуск; CMP-004 ресурсы; CMP-006 бронирование; CMP-008 аудит; CMP-009 данные. Внешних систем нет.'),
        ('资格或时间规则不通过：403 或 422；同学生或同座位时段冲突：409，回滚且不创建。相邻与多条非重叠预约允许。',
         'Недопуск или неверное время: 403 либо 422. Пересечение студента или места: 409, откат без создания. Соседние и несколько непересекающихся записей допустимы.'),
    ],
    [
        ('US-004\n管理员审核校内身份', 'US-004\nАдминистратор проверяет принадлежность к вузу'),
        ('风险场景。审核决定预约资格，依赖真实学校证据，并涉及权限、个人信息和审核竞争。',
         'Рискованный сценарий. Решение даёт допуск к бронированию, зависит от реальных сведений вуза и связано с правами, личными данными и гонкой проверок.'),
        ('管理员；CMP-001 界面；CMP-002 认证；CMP-003 校内审核；CMP-008 审计；CMP-009 数据；外部 CMP-010 学校核验来源，由管理员人工查询。',
         'Администратор; CMP-001 интерфейс; CMP-002 доступ; CMP-003 проверка; CMP-008 аудит; CMP-009 данные; внешний CMP-010 источник вуза, проверяемый вручную.'),
        ('来源无法核实：不授予 VERIFIED，保持 PENDING；可信证据不符：REJECTED；审核期间身份或状态变化：409；管理员无权限：403。',
         'Источник не проверен: без VERIFIED, остаётся PENDING. Достоверные сведения не совпадают: REJECTED. Изменение данных или статуса: 409. Нет прав: 403.'),
    ],
]


class Canvas:
    """One model feeds raster, vector and editable diagram representations."""
    def __init__(self, width=2200):
        self.width = width
        self.items = []
        self.height = 150

    def rect(self, x, y, w, h, fill='#FFFFFF', stroke='#728392', dash=False):
        self.items.append(dict(kind='rect', x=x, y=y, w=w, h=h, fill=fill, stroke=stroke, dash=dash))

    def line(self, x1, y1, x2, y2, dash=False, arrow=False, color='#253F51'):
        self.items.append(dict(kind='line', x1=x1, y1=y1, x2=x2, y2=y2, dash=dash, arrow=arrow, color=color))

    def text(self, x, y, text, size=27, color='#152431', align='center', bg=False):
        self.items.append(dict(kind='text', x=x, y=y, text=text, size=size, color=color, align=align, bg=bg))

    def render(self, base):
        scale = 2
        image = Image.new('RGB', (self.width * scale, math.ceil(self.height) * scale), 'white')
        dr = ImageDraw.Draw(image)
        font_cache = {}
        def font(txt, size):
            chinese = bool(re.search('[\u3000-\u303f\u4e00-\u9fff]', txt))
            key = chinese, size
            if key not in font_cache:
                p = '/System/Library/Fonts/STHeiti Light.ttc' if chinese else '/System/Library/Fonts/Supplemental/Arial.ttf'
                font_cache[key] = ImageFont.truetype(p, size * scale)
            return font_cache[key]
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">',
               '<defs><marker id="arr" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9" fill="#253F51"/></marker></defs>',
               '<rect width="100%" height="100%" fill="white"/>']
        for it in self.items:
            if it['kind'] == 'rect':
                x, y, w, h = [it[k] for k in ['x', 'y', 'w', 'h']]
                dr.rectangle((x*scale, y*scale, (x+w)*scale, (y+h)*scale), fill=it['fill'], outline=it['stroke'], width=2*scale)
                svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{it["fill"]}" stroke="{it["stroke"]}" stroke-width="2"/>')
            elif it['kind'] == 'line':
                x1, y1, x2, y2 = [it[k] for k in ['x1', 'y1', 'x2', 'y2']]
                length = math.hypot(x2-x1, y2-y1)
                if it['dash']:
                    for p in range(0, int(length), 20):
                        q = min(p+11, length)
                        dr.line(((x1+(x2-x1)*p/length)*scale, (y1+(y2-y1)*p/length)*scale,
                                 (x1+(x2-x1)*q/length)*scale, (y1+(y2-y1)*q/length)*scale), fill=it['color'], width=2*scale)
                else:
                    dr.line((x1*scale, y1*scale, x2*scale, y2*scale), fill=it['color'], width=2*scale)
                if it['arrow']:
                    direction = 1 if x2 > x1 else -1
                    dr.polygon([(x2*scale,y2*scale),((x2-direction*13)*scale,(y2-7)*scale),((x2-direction*13)*scale,(y2+7)*scale)], fill=it['color'])
                dash = ' stroke-dasharray="11 9"' if it['dash'] else ''
                marker = ' marker-end="url(#arr)"' if it['arrow'] else ''
                svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{it["color"]}" stroke-width="2"{dash}{marker}/>')
            else:
                x, y, txt, size = [it[k] for k in ['x','y','text','size']]
                f = font(txt, size)
                box = dr.textbbox((0,0),txt,font=f)
                tw, th = box[2]-box[0], box[3]-box[1]
                tx = x*scale - (tw/2 if it['align']=='center' else 0)
                ty = y*scale - th/2 - box[1]
                if it['bg']:
                    dr.rectangle((tx-7, y*scale-th/2-3, tx+tw+7, y*scale+th/2+4),fill='white')
                    sx = x-tw/scale/2 if it['align']=='center' else x
                    svg.append(f'<rect x="{sx-3}" y="{y-th/scale/2-2}" width="{tw/scale+6}" height="{th/scale+4}" fill="white"/>')
                dr.text((tx,ty),txt,font=f,fill=it['color'])
                anch = 'middle' if it['align']=='center' else 'start'
                svg.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anch}" dominant-baseline="central" fill="{it["color"]}" font-family="Arial,Heiti SC,sans-serif">{escape(txt)}</text>')
        svg.append('</svg>')
        image.save(base.with_suffix('.png'))
        base.with_suffix('.svg').write_text('\n'.join(svg),encoding='utf-8')


class Sequence:
    def __init__(self, key, lanes, continued=False):
        self.key, self.lanes = key, lanes
        self.c = Canvas()
        self.x = {a[0]: 150+i*1900/(len(lanes)-1) for i,a in enumerate(lanes)}
        self.y = 162
        self.messages = []
        self.frames = []
        for k, zh, ru in lanes:
            x = self.x[k]
            self.c.rect(x-125,12,250,112,fill='#EAF0F5')
            self.c.text(x,35,k if k.startswith('CMP-') else '«actor»',26)
            self.c.text(x,68,zh,28)
            self.c.text(x,100,ru,25)
        self.continued = continued

    def note(self, zh, ru):
        self.c.text(1100,self.y,zh,26)
        self.c.text(1100,self.y+31,ru,25)
        self.y += 72

    def msg(self, n, src, dst, zh, ru, ret=False):
        x1, x2 = self.x[src], self.x[dst]
        center = (x1+x2)/2
        # Labels may extend beyond short arrows but never beyond the canvas.
        longest = max(len(zh)*16, len(ru)*13)
        center = max(longest/2+45,min(2155-longest/2,center))
        self.c.text(center,self.y+12,f'{n}  {zh}',27,bg=True)
        self.c.text(center,self.y+42,ru,25,bg=True)
        if src==dst:
            self.c.line(x1,self.y+60,x1+90,self.y+60)
            self.c.line(x1+90,self.y+60,x1+90,self.y+80)
            self.c.line(x1+90,self.y+80,x1,self.y+80,arrow=True)
            step=94
        else:
            self.c.line(x1,self.y+62,x2,self.y+62,dash=ret,arrow=True)
            step=77
        self.messages.append(dict(number=n,src=src,dst=dst,zh=zh,ru=ru,return_message=ret,y=self.y))
        self.y += step

    def frame(self, zh, ru, nested=False):
        start=self.y
        self.c.text(90 if nested else 48,start+19,'alt',26,align='left')
        self.c.text(1100,start+18,zh,26,bg=True)
        self.c.text(1100,start+49,ru,25,bg=True)
        self.y += 76
        return start

    def branch(self, zh, ru, nested=False):
        inset=90 if nested else 32
        self.c.line(inset,self.y,2168 if not nested else 2130,self.y,dash=True,color='#728392')
        self.c.text(1100,self.y+22,zh,26,bg=True)
        self.c.text(1100,self.y+53,ru,25,bg=True)
        self.y += 80

    def end_frame(self,start,nested=False):
        inset=90 if nested else 32
        # Place frame outline behind its labels and lifelines.
        frame=dict(kind='rect',x=inset,y=start,w=2200-2*inset,h=self.y-start+10,fill=None,stroke='#728392',dash=False)
        self.frames.append(frame)
        self.y+=24

    def finish(self):
        self.c.height=self.y+20
        lines=[dict(kind='line',x1=x,y1=124,x2=x,y2=self.c.height-12,dash=True,arrow=False,color='#A2ADB6') for x in self.x.values()]
        # Non-filled frames become line primitives to keep raster and SVG exact.
        frame_lines=[]
        for f in self.frames:
            x,y,w,h=[f[k] for k in ['x','y','w','h']]
            for a,b,c,d in [(x,y,x+w,y),(x,y+h,x+w,y+h),(x,y,x,y+h),(x+w,y,x+w,y+h)]:
                frame_lines.append(dict(kind='line',x1=a,y1=b,x2=c,y2=d,dash=False,arrow=False,color='#728392'))
        self.c.items=lines+frame_lines+self.c.items
        self.c.render(FIG/self.key)
        return self


LANES1=[('学生','学生','Студент'),('CMP-001','界面','Интерфейс'),('CMP-006','预约事务','Бронирование'),('CMP-002','认证权限','Доступ'),('CMP-003','校内资格','Допуск вуза'),('CMP-004','资源规则','Ресурсы'),('CMP-008','审计事件','Аудит'),('CMP-009','数据访问','Данные')]
LANES2=[('管理员','管理员','Администратор'),('CMP-001','界面','Интерфейс'),('CMP-002','认证权限','Доступ'),('CMP-003','校内审核','Проверка вуза'),('CMP-008','审计事件','Аудит'),('CMP-009','数据访问','Данные'),('CMP-010','学校来源 外部','Источник вуза')]

s1a=Sequence('01_booking_part_a',LANES1)
s1a.note('前提 已登录并选择已有座位；路径为拟定 API','Условие: вход выполнен, место выбрано; API проектируется')
s1a.msg('1','学生','CMP-001','选择 seat_id、D、start、end','Выбрать место, дату и интервал')
s1a.msg('2','CMP-001','CMP-006','POST /api/v1/bookings + session','Передать заявку и сессию')
s1a.msg('3','CMP-006','CMP-002','校验会话与学生角色','Проверить сессию и роль студента')
s1a.msg('4','CMP-002','CMP-006','返回服务端 user_id 与权限','Вернуть user_id и права',True)
s1a.msg('5','CMP-006','CMP-009','BEGIN；锁 User → Room → Seat','Начать транзакцию и взять блокировки')
s1a.msg('6','CMP-009','CMP-006','返回 tx 与锁后实际 now','Вернуть tx и фактическое время после блокировок',True)
s1a.msg('7','CMP-006','CMP-003','在 tx 内复核启用、角色、VERIFIED','Повторно проверить активность, роль и VERIFIED')
s1a.msg('8','CMP-003','CMP-006','返回资格校验结果','Вернуть результат допуска',True)
s1a.msg('9','CMP-006','CMP-004','在 tx 内校验座位、开放与时段','Проверить место, часы и время в tx')
s1a.msg('10','CMP-004','CMP-006','返回资源与时间校验结果','Вернуть результат проверки ресурсов и времени',True)
s1a.msg('11','CMP-006','CMP-009','查询同学生或同座位的区间重叠','Найти пересечения студента или места в tx')
s1a.msg('12','CMP-009','CMP-006','返回冲突类型或无冲突','Вернуть тип конфликта либо его отсутствие',True)
s1a.note('校验结果统一进入下一部分；拒绝分支不产生业务写入','Результаты передаются в часть Б; отказ не создаёт запись')
s1a.finish()

s1b=Sequence('01_booking_part_b',LANES1,True)
s1b.note('延续同一 tx；所有成功响应均在 COMMIT 确认后返回','Продолжение той же tx; успех возвращается после COMMIT')
f=s1b.frame('[资格失败或资源／时间不合法]','[Нет допуска либо неверны ресурс или время]')
s1b.msg('13a','CMP-006','CMP-009','ROLLBACK','Откатить транзакцию')
s1b.msg('14a','CMP-006','CMP-001','403 / 422 + 原因码','Отказать с кодом причины',True)
s1b.branch('[校验通过，且学生或座位区间冲突]','[Проверки пройдены, но есть пересечение]')
s1b.msg('13b','CMP-006','CMP-009','ROLLBACK','Откатить транзакцию')
s1b.msg('14b','CMP-006','CMP-001','409 + STUDENT_OVERLAP / SEAT_OVERLAP','Вернуть тип пересечения',True)
s1b.msg('15b','CMP-001','学生','提示更换时段或重新选择','Предложить другой интервал или выбор',True)
s1b.branch('[校验通过，且无区间冲突]','[Проверки пройдены и пересечений нет]')
s1b.msg('13c','CMP-006','CMP-009','写入一个座位的预约 tx','Создать запись одного места в tx')
s1b.msg('14c','CMP-009','CMP-006','返回 booking_id 尚未提交','Вернуть booking_id до фиксации',True)
s1b.msg('15c','CMP-006','CMP-008','记录创建事件 tx、booking_id、actor','Подготовить событие создания в той же tx')
s1b.msg('16c','CMP-008','CMP-009','写入事件 tx、event_at','Сохранить событие без отдельного COMMIT')
s1b.msg('17c','CMP-006','CMP-009','COMMIT 预约与事件','Зафиксировать запись и событие вместе')
s1b.msg('18c','CMP-009','CMP-006','提交成功','Фиксация успешна',True)
s1b.msg('19c','CMP-006','CMP-001','201 Created + booking_id、seat、start、end','Вернуть созданную запись',True)
s1b.msg('20c','CMP-001','学生','显示预约确认','Показать подтверждение',True)
s1b.end_frame(f)
s1b.finish()

s2a=Sequence('02_review_part_a',LANES2)
s2a.note('前提 目标为 PENDING；学校来源由管理员人工查验','Условие: студент PENDING; источник вуза проверяется вручную')
s2a.msg('1','管理员','CMP-001','打开待审核学生','Открыть студента на проверку')
s2a.msg('2','CMP-001','CMP-003','GET /api/v1/identity-reviews/pending','Запросить данные для проверки')
s2a.msg('3','CMP-003','CMP-002','校验管理员会话与权限','Проверить сессию и права администратора')
s2a.msg('4','CMP-002','CMP-003','返回管理员身份与权限','Вернуть администратора и права',True)
s2a.msg('5','CMP-003','CMP-009','读取目标身份、状态与快照','Прочитать данные, статус и снимок студента')
s2a.msg('6','CMP-009','CMP-003','返回必要学号、姓名、PENDING、revision','Вернуть необходимые поля и версию снимка',True)
s2a.msg('7','CMP-003','CMP-001','返回最少必要审核信息','Вернуть минимальные сведения для проверки',True)
s2a.msg('8','CMP-001','管理员','展示身份及审核状态','Показать данные и статус',True)
s2a.msg('9','管理员','CMP-010','人工核对学校认可来源 IF-04','Вручную сверить с признанным вузом источником')
s2a.msg('10','CMP-010','管理员','得到可信证据或来源不可用','Получить сведения либо недоступность источника',True)
s2a.msg('11','管理员','CMP-001','填写决定与来源类型、引用','Внести решение, тип источника и ссылку')
s2a.msg('12','CMP-001','CMP-003','POST /api/v1/identity-reviews','Передать user_id, решение, ссылку и revision')
s2a.msg('13','CMP-003','CMP-002','再次校验管理员会话','Повторно проверить сессию администратора')
s2a.msg('14','CMP-002','CMP-003','返回当前管理员身份','Вернуть текущую личность администратора',True)
s2a.msg('15','CMP-003','CMP-009','BEGIN；按固定顺序锁相关账号','Начать tx и блокировать аккаунты в едином порядке')
s2a.msg('16','CMP-009','CMP-003','返回权限、PENDING 与当前 revision','Вернуть права, статус и текущую версию',True)
s2a.note('9、10 为人工信息交互；tx 延续至下一部分','Шаги 9 и 10 ручные; та же tx продолжается в части Б')
s2a.finish()

s2b=Sequence('02_review_part_b',LANES2,True)
s2b.note('延续同一 tx；锁内复核权限、可信依据和身份状态','Продолжение той же tx; сверить права, основания и состояние')
f=s2b.frame('[无管理员权限，或来源不可核验]','[Нет прав администратора либо источник не проверен]')
s2b.msg('17a','CMP-003','CMP-009','ROLLBACK；审核状态保持不变','Откат; статус проверки не изменяется')
s2b.msg('18a','CMP-003','CMP-001','403 / 422；不得授予 VERIFIED','Отказ без предоставления VERIFIED',True)
s2b.branch('[权限与来源有效，但身份快照或状态已变化]','[Права и источник действуют, но данные или статус изменились]')
s2b.msg('17b','CMP-003','CMP-009','ROLLBACK','Откатить транзакцию')
s2b.msg('18b','CMP-003','CMP-001','409 STALE_REVIEW；重新读取','Вернуть конфликт и потребовать обновление',True)
s2b.branch('[权限与可信依据有效，且快照一致]','[Права и основания действуют, снимок совпадает]')
f2=s2b.frame('[可信核验相符]','[Достоверные сведения совпадают]',nested=True)
s2b.msg('17c','CMP-003','CMP-009','在 tx 中保存决定 VERIFIED','Сохранить решение VERIFIED в tx')
s2b.branch('[可信核验确实不符]','[Установлено достоверное несоответствие]',nested=True)
s2b.msg('17d','CMP-003','CMP-009','在 tx 中保存决定 REJECTED','Сохранить решение REJECTED в tx')
s2b.end_frame(f2,nested=True)
s2b.msg('18','CMP-003','CMP-008','记录 user_id、审核人、时间、决定、来源引用','Подготовить автора, время, решение и ссылку')
s2b.msg('19','CMP-008','CMP-009','写审核事件 tx，不复制身份或影像','Записать событие в tx без копий данных и фото')
s2b.msg('20','CMP-003','CMP-009','COMMIT 状态与事件','Зафиксировать статус и событие вместе')
s2b.msg('21','CMP-009','CMP-003','提交成功','Фиксация успешна',True)
s2b.msg('22','CMP-003','CMP-001','200 OK + VERIFIED / REJECTED','Вернуть сохранённый статус для показа',True)
s2b.end_frame(f)
s2b.finish()

PANELS=[s1a,s1b,s2a,s2b]


def export_drawio():
    mxfile=ET.Element('mxfile',host='app.diagrams.net',type='device',version='29.6.6')
    for n,(title,parts) in enumerate([('US-002 创建座位预约 Бронирование',[s1a,s1b]),('US-004 校内身份审核 Проверка вуза',[s2a,s2b])],1):
        diagram=ET.SubElement(mxfile,'diagram',id=f'studyspace-sequence-{n}',name=title)
        total_h=sum(p.c.height for p in parts)+180
        model=ET.SubElement(diagram,'mxGraphModel',dx='2200',dy=str(total_h),grid='1',gridSize='10',page='1',pageScale='1',pageWidth='2200',pageHeight=str(total_h),math='0',shadow='0')
        root=ET.SubElement(model,'root')
        ET.SubElement(root,'mxCell',id='0')
        ET.SubElement(root,'mxCell',id='1',parent='0')
        count=0
        offset=65
        def vertex(value,x,y,w,h,style):
            nonlocal count
            count+=1
            c=ET.SubElement(root,'mxCell',id=f'n{n}-{count}',value=value,style=style,vertex='1',parent='1')
            ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
        vertex(title,20,0,2160,48,'text;html=0;fontSize=32;fontStyle=1;align=center;strokeColor=none;fillColor=none;')
        for p in parts:
            for it in p.c.items:
                if it['kind']=='line':
                    count+=1
                    style='edgeStyle=none;html=0;rounded=0;strokeWidth=2;strokeColor='+it['color']+';'
                    style+='dashed=1;dashPattern=6 5;' if it['dash'] else ''
                    style+='endArrow=classic;endFill=1;' if it['arrow'] else 'endArrow=none;'
                    cell=ET.SubElement(root,'mxCell',id=f'n{n}-{count}',style=style,edge='1',parent='1')
                    geo=ET.SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'})
                    ET.SubElement(geo,'mxPoint',x=str(it['x1']),y=str(it['y1']+offset),attrib={'as':'sourcePoint'})
                    ET.SubElement(geo,'mxPoint',x=str(it['x2']),y=str(it['y2']+offset),attrib={'as':'targetPoint'})
                elif it['kind']=='rect':
                    vertex('',it['x'],it['y']+offset,it['w'],it['h'],f'rounded=0;fillColor={it["fill"]};strokeColor={it["stroke"]};strokeWidth=2;')
                else:
                    width=min(2120,max(220,len(it['text'])*it['size']*.9))
                    x=it['x']-width/2 if it['align']=='center' else it['x']
                    style=f'text;html=0;whiteSpace=wrap;overflow=visible;fontSize={it["size"]};fontFamily=Arial;align={it["align"]};verticalAlign=middle;strokeColor=none;fillColor={"#FFFFFF" if it["bg"] else "none"};fontColor={it["color"]};'
                    vertex(it['text'],x,it['y']+offset-20,width,40,style)
            offset+=p.c.height+70
    ET.ElementTree(mxfile).write(DRAWIO,encoding='utf-8',xml_declaration=True)


export_drawio()

doc=Document()
def section(landscape=False,new=False):
    s=doc.add_section(WD_SECTION_START.NEW_PAGE) if new else doc.sections[0]
    s.orientation=WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
    s.page_width=Inches(11 if landscape else 8.5)
    s.page_height=Inches(8.5 if landscape else 11)
    s.top_margin=s.bottom_margin=Inches(.4 if landscape else .6)
    s.left_margin=s.right_margin=Inches(.6)
    return s
section()
for name in ['Normal','Title','Heading 1','Heading 2']:
    st=doc.styles[name]
    st.font.name='Arial'
    st.font.color.rgb=RGBColor(0,0,0)
    rf=st.element.get_or_add_rPr().get_or_add_rFonts()
    rf.set(qn('w:ascii'),'Arial');rf.set(qn('w:hAnsi'),'Arial');rf.set(qn('w:eastAsia'),'Heiti SC')
    for b in list(st.element.iter(qn('w:pBdr'))): b.getparent().remove(b)
doc.styles['Normal'].font.size=Pt(11)
doc.styles['Normal'].paragraph_format.line_spacing=1.04
doc.styles['Normal'].paragraph_format.space_after=Pt(4)
doc.styles['Title'].font.size=Pt(19)
doc.styles['Title'].paragraph_format.space_after=Pt(4)
doc.styles['Heading 1'].font.size=Pt(14)
doc.styles['Heading 1'].paragraph_format.space_before=Pt(9)
doc.styles['Heading 1'].paragraph_format.space_after=Pt(4)
doc.styles['Heading 2'].font.size=Pt(12)
doc.styles['Heading 2'].paragraph_format.space_before=Pt(7)
doc.styles['Heading 2'].paragraph_format.space_after=Pt(3)

MD=[]
def para(text,style=None,size=None,lang='zh-CN'):
    p=doc.add_paragraph(style=style)
    r=p.add_run(text)
    r.font.name='Arial';r.font.color.rgb=RGBColor(0,0,0)
    if size:r.font.size=Pt(size)
    rp=r._element.get_or_add_rPr()
    rp.rFonts.set(qn('w:eastAsia'),'Heiti SC')
    l=OxmlElement('w:lang');l.set(qn('w:val'),lang);l.set(qn('w:eastAsia'),'zh-CN');rp.append(l)
    return p

def pair(zh,ru,style=None,size=None):
    after_table=doc.element.body[-2].tag==qn('w:tbl') if len(doc.element.body)>1 else False
    p=para(zh,style,size);p.paragraph_format.keep_with_next=True
    p.paragraph_format.space_after=Pt(2)
    if after_table:p.paragraph_format.space_before=Pt(5)
    p=para(ru,style,size,'ru-RU');p.paragraph_format.keep_together=True
    p.paragraph_format.space_after=Pt(4)
    if style in {'Heading 1','Heading 2','Title'}:
        p.paragraph_format.space_before=Pt(0)
    MD.extend([zh,ru,''])
    return p

def table(headers,rows,widths,size=9.5):
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for c,w in zip(t.columns,widths):c.width=Inches(w)
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','left','bottom','right','insideH','insideV']:
        el=OxmlElement('w:'+edge)
        for k,v in [('val','single'),('sz','5'),('color','D9D9D9')]:el.set(qn('w:'+k),v)
        borders.append(el)
    t._tbl.tblPr.append(borders)
    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for ri,vals in enumerate([headers,*rows]):
        row=t.rows[0] if ri==0 else t.add_row()
        ns=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(ns)
        for ci,(c,val) in enumerate(zip(row.cells,vals)):
            c.width=Inches(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tc=c._tc.get_or_add_tcPr();mar=OxmlElement('w:tcMar')
            for edge in ['top','bottom','left','right']:
                el=OxmlElement('w:'+edge);el.set(qn('w:w'),'90');el.set(qn('w:type'),'dxa');mar.append(el)
            tc.append(mar)
            sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'29485D' if ri==0 else ('F1F5F8' if ri%2 else 'FFFFFF'));tc.append(sh)
            for li,txt in enumerate(val):
                p=c.paragraphs[0] if li==0 else c.add_paragraph()
                p.paragraph_format.space_after=Pt(4 if li==0 else 0)
                p.paragraph_format.line_spacing=1.03
                p.paragraph_format.keep_with_next=False
                p.alignment=WD_ALIGN_PARAGRAPH.CENTER if ri==0 else WD_ALIGN_PARAGRAPH.LEFT
                r=p.add_run(txt);r.font.name='Arial';r.font.size=Pt(size);r.bold=ri==0
                r.font.color.rgb=RGBColor.from_string('FFFFFF' if ri==0 else '000000')
                rp=r._element.get_or_add_rPr();rp.rFonts.set(qn('w:eastAsia'),'Heiti SC')
                lang=OxmlElement('w:lang');lang.set(qn('w:val'),'zh-CN' if li==0 else 'ru-RU');rp.append(lang)
    MD.append('| '+' | '.join('<br>'.join(v).replace('\n','<br>') for v in headers)+' |')
    MD.append('| '+' | '.join('---' for _ in headers)+' |')
    MD.extend('| '+' | '.join('<br>'.join(v).replace('\n','<br>') for v in row)+' |' for row in rows)
    MD.append('')
    return t

pair('StudySpace 双场景时序图与说明','StudySpace Диаграммы последовательности двух сценариев','Title')
para('SS-SEQ-01  |  v1  |  2026-10-15  |  DRAFT',size=9)
pair('本文选择核心预约场景 US-002 和风险审核场景 US-004，给出场景选择表、时序图与流程说明。组件编号沿用 SS-ARCH-03 v2，需求基线为课堂 v0.2 与工程文档 0.3.0。',
     'Выбраны основной сценарий бронирования US-002 и рискованный сценарий проверки US-004. Приведены таблица выбора, диаграммы и пояснения. ID компонентов взяты из SS-ARCH-03 v2; требования из учебной v0.2 и инженерной 0.3.0.',size=10.5)
pair('1 两个场景的选择表','1 Таблица выбора двух сценариев','Heading 1')
table(HEADERS,ROWS,[1.13,1.42,2.25,2.5],9.5)
pair('图中路径、错误码及审核快照 revision 为本文件拟定的设计契约；不代表现有业务接口。业务实现未完成，业务测试保持 NOT_RUN。',
     'Пути API, коды ошибок и revision снимка проверки являются предлагаемыми контрактами. Это не готовые бизнес-интерфейсы; реализация не завершена, бизнес-тесты остаются NOT_RUN.',size=9)

doc.add_page_break()
pair('2 场景一 学生创建单座位预约','2 Сценарий один Бронирование одного места студентом','Heading 1')
pair('2.1 目标与前后条件','2.1 Цель и условия','Heading 2')
pair('目标是创建一条单座位预约。学生已登录并选中已有座位，但查询结果不保证提交时空闲。服务端重新检查启用状态、STUDENT 角色和 VERIFIED 资格。',
     'Цель — создать запись одного места. Студент вошёл и выбрал место, но поиск не гарантирует доступность при отправке. Сервер повторно проверяет активность, STUDENT и VERIFIED.')
pair('预约与创建事件一起提交或回滚。请求含 seat_id、业务日期 D、带时区的 start/end；user_id 从服务端会话取得，不信任客户端自报身份。',
     'Бронирование и событие фиксируются или откатываются вместе. Запрос содержит seat_id, дату D и start/end с часовым поясом; user_id берётся из серверной сессии, а не от клиента.')
pair('2.2 主流程与替代流程','2.2 Основной и альтернативные потоки','Heading 2')
pair('步骤 1–12：提交、授权、事务加锁，按锁后实际时刻复核资格与资源时间，并查询同学生和同座位的重叠。图 1A、1B 是同一时序图的连续两部分。',
     'Шаги 1–12: заявка, авторизация, блокировки, повторная проверка допуска, ресурсов и времени, поиск пересечений студента и места. Время берётся после блокировок. Рисунки 1А и 1Б продолжают одну диаграмму.')
pair('分支 a：资格不符返回 403，资源或时间不合法返回 422。分支 b：校验通过但区间冲突，返回 409 及冲突类型，并回滚。分支 c：全部通过，写预约和审计事件，提交成功后返回 201 与预约编号。所有分支互斥。',
     'Ветка a: нет допуска — 403, неверный ресурс или время — 422. Ветка b: проверки пройдены, но есть пересечение — 409 с типом конфликта и откат. Ветка c: записать бронь и событие, после успешного COMMIT вернуть 201 и ID. Ветки взаимоисключающие.')
pair('2.3 关键业务与事务规则','2.3 Правила бронирования и транзакции','Heading 2')
pair('预约区间为 [start,end)。同学生或同座位满足 existing.start < new.end 且 new.start < existing.end 即冲突；取消记录不占用。相邻区间允许，同一学生可持有多条非重叠预约，不设置全局未结束预约总量限制。',
     'Интервал — [start,end). Пересечение студента либо места: existing.start < new.end и new.start < existing.end; отменённые записи не занимают время. Соседние интервалы и несколько непересекающихся записей одного студента допустимы; общего лимита незавершённых записей нет.')
pair('使用 Asia/Shanghai 业务日，UTC 存储；默认 08:00–22:00、30 分钟粒度，最短 30 分钟、硬上限 24 小时，限今天至今天+6 且不跨所选业务日。默认窗口实际最多 14 小时；start 必须晚于锁后实际 now。',
     'Деловой день — Asia/Shanghai, хранение — UTC. По умолчанию 08:00–22:00 с шагом 30 минут; минимум 30 минут, предел 24 часа, от сегодня до сегодня+6 без выхода за выбранный день. При обычных часах максимум 14 часов; start позже фактического now после блокировок.')
pair('PostgreSQL 锁序为 User → Room → Seat；SQLite 使用 BEGIN IMMEDIATE，二者锁机制不同。锁超时属于暂时不可用，未知数据库异常属于服务端错误，不能全部返回 409。并发尚待验证。',
     'PostgreSQL: User → Room → Seat; SQLite: BEGIN IMMEDIATE с иным механизмом блокировки. Тайм-аут — временная недоступность, неизвестный сбой БД — ошибка сервера, а не 409. Конкурентность ещё не проверена.',size=10)


def add_figure(p,zh,ru,alt):
    section(True,True)
    pair(zh,ru,'Heading 1',12)
    for hp in doc.paragraphs[-2:]:
        hp.paragraph_format.space_before=Pt(0)
        hp.paragraph_format.space_after=Pt(2)
        hp.paragraph_format.line_spacing=1
    q=doc.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    q.paragraph_format.space_after=Pt(0)
    q.paragraph_format.line_spacing=1
    shape=q.add_run().add_picture(str(FIG/(p.key+'.png')),width=Inches(9.8))
    shape._inline.docPr.set('descr',alt)
    MD.append(f'![{alt}](diagrams/{p.key}.svg)\n')

add_figure(s1a,'图 1A US-002 提交与事务内校验','Рисунок 1А US-002 Отправка и проверки в транзакции','US-002 中俄双语时序图 前半 Диаграмма US-002 часть А')
add_figure(s1b,'图 1B US-002 条件分支与提交','Рисунок 1Б US-002 Ветвление и фиксация','US-002 中俄双语时序图 后半 Диаграмма US-002 часть Б')

section(False,True)
pair('3 场景二 管理员审核校内身份','3 Сценарий два Проверка принадлежности к вузу','Heading 1')
pair('3.1 目标与前后条件','3.1 Цель и условия','Heading 2')
pair('管理员依据学校认可的可信来源，审核 PENDING 学生。须有有效管理权限；CMP-010 是人工核验依赖，不假设已有 SSO 或自动学校 API。',
     'Администратор с действующими правами проверяет студента PENDING по признанному вузом источнику. CMP-010 — ручная проверка без предположения о готовом SSO или API вуза.')
pair('真实核验相符为 VERIFIED，确实不符为 REJECTED；无法取得可信来源时保持 PENDING。实际来源仍由 OPEN-003 确认，不能声称已完成真实学校核验。',
     'Достоверное совпадение даёт VERIFIED, несоответствие — REJECTED; без проверяемого источника сохраняется PENDING. Реальный источник уточняется в OPEN-003, фактическая проверка вуза не заявляется.')
pair('3.2 主流程与替代流程','3.2 Основной и альтернативные потоки','Heading 2')
pair('步骤 1–12：授权后显示必要身份与状态，管理员人工核对 CMP-010，提交审核决定、来源类型及引用、快照版本。图 2A、2B 连续展示同一场景。',
     'Шаги 1–12: авторизовать чтение, показать необходимые сведения, вручную сверить CMP-010 и отправить решение, тип и ссылку источника с revision снимка. Рисунки 2А и 2Б продолжают один сценарий.')
pair('步骤 13–22：保存时再次授权，在事务与固定锁序下复核管理员、目标账号状态和身份快照。无权限返回 403；来源无法核实返回 422；身份或状态已变化返回 409 并要求刷新。其余情况按相符或不符保存决定和审核事件，提交后返回 200。',
     'Шаги 13–22: повторно авторизовать сохранение и в транзакции с единым порядком блокировок сверить администратора, аккаунт и снимок. Нет прав — 403; источник не проверен — 422; данные или статус изменились — 409 с обновлением. Иначе по результату сверки сохранить решение и событие, после COMMIT вернуть 200.')
pair('3.3 数据保护与边界','3.3 Данные и границы','Heading 2')
pair('User 保留必要学号、姓名及当前状态；审核事件仅含 user_id、审核人、event_at、决定、来源类型与引用，不复制原始学号、姓名或证明影像。状态与事件共用同一事务。',
     'User хранит необходимые номер, имя и статус; событие — user_id, автора, event_at, решение, тип и ссылку источника без копий номера, имени или изображений. Статус и событие используют одну транзакцию.')
pair('revision 是本次拟定的身份与状态快照契约，实现机制待开发。身份变更、停用及其取消预约联动是其他场景，沿用既有规则。',
     'revision — предлагаемый контракт снимка идентификаторов и статуса; реализация определяется при разработке. Их изменение, отключение и отмена записей — другие сценарии по прежним правилам.')
pair('PENDING 仅可登录只读；启用且 VERIFIED 的 STUDENT 可预约；REJECTED 可申请复核。学生后续读取自身状态查看结果，不增加自动通知。',
     'PENDING даёт только чтение; активный STUDENT с VERIFIED бронирует; после REJECTED возможна повторная заявка. Результат читается в статусе студента без автоматического уведомления.',size=10)

add_figure(s2a,'图 2A US-004 人工核验与事务复核','Рисунок 2А US-004 Ручная сверка и повторные проверки','US-004 中俄双语时序图 前半 Диаграмма US-004 часть А')
add_figure(s2b,'图 2B US-004 条件分支与审核提交','Рисунок 2Б US-004 Ветвление и сохранение проверки','US-004 中俄双语时序图 后半 Диаграмма US-004 часть Б')

section(False,True)
pair('4 参与组件与课堂要求核对','4 Компоненты и сверка с заданием','Heading 1')
pair('4.1 与既有组件图的对应','4.1 Соответствие диаграмме компонентов','Heading 2')
table([('编号','ID'),('组件名称','Компонент'),('使用场景','Сценарий')],
      [[(cid,cid),(zh,ru),('场景一、场景二' if cid in {'CMP-001','CMP-002','CMP-003','CMP-008','CMP-009'} else ('场景一' if cid in {'CMP-004','CMP-006'} else '场景二 外部人工依赖'),
        'Оба сценария' if cid in {'CMP-001','CMP-002','CMP-003','CMP-008','CMP-009'} else ('Сценарий один' if cid in {'CMP-004','CMP-006'} else 'Сценарий два Внешняя ручная зависимость'))] for cid,zh,ru in COMPONENTS],
      [1.0,4.25,2.05],9.5)
pair('CMP-005 可用性查询发生于场景一的前置选择阶段；CMP-007 记录统计不在这两个交互范围内，故未新增生命线。学生与管理员是角色，不新增组件。CMP-009 包含持久化访问，未再增设独立“数据库组件”。',
     'CMP-005 используется при предварительном выборе; CMP-007 со статистикой вне этих взаимодействий, поэтому отдельные линии не добавлены. Студент и администратор — акторы. CMP-009 представляет доступ к хранению без нового компонента БД.',size=10)
pair('4.2 表达方式与一致性','4.2 Обозначения и согласованность','Heading 2')
pair('实线箭头表示调用或提交，虚线箭头表示返回，竖虚线为生命线。alt 条件互斥，每次仅执行一个满足条件的分支。两图均无需 opt 或 loop；不增加提醒或循环。内部空返回可省略。',
     'Сплошная стрелка — вызов или отправка, пунктирная — возврат, вертикальный пунктир — линия жизни. Условия alt взаимоисключающие, выполняется одна подходящая ветка. Здесь opt и loop не нужны; пустые внутренние возвраты могут опускаться.',size=10)
pair('界面通过候选 HTTPS/JSON API 调用后端；CMP-002 至 CMP-009 的交互是 FastAPI 模块化单体内部调用，不表示独立微服务。图中的事务、锁、规则检查及接口均是设计内容。',
     'Интерфейс вызывает сервер через предлагаемый HTTPS/JSON API; взаимодействия CMP-002–CMP-009 — внутренние вызовы модульного монолита FastAPI, а не микросервисы. Транзакции, блокировки, проверки и API на схемах являются проектом.',size=10)

doc.add_page_break()
pair('5 追溯与计划验证','5 Трассируемость и план проверки','Heading 1')
trace_rows=[
    [('US-002','US-002'),('SP-FR-007、SP-FR-008、SP-FR-009；SP-NFR-004；DEC-016','SP-FR-007, SP-FR-008, SP-FR-009; SP-NFR-004; DEC-016'),('TC-007、TC-008、TC-017、TC-025、TC-030、TC-031、TC-032、TC-033','TC-007, TC-008, TC-017, TC-025, TC-030, TC-031, TC-032, TC-033')],
    [('US-004','US-004'),('SP-FR-004、SP-FR-022；SP-IF-002；SP-DR-001；OPEN-003','SP-FR-004, SP-FR-022; SP-IF-002; SP-DR-001; OPEN-003'),('TC-001、TC-003、TC-015、TC-035、TC-038','TC-001, TC-003, TC-015, TC-035, TC-038')],
]
table([('场景','Сценарий'),('主要需求与决定','Требования и решения'),('既有计划测试','Плановые тесты')],trace_rows,[1.0,3.65,2.65],9.5)
pair('两场景的业务测试均为 NOT_RUN。计划验证预约正常创建、同学生／同座位重叠、相邻与非重叠多预约、并发与事务回滚；审核验证可信通过、不符拒绝、来源缺失、权限失效和审核期间数据变化。',
     'Бизнес-тесты обоих сценариев имеют статус NOT_RUN. Планируются создание, пересечения студента и места, соседние и непересекающиеся записи, конкуренция и откат; для проверки — достоверный успех, отказ, отсутствие источника, утрата прав и изменение данных.')
pair('课程内容检查包括恰好两个用例、四列表格、统一组件编号、标注消息及响应、明确 alt 条件，以及中俄上下对应。文档结构和页面检查不等于业务运行验证或教师验收。',
     'Проверка материала включает два Use Case, четыре колонки, единые ID компонентов, подписи сообщений и ответов, условия alt и пары китайского и русского текста. Проверка документа и страниц не является запуском бизнеса или приёмкой преподавателя.')
pair('6 依据与交付信息','6 Основания и сведения о результате','Heading 1')
pair('课堂依据为本次四张图片：元素与片段提示、预约示例、从场景到时序图的步骤、两个场景的选择表。最终选择表保留原四列和两条场景记录。',
     'Учебные основания — четыре фото: элементы и фрагменты, пример бронирования, переход от сценария к диаграмме и таблица выбора двух сценариев. Итоговая таблица сохраняет четыре колонки и две записи.')
pair('项目依据为 SS-ARCH-03 v2 统一组件表与组件图、DOC-04 系统设计 0.3.0、课堂需求登记 v0.2、用户故事待办 SS-PB-05 v1、project-decisions.json 中的 DEC-016。OPEN-003 的真实来源仍待确认。',
     'Основания проекта: единые компоненты и схема SS-ARCH-03 v2, DOC-04 0.3.0, учебный реестр v0.2, бэклог SS-PB-05 v1 и DEC-016 в project-decisions.json. Реальный источник OPEN-003 остаётся неуточнённым.')
pair('执行环境为本地 macOS 与 Codex 内置 Python、文档渲染工具；本次仅新增课程设计材料。可编辑 draw.io 文件含 US-002 与 US-004 两个页签，每个页签保留前后两部分。',
     'Среда — локальная macOS, встроенные Python и средства рендеринга Codex. Добавлен учебный проектный материал. Редактируемый файл draw.io содержит вкладки US-002 и US-004 с обеими частями каждого сценария.')
pair('交付目录','Каталог результата','Heading 2')
para(str(OUT),size=9)
doc.core_properties.title='StudySpace 双场景时序图与说明 Диаграммы последовательности'
doc.core_properties.subject='两个场景 四列选择表 中俄双语 / Два сценария и таблица выбора'
doc.core_properties.author='StudySpace'
doc.core_properties.comments='Design artifact. Business tests NOT_RUN.'
doc.save(DOCX)
(OUT/(STEM+'.md')).write_text('\n\n'.join(MD),encoding='utf-8')

content={
    'doc_id':'SS-SEQ-01','version':'v1','date':'2026-10-15','status':'DRAFT','business_tests':'NOT_RUN',
    'headers':HEADERS,'scenario_rows':ROWS,'components':COMPONENTS,
    'panels':[{'key':p.key,'height':p.c.height,'lanes':[x[0] for x in p.lanes],'messages':p.messages} for p in PANELS],
    'source_fingerprints':FINGERPRINTS,
    'proposed_contracts':['POST /api/v1/bookings','GET /api/v1/identity-reviews/pending','POST /api/v1/identity-reviews','revision','HTTP response and reason codes'],
}
(DATA/'content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'fonts.conf').write_text('''<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd"><fontconfig>
<dir>/System/Library/Fonts</dir><dir>/System/Library/Fonts/Supplemental</dir><dir>/Library/Fonts</dir><dir>/Users/zhi/Library/Fonts</dir>
<cachedir>/private/tmp/studyspace-sequence-fontcache</cachedir>
<match target="pattern"><test name="family"><string>sans-serif</string></test><edit name="family" mode="prepend"><string>Arial</string><string>Heiti SC</string></edit></match>
</fontconfig>''',encoding='utf-8')

rd=Document(DOCX)
with ZipFile(DOCX) as z:
    xml=ET.fromstring(z.read('word/document.xml'))
    names=z.namelist()
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
txt='\n'.join(p.text for p in rd.paragraphs)+'\n'+'\n'.join(c.text for t in rd.tables for r in t.rows for c in r.cells)
requirements=json.loads(SOURCES['requirements'].read_text())
reqids={x['id'] for x in requirements['requirements']}
allmessages=[m for p in PANELS for m in p.messages]
checks={
    'selection_table_exactly_four_columns_two_scenarios':len(rd.tables[0].columns)==4 and len(rd.tables[0].rows)==3,
    'selection_table_preserves_four_fields':all(rd.tables[0].cell(0,i).text=='\n'.join(h) for i,h in enumerate(HEADERS)),
    'selection_rows_match_bilingual_data':all(rd.tables[0].cell(i+1,j).text=='\n'.join(v) for i,row in enumerate(ROWS) for j,v in enumerate(row)),
    'all_tables_bilingual_pairs':all(len(c.paragraphs)==2 for t in rd.tables for r in t.rows for c in r.cells),
    'two_use_cases_reuse_story_ids':all(k in SOURCES['stories'].read_text() for k in ['US-002','US-004']),
    'all_component_ids_from_existing_component_table':all(cid in SOURCES['components'].read_text() for cid,_,_ in COMPONENTS),
    'no_new_system_component_lifelines':all(k in {'学生','管理员'}|{c[0] for c in COMPONENTS} for p in PANELS for k,_,_ in p.lanes),
    'all_message_endpoints_present':all(m['src'] in {l[0] for l in p.lanes} and m['dst'] in {l[0] for l in p.lanes} for p in PANELS for m in p.messages),
    'all_messages_have_chinese_and_russian':all(re.search('[\u4e00-\u9fff]',m['zh']) or m['zh'].startswith(('POST','GET','BEGIN','ROLLBACK','COMMIT','403','409','201','200')) for m in allmessages) and all(re.search('[А-Яа-яЁё]',m['ru']) for m in allmessages),
    'returns_are_distinct':any(m['return_message'] for m in allmessages) and any(not m['return_message'] for m in allmessages),
    'both_diagrams_have_alt':bool(s1b.frames) and bool(s2b.frames),
    'same_student_multiple_nonoverlapping_rule_retained':'多条非重叠预约' in txt and '全局未结束预约总量' in txt,
    'overlap_formula_half_open_present':all(s in txt for s in ['[start,end)','existing.start < new.end','new.start < existing.end']),
    'transaction_lock_clock_defined':all(s in txt for s in ['User → Room → Seat','BEGIN IMMEDIATE','锁后实际']),
    'manual_school_source_unresolved':all(s in txt for s in ['人工核验','OPEN-003','PENDING','REJECTED','VERIFIED']),
    'no_evidence_images_in_audit':'不复制原始学号、姓名或证明影像' in txt,
    'audit_and_business_share_transaction':all('tx' in m['zh'] for m in allmessages if m['src']=='CMP-008' and m['dst']=='CMP-009'),
    'proposed_api_not_claimed_implemented':'拟定的设计契约' in txt and 'NOT_RUN' in txt,
    'four_embedded_figure_panels':len(rd.inline_shapes)==4,
    'two_drawio_scenario_tabs':len(ET.parse(DRAWIO).findall('diagram'))==2,
    'four_svg_and_png_pairs':all((FIG/(p.key+'.svg')).exists() and (FIG/(p.key+'.png')).exists() for p in PANELS),
    'all_figures_fit_landscape_page':all(p.c.height/2200*9.8 < 6.95 for p in PANELS),
    'source_files_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in FINGERPRINTS.items()),
    'no_headers_or_footers':not any(re.fullmatch(r'word/(header|footer)\d+\.xml',n) for n in names),
    'source_images_preserved':len(list((DATA/'sources').glob('classroom-*.jpg')))==4,
    'requirement_references_exist':all(k in reqids for k in ['SP-FR-007','SP-FR-008','SP-FR-009','SP-FR-004','SP-FR-022','SP-IF-002','SP-DR-001','SP-NFR-004']),
}
report={'checks':checks,'check_count':len(checks),'all_pass':all(checks.values()),'visual_review':'PENDING',
        'business_tests':'NOT_RUN','timestamp_utc':datetime.now(timezone.utc).isoformat(),'environment':'Local macOS; bundled Codex Python; document design only',
        'source_fingerprints':FINGERPRINTS,'docx_sha256':hashlib.sha256(DOCX.read_bytes()).hexdigest(),
        'figure_sizes':{p.key:[2200,p.c.height] for p in PANELS}}
(DATA/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'README.md').write_text(f'''# StudySpace 双场景时序图与说明
# StudySpace Диаграммы последовательности двух сценариев

SS-SEQ-01 · v1 · 2026-10-15 · DRAFT

交付文件 / Результат: [{STEM}.docx]({STEM}.docx)

图源 / Редактируемая схема: [{DRAWIO.name}]({DRAWIO.name})

US-002 核心单座位预约；US-004 风险校内审核。选择表保留课件四列两行，中俄在同一单元格内上下对应。
US-002 основное бронирование места; US-004 рискованная проверка вуза. Таблица имеет четыре колонки и две записи, китайский над русским.

每个场景的图为 A、B 两个连续部分。draw.io 有两个页签，SVG/PNG 在 diagrams/。文档中的接口与 revision 是候选设计。
Каждая схема состоит из двух последовательных частей А и Б; draw.io содержит две вкладки, SVG/PNG в diagrams/. API и revision — проектные контракты.

内容与来源 / Содержание и источники: data/content.json
验证记录 / Проверка: data/verification.json
业务测试 / Бизнес-тесты: NOT_RUN
OPEN-003 实际学校来源未闭合 / Реальный источник вуза не определён.
''',encoding='utf-8')
print(json.dumps({'docx':str(DOCX),'drawio':str(DRAWIO),'checks':len(checks),'all_pass':report['all_pass'],'failed':[k for k,v in checks.items() if not v],'figure_sizes':report['figure_sizes']},ensure_ascii=False))
if not report['all_pass']:raise SystemExit(1)
