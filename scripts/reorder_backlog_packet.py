"""Apply the requested three-document order and complete classroom task 3."""

import hashlib
import json
import shutil
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "coursework/2026-10-14-product-backlog-v1"
DATA = OUT / "data"
PACKET = DATA / "backlog-v1.json"
p = json.loads(PACKET.read_text())
refresh = "--refresh-task3" in sys.argv
if p.get("layout_version") == 2 and not refresh:
    raise SystemExit(
        "Three-document layout already exists; inspect current files before changing it."
    )
old = [x["path"] for x in p["documents"]]
new = [
    "01_StudySpace_用户画像_中俄双语_v1.docx",
    "02_StudySpace_用户故事地图与版本计划_中俄双语_v1.docx",
    "03_StudySpace_用户故事待办表_中俄双语_v1.docx",
]
assert (len(old) == 4 or refresh) and all((OUT / f).is_file() for f in old)
assert refresh or not any((OUT / f).exists() for f in new)
qa = OUT / "qa"
if qa.exists():
    assert not qa.is_symlink()
    assert all(
        not f.is_symlink() and f.suffix in [".png", ".pdf"] for f in qa.rglob("*") if f.is_file()
    )


def sha(f):
    return hashlib.sha256(f.read_bytes()).hexdigest()


preserved = (
    p["preserved_files"]
    if refresh
    else [dict(old=old[i], new=new[j], sha256=sha(OUT / old[i])) for j, i in [(0, 1), (1, 2)]]
)
retired = (
    p["retired_documents"]
    if refresh
    else [
        dict(
            id=p["documents"][i]["id"],
            path=old[i],
            sha256=sha(OUT / old[i]),
            reason="User requested deletion on 2026-10-14",
        )
        for i in [0, 3]
    ]
)
items = {x["id"]: x for x in p["items"]}
epics = {x["id"]: x for x in p["epics"]}
done = {
    "US-001": {
        "zh-CN": "给定位置、日期和时段，系统返回符合条件的启用且空闲的座位，并排除停用资源与占用区间。",
        "ru-RU": "Для заданных расположения, даты и интервала система возвращает подходящие активные свободные места, исключая отключённые ресурсы и занятые интервалы.",
    },
    "US-002": {
        "zh-CN": "合法请求仅创建一条单座位预约并返回编号，拒绝同学生或同座位重叠，同时允许相邻时段及多条非重叠预约。",
        "ru-RU": "Допустимая заявка создаёт одну запись одного места с ID, отклоняет пересечения студента или места и допускает соседние интервалы и несколько непересекающихся записей.",
    },
    "US-003": {
        "zh-CN": "学生可在开始前取消本人预约并释放对应时段，重复取消不重复计数，其他预约保持不变。",
        "ru-RU": "Студент до начала отменяет свою запись и освобождает интервал, повторная отмена не увеличивает счётчик, а остальные записи сохраняются.",
    },
    "US-004": {
        "zh-CN": "管理员依据可信学校来源保存审核人、时间、决定和引用，仅启用且已核验的学生可预约，停用或身份变更原子取消未结束预约。",
        "ru-RU": "Администратор по доверенному источнику вуза сохраняет автора, время, решение и ссылку, допускает только активного подтверждённого студента и атомарно отменяет незавершённые записи при отключении или смене идентификаторов.",
    },
    "US-005": {
        "zh-CN": "管理员维护房间、座位及开放例外后查询使用新配置，停用或缩减开放原子取消受影响未结束预约，重新启用不恢复旧预约。",
        "ru-RU": "Поиск использует новые помещения, места и исключения часов, отключение или сокращение часов атомарно отменяет затронутые незавершённые записи, а включение не восстанавливает прежние записи.",
    },
    "US-006": {
        "zh-CN": "学生仅见本人记录，管理员按权限查询的记录及创建、取消、未结束三项统计与同一业务日期和 as_of 快照一致。",
        "ru-RU": "Студент видит только своё, а доступные администратору записи и числа созданных, отменённых и незавершённых бронирований совпадают для одной деловой даты и снимка as_of.",
    },
}
core = [items[f"US-{i:03}"] for i in range(1, 7)]
records = [
    dict(
        id=x["id"],
        story=x["story"],
        epic_id=x["epic_id"],
        epic=epics[x["epic_id"]]["title"],
        requirement_ids=x["requirement_ids"],
        done=done[x["id"]],
        release=x["release"],
    )
    for x in core
]

doc = Document()
sec = doc.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width = Cm(29.7)
sec.page_height = Cm(21)
sec.top_margin = Cm(1.2)
sec.bottom_margin = Cm(1.2)
sec.left_margin = Cm(1.6)
sec.right_margin = Cm(1.6)
sec.footer_distance = Cm(0.5)
for n in ["Normal", "Title", "Subtitle", "Heading 1", "Heading 2"]:
    style = doc.styles[n]
    style.font.name = "Arial"
    style.font.color.rgb = RGBColor(0, 0, 0)
    fonts = OxmlElement("w:rFonts")
    fonts.set(qn("w:ascii"), "Arial")
    fonts.set(qn("w:hAnsi"), "Arial")
    fonts.set(qn("w:eastAsia"), "PingFang SC")
    style.element.get_or_add_rPr().append(fonts)
    snap = OxmlElement("w:snapToGrid")
    snap.set(qn("w:val"), "0")
    style.element.get_or_add_pPr().append(snap)
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.space_after = Pt(4)
for e in doc.styles.element.xpath(".//w:pBdr"):
    e.getparent().remove(e)
doc.styles["Normal"].font.size = Pt(10)
doc.styles["Normal"].paragraph_format.line_spacing = Pt(13)
doc.styles["Title"].font.size = Pt(20)
doc.styles["Title"].paragraph_format.line_spacing = Pt(25)
doc.styles["Subtitle"].font.size = Pt(12)
doc.styles["Subtitle"].paragraph_format.line_spacing = Pt(16)
doc.styles["Heading 1"].font.size = Pt(14)
doc.styles["Heading 1"].paragraph_format.space_before = Pt(5)
lines = []


def para(s, style=None, size=None):
    a = doc.add_paragraph(s, style)
    lines.append(s)
    if size:
        for r in a.runs:
            r.font.size = Pt(size)
        a.paragraph_format.line_spacing = Pt(size * 1.35)
    return a


def table(lang):
    headers = (
        ["ID", "用户故事", "史诗", "需求 ID", "如何判断完成（一句话）"]
        if lang == "zh-CN"
        else [
            "ID",
            "История",
            "Эпик",
            "ID требований",
            "Как узнаем что готово\nОдна фраза",
        ]
    )
    widths = [1.7, 8.5, 4.0, 5.5, 6.8]
    t = doc.add_table(rows=1, cols=5)
    t.autofit = False
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, w in zip(t.columns, widths, strict=False):
        c.width = Cm(w)
    for c, s in zip(t.rows[0].cells, headers, strict=False):
        c.text = s
    for x in records:
        row = t.add_row().cells
        reqtext = "\n".join(
            ", ".join(x["requirement_ids"][i : i + 2])
            for i in range(0, len(x["requirement_ids"]), 2)
        )
        for c, s in zip(
            row,
            [
                x["id"],
                x["story"][lang],
                x["epic_id"] + "\n" + x["epic"][lang],
                reqtext,
                x["done"][lang],
            ],
            strict=False,
        ):
            c.text = s
    for ri, row in enumerate(t.rows):
        trpr = row._tr.get_or_add_trPr()
        trpr.append(OxmlElement("w:cantSplit"))
        if ri == 0:
            trpr.append(OxmlElement("w:tblHeader"))
        for ci, c in enumerate(row.cells):
            c.width = Cm(widths[ci])
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            props = c._tc.get_or_add_tcPr()
            mar = OxmlElement("w:tcMar")
            for side in ["top", "bottom", "left", "right"]:
                e = OxmlElement("w:" + side)
                e.set(qn("w:w"), "60" if side in ["top", "bottom"] else "85")
                e.set(qn("w:type"), "dxa")
                mar.append(e)
            props.append(mar)
            borders = OxmlElement("w:tcBorders")
            for side in ["top", "bottom", "left", "right"]:
                e = OxmlElement("w:" + side)
                e.set(qn("w:val"), "single")
                e.set(qn("w:sz"), "4")
                e.set(qn("w:color"), "D9D9D9")
                borders.append(e)
            props.append(borders)
            sh = OxmlElement("w:shd")
            sh.set(
                qn("w:fill"),
                "DFE9F2" if ri == 0 else ("F5F7FA" if ri % 2 == 0 else "FFFFFF"),
            )
            props.append(sh)
            for a in c.paragraphs:
                a.paragraph_format.space_before = Pt(1)
                a.paragraph_format.space_after = Pt(1)
                a.paragraph_format.line_spacing = Pt(12)
                if ci == 0:
                    a.alignment = WD_ALIGN_PARAGRAPH.CENTER
                snap = OxmlElement("w:snapToGrid")
                snap.set(qn("w:val"), "0")
                a._p.get_or_add_pPr().append(snap)
                for r in a.runs:
                    r.font.size = Pt(9)
                    r.font.bold = ri == 0
    lines.append("| " + " | ".join(headers) + " |")
    for x in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    x["id"],
                    x["story"][lang],
                    x["epic_id"] + " " + x["epic"][lang],
                    ", ".join(x["requirement_ids"]),
                    x["done"][lang],
                ]
            )
            + " |"
        )


doc.core_properties.title = "StudySpace 用户故事待办表 Бэклог пользовательских историй"
doc.core_properties.author = "StudySpace"
para("StudySpace 用户故事待办表", "Title")
para("StudySpace Бэклог пользовательских историй", "Subtitle")
para(
    "排序 03 / Порядок 03  |  Doc-ID SS-PB-05  |  Version v1  |  2026-10-14  |  DRAFT",
    size=9,
)
para("任务 3 编写产品待办列表", "Heading 1")
para(
    "按课堂五列模板填写六条核心故事，沿用 US-001 至 US-006 和既有需求 ID；最后一列是计划验收标准，业务测试仍为 NOT_RUN。"
)
table("zh-CN")
para(
    "需求 ID 使用课堂 v0.2 的 SP 命名空间；这些核心故事均属于 MVP，完整版本范围见第 2 份故事地图文档，US-003 的管理员取消补充仍由 US-010 承接。",
    size=8.5,
)
para(
    "来源 / Источники  requirements-practice.json v0.2  backlog-v1.json  DEC-016  OPEN-003",
    size=8,
)
para(
    "课件图片 / Изображение  codex-clipboard-99e96d30-1318-4139-a58d-3ea61c4b2b35.jpg",
    size=8,
)
h = para("Задание 3 Написание бэклога", "Heading 1")
h.paragraph_format.page_break_before = True
para(
    "По пяти колонкам слайда заполнены шесть основных историй с прежними ID US-001…US-006 и ID требований; последняя колонка задаёт плановую приёмку, бизнес-тесты остаются NOT_RUN."
)
table("ru-RU")
para(
    "ID требований используют пространство SP учебной версии v0.2; основные истории относятся к MVP, полный объём выпусков приведён в документе 2 с картой историй, административное дополнение US-003 по-прежнему покрывает US-010.",
    size=8.5,
)
footer = sec.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = footer.add_run("StudySpace  03  |  ")
r.font.size = Pt(8)
f = OxmlElement("w:fldSimple")
f.set(qn("w:instr"), "PAGE")
footer._p.append(f)
doc.save(OUT / new[2])
(OUT / new[2]).with_suffix(".md").write_text("\n\n".join(lines))
if refresh:
    print("Updated task 3 document: " + str(OUT / new[2]))
    raise SystemExit(0)

# Retain the actual current contents, including any edits made after generation.
for x in preserved:
    (OUT / x["old"]).rename(OUT / x["new"])
    oldmd = (OUT / x["old"]).with_suffix(".md")
    if oldmd.exists():
        oldmd.rename((OUT / x["new"]).with_suffix(".md"))
    assert sha(OUT / x["new"]) == x["sha256"]
for x in retired:
    (OUT / x["path"]).unlink()
    md = (OUT / x["path"]).with_suffix(".md")
    if md.exists():
        md.unlink()
# Superseded render copies also contain deleted documents; regenerate current QA.
if qa.exists():
    shutil.rmtree(qa)
qa.mkdir()
before = p["documents"]
p["documents"] = [
    dict(before[1], path=new[0], order=1),
    dict(before[2], path=new[1], order=2),
    dict(
        id="SS-PB-05",
        path=new[2],
        order=3,
        version="v1",
        status="DRAFT",
        languages=["zh-CN", "ru-RU"],
    ),
]
p.update(
    layout_version=2,
    retired_documents=retired,
    preserved_files=preserved,
    classroom_task3=records,
)
PACKET.write_text(json.dumps(p, ensure_ascii=False, indent=2))
(OUT / "manifest.txt").write_text("\n".join(new) + "\n")
(OUT / "README.md").write_text(
    "# StudySpace 课堂材料 / Учебные материалы\n\n2026-10-14 · v1 · DRAFT\n\n"
    + "\n".join(f"{i}. [{name}]({name})" for i, name in enumerate(new, 1))
    + "\n\n1 用户画像 / Профили пользователей\n2 用户故事地图及 MVP 与后续版本 / Карта историй и выпуски\n3 任务 3 的五列表格，六条核心用户故事 / Пять колонок задания 3 и шесть основных историй\n\n文档排序使用文件名前缀；保留原文档 ID、故事 ID 和需求 ID。第 1、2 份原内容保持不变。最后一列是计划验收标准，业务测试 NOT_RUN。\nПорядок задаётся префиксом имени файла; сохранены ID документов, историй и требований. Содержимое документов 1 и 2 сохранено. Последняя колонка — плановая приёмка, бизнес-тесты NOT_RUN.\n\n原产品待办与需求对应文档和综合说明已按用户要求删除；当前仅交付上述三份文档。\nПрежние документы бэклога и общего описания удалены по запросу; передаются только эти три документа.\n"
)
(DATA / "verification.json").write_text(
    json.dumps(dict(state="PENDING", date="2026-10-14", layout_version=2), indent=2)
)
print(
    json.dumps(
        dict(
            deleted=[x["path"] for x in retired],
            files=new,
            retained_content_unchanged=True,
            core_stories=6,
        ),
        ensure_ascii=False,
        indent=2,
    )
)
