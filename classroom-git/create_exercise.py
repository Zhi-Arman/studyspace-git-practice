#!/usr/bin/env python3
"""Create a local, self-contained three-branch exercise; never access a remote."""

import argparse
from pathlib import Path
import subprocess

BASE_MODULE = '''"""Standalone classroom tickets, unrelated to production booking rules."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Ticket:
    description: str
    status: str = "new"
'''

DESCRIPTION_FEATURE = '''

def validate_description(value: str) -> str:
    """Return stripped text containing 10 through 500 Unicode code points."""
    if not isinstance(value, str):
        raise TypeError("description must be a string")
    normalized = value.strip()
    if not 10 <= len(normalized) <= 500:
        raise ValueError("description must contain 10 to 500 characters")
    return normalized
'''

STATUS_FEATURE = '''

TRANSITIONS = {
    "new": frozenset({"in_progress"}),
    "in_progress": frozenset({"resolved"}),
    "resolved": frozenset({"in_progress", "closed"}),
    "closed": frozenset(),
}


def transition_ticket(ticket: Ticket, target: str) -> Ticket:
    """Return a new ticket for an allowed transition, preserving the input."""
    from dataclasses import replace

    if not isinstance(ticket, Ticket):
        raise TypeError("ticket must be a Ticket")
    if not isinstance(target, str):
        raise TypeError("target status must be a string")
    if ticket.status not in TRANSITIONS or target not in TRANSITIONS:
        raise ValueError("unknown status")
    if target not in TRANSITIONS[ticket.status]:
        raise ValueError("transition is not allowed")
    return replace(ticket, status=target)
'''

BASE_TESTS = '''import unittest
from exercise import Ticket


class TicketTests(unittest.TestCase):
    def test_default_status(self):
        self.assertEqual(Ticket("example description").status, "new")

    def test_description_preserved(self):
        self.assertEqual(Ticket("中文说明 Русский").description, "中文说明 Русский")
'''

DESCRIPTION_TESTS = '''import unittest
from exercise import validate_description


class DescriptionTests(unittest.TestCase):
    def test_boundaries(self):
        for length in (10, 500):
            with self.subTest(length=length):
                self.assertEqual(validate_description("x" * length), "x" * length)

    def test_invalid_lengths(self):
        for value in ("", " " * 20, "x" * 9, "x" * 501):
            with self.subTest(length=len(value)):
                with self.assertRaises(ValueError):
                    validate_description(value)

    def test_whitespace_is_trimmed_before_counting(self):
        self.assertEqual(validate_description("  " + "x" * 10 + "\\n"), "x" * 10)
        with self.assertRaises(ValueError):
            validate_description(" " + "x" * 9 + " ")

    def test_non_strings(self):
        for value in (None, 10, True, [], b"abcdefghij"):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    validate_description(value)

    def test_multilingual_text(self):
        for value in ("中" * 10, "Описание заявки"):
            self.assertEqual(validate_description(value), value)
'''

STATUS_TESTS = '''import unittest
from exercise import Ticket, transition_ticket


class StatusTests(unittest.TestCase):
    def test_allowed_transitions(self):
        for source, target in (("new", "in_progress"),
                               ("in_progress", "resolved"),
                               ("resolved", "in_progress"),
                               ("resolved", "closed")):
            with self.subTest(source=source, target=target):
                result = transition_ticket(Ticket("description", source), target)
                self.assertEqual(result.status, target)

    def test_all_other_known_pairs_rejected(self):
        allowed = {("new", "in_progress"), ("in_progress", "resolved"),
                   ("resolved", "in_progress"), ("resolved", "closed")}
        for source in ("new", "in_progress", "resolved", "closed"):
            for target in ("new", "in_progress", "resolved", "closed"):
                if (source, target) not in allowed:
                    with self.subTest(source=source, target=target):
                        with self.assertRaises(ValueError):
                            transition_ticket(Ticket("description", source), target)

    def test_unknown_status_rejected(self):
        for source, target in (("unknown", "new"), ("new", "unknown")):
            with self.assertRaises(ValueError):
                transition_ticket(Ticket("description", source), target)

    def test_original_preserved_on_success(self):
        original = Ticket("description")
        result = transition_ticket(original, "in_progress")
        self.assertEqual(original.status, "new")
        self.assertEqual(result.description, original.description)
        self.assertIsNot(result, original)

    def test_original_preserved_on_error(self):
        original = Ticket("description")
        with self.assertRaises(ValueError):
            transition_ticket(original, "closed")
        self.assertEqual(original.status, "new")

    def test_wrong_types_rejected(self):
        with self.assertRaises(TypeError):
            transition_ticket(None, "new")
        for target in (None, [], 10):
            with self.assertRaises(TypeError):
                transition_ticket(Ticket("description"), target)
'''

README = '''# 双人 Git PR 练习 / Упражнение Git PR

## 1 来源与范围 / Источник и область

中文：用户未提供老师脚本，本目录按用户授权自行编写，用于课堂图片的仓库准备与两个 PR。它不是老师原始代码，也不是 StudySpace 预约业务实现。沿用已有共享仓库，因此历史 PR 编号不重置；“PR 1/2”作为本练习顺序标签。

Русский: По разрешению пользователя подготовлен собственный пример вместо отсутствующего скрипта преподавателя. Это учебные заявки, а не реализация бронирования StudySpace. Используется существующий репозиторий; PR 1/2 обозначают порядок упражнения, номера GitHub сохраняются.

## 2 自定规则 / Правила примера

中文：Ticket 初始状态为 new。A 的分支添加描述校验：必须是字符串，去除首尾空白后长度为 10–500 个 Unicode 码点（包含边界）。B 的分支添加状态流转：new → in_progress → resolved → closed，允许 resolved → in_progress；其余跳转（含原地跳转）拒绝；成功返回新对象，不修改原工单。这些均为本练习自定规则，不声称来自老师。

Русский: Начальный статус Ticket — new. Ветка A проверяет строковое описание: после удаления пробелов по краям 10–500 кодовых точек Unicode включительно. Ветка B разрешает new → in_progress → resolved → closed и resolved → in_progress; остальные переходы, включая переход в тот же статус, отклоняются. Возвращается новый объект без изменения исходного. Это собственные учебные правила.

## 3 运行与分支 / Запуск и ветки

中文：Python 3.10+，不需要第三方依赖。在 classroom-git 目录运行 `python3 -m unittest discover -s tests -v`。main 含公共基础；两个 feature 分支分别只添加对应功能与测试。

Русский: Python 3.10+, без сторонних зависимостей. Из classroom-git запустите `python3 -m unittest discover -s tests -v`. main содержит основу, каждая feature-ветка добавляет свою функцию и тесты.

```text
main
feature/description-validator -> main  (A: Zhi-Arman)
feature/status-transitions -> main     (B: like577)
```

中文：`python3 classroom-git/create_exercise.py /绝对路径/新目录` 可重新生成一个恰含上述三个分支的独立本地仓库。目标必须不存在。脚本不联网、不推送、不修改现有仓库，生成提交使用明确标注的自动化身份，不冒充学生。

Русский: `python3 classroom-git/create_exercise.py /absolute/path/new-directory` создаёт отдельный локальный репозиторий ровно с тремя ветками. Целевой каталог не должен существовать. Скрипт не использует сеть и не изменяет существующий репозиторий; коммиты имеют явно автоматизированную подпись.

## 4 PR 描述 / Описания PR

中文：A 使用根目录 pr-descriptions/description-validator.md；B 使用 pr-descriptions/status-transitions.md。短描述是故意薄弱的练习材料，暂不补写测试与设计细节。创建两个 PR 后保持打开，图片本阶段没有要求合并。当前功能提交由所有者自动准备，不能证明 B 本人编码；B 应用本人账号创建自己的 PR。吕嘉伟的正式课程编号为 D，GitHub 账号为 lvjiaw。双人练习 A/B 是该练习的操作角色，不覆盖 DEC-019 的现行四人编号。

Русский: A использует pr-descriptions/description-validator.md, B — pr-descriptions/status-transitions.md. Краткие описания намеренно неполные. Оба PR остаются открытыми: на фото слияние не требуется. Код автоматически подготовлен владельцем, что не доказывает личное программирование B; свой PR B создаёт из собственного аккаунта. 吕嘉伟 — участник D, аккаунт lvjiaw. Роли A/B парного упражнения не заменяют именные роли четырёх участников DEC-019.

中文：账号操作提示见 PARTICIPANTS.md。邀请接受、克隆、创建 PR 与正式课程验收分别核验，不互相替代。

Русский: Инструкции аккаунтов находятся в PARTICIPANTS.md. Принятие приглашения, клонирование, создание PR и учебная приёмка проверяются отдельно.
'''

PARTICIPANTS = '''# 账号 Bot 操作提示 / Инструкции для ботов участников

中文：将对应代码块交给该成员本人电脑上的 Bot。已授权的范围仅为本仓库；本人登录如需交互，由本人完成。不输出凭据，不覆盖目录，不强推或删除分支，不合并 PR。

Русский: Передайте соответствующий блок боту на компьютере участника. Разрешён только указанный репозиторий; интерактивный вход выполняет сам участник. Не раскрывать секреты, не перезаписывать каталоги, не применять force push, не удалять ветки и не сливать PR.

## B 曹浩然：like577 / B

```text
请以我的 GitHub 账号 like577 完成仓库准备练习的 B 步骤：
仓库为 Zhi-Arman/studyspace-git-practice。
先用 gh api user --jq .login 确认账号为 like577；不符则提示本人切换登录，不使用别人的凭据。
如仍有本仓库协作邀请，核对仓库后接受；若已接受则继续。
在合适的课程目录克隆仓库；如已有该仓库则先检查状态，不覆盖目录或丢弃修改。
获取远程分支（git fetch origin，不加 --prune），检查工作区干净后切换到 feature/status-transitions，跟踪 origin/feature/status-transitions。
已有该分支时检查本地与远程差异；不 reset --hard，不强制覆盖，不改写历史。
进入 classroom-git，运行 python3 -m unittest discover -s tests -v（Windows 可按实际 Python 命令调整）。
回到仓库根目录，用本人账号创建 feature/status-transitions -> main 的 PR；标题为 feat: add ticket status transitions。
正文必须原样读取 pr-descriptions/status-transitions.md，保持老师图片要求的故意薄弱初始描述。
可用命令：gh pr create --repo Zhi-Arman/studyspace-git-practice --base main --head feature/status-transitions --title "feat: add ticket status transitions" --body-file pr-descriptions/status-transitions.md
先查询是否已有同来源与目标分支的 PR；若作者为 like577 则返回现有链接，避免重复；若作者不是本人则报告事实，不冒称本人创建。
不要合并任何 PR；代码已由仓库所有者准备，不要把现有代码提交声称为本人编写。
最后回传：登录用户名、接受邀请结果、仓库绝对路径、当前分支、远程地址、工作区状态、测试真实结果、PR 链接和实际作者。
```

## D 吕嘉伟（项目经理）：lvjiaw / D, менеджер проекта

```text
我是成员 D 吕嘉伟，请以我的 GitHub 账号 lvjiaw 检查 Zhi-Arman/studyspace-git-practice 的访问权限并克隆仓库；已接受邀请时直接继续。
先确认 GitHub 登录账号确实为 lvjiaw；若需要本人登录，提示我操作，不输出凭据。
打开 https://github.com/Zhi-Arman/studyspace-git-practice/invitations 并核对后接受。
也可用 gh api user/repository_invitations 查询邀请，核对 full_name 后仅接受本仓库的邀请。
在合适的课程目录执行 git clone https://github.com/Zhi-Arman/studyspace-git-practice.git；已有目录则先检查，不覆盖或删除。
检查 git remote -v、git branch --show-current、git status --short --branch。
回传：登录账号、邀请是否接受、仓库绝对路径、当前分支和工作区状态。
仅接受邀请并克隆，不修改文件、不推送、不创建或合并 PR。
```
'''

BASE_FILES = {
    "classroom-git/exercise.py": BASE_MODULE,
    "classroom-git/tests/test_ticket.py": BASE_TESTS,
    "classroom-git/README.md": README,
    "classroom-git/PARTICIPANTS.md": PARTICIPANTS,
    "classroom-git/.gitignore": "__pycache__/\n*.py[cod]\n",
    "pr-descriptions/description-validator.md": "Add description validation.\n",
    "pr-descriptions/status-transitions.md": "Update ticket status handling.\n",
}

FEATURES = {
    "feature/description-validator": (
        DESCRIPTION_FEATURE, "test_description.py", DESCRIPTION_TESTS,
        "feat: validate classroom ticket descriptions",
    ),
    "feature/status-transitions": (
        STATUS_FEATURE, "test_status.py", STATUS_TESTS,
        "feat: enforce classroom ticket status transitions",
    ),
}


def git(destination, *args):
    return subprocess.run(
        ["git", "-C", str(destination), *args], check=True,
        text=True, capture_output=True,
    ).stdout.strip()


def write_base(destination):
    for name, content in BASE_FILES.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise FileExistsError(target)
        target.write_text(content, encoding="utf-8")
    script = destination / "classroom-git/create_exercise.py"
    if script.exists():
        raise FileExistsError(script)
    script.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")


def write_feature(destination, branch):
    feature, test_name, tests, _ = FEATURES[branch]
    (destination / "classroom-git/exercise.py").write_text(
        BASE_MODULE + feature, encoding="utf-8",
    )
    (destination / "classroom-git/tests" / test_name).write_text(tests, encoding="utf-8")


def commit(destination, message):
    git(destination, "add", "--all")
    git(destination, "-c", "user.name=Classroom exercise generator",
        "-c", "user.email=exercise-generator@example.invalid", "commit", "-m", message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    destination = args.destination.expanduser().resolve()
    if destination.exists():
        parser.error("destination already exists; refusing to overwrite")
    destination.mkdir(parents=True)
    git(destination, "init", "--initial-branch=main")
    write_base(destination)
    commit(destination, "chore: initialize self-authored classroom Git exercise")
    for branch, (_, _, _, message) in FEATURES.items():
        git(destination, "switch", "-c", branch, "main")
        write_feature(destination, branch)
        commit(destination, message)
    git(destination, "switch", "main")
    print(destination)
    print(git(destination, "branch", "--format=%(refname:short)"))


if __name__ == "__main__":
    main()
