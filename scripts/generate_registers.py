#!/usr/bin/env python3
"""Regenerate only marked register/matrix blocks from bilingual JSON registries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- GENERATED:BEGIN -->"
END = "<!-- GENERATED:END -->"


def cell(value: object, language: str) -> str:
    if isinstance(value, dict):
        value = value.get(language, "")
    if isinstance(value, list):
        value = "; ".join(str(item) for item in value)
    return str(value or "—").replace("|", "\\|").replace("\n", "<br>")


def design_cell(requirement: dict, language: str) -> str:
    references = []
    for target in requirement.get("design", []):
        if isinstance(target, str):
            path, section = target, ""
        else:
            path = (
                target.get("ru_document", target.get("document", ""))
                if language == "ru-RU"
                else target.get("document", "")
            )
            path = path.replace("/zh-CN/", f"/{language}/")
            section = target.get("section", "")
        if path:
            name = Path(path).name
            references.append(f"[{name}]({name}) §{section}")
    return "; ".join(references) or "—"


def render(requirements: list[dict], cases: dict[str, dict], language: str, matrix: bool) -> str:
    zh = language == "zh-CN"
    missing = "待实现" if zh else "Не реализовано"
    if matrix:
        columns = (
            ["需求ID", "状态", "来源", "设计草稿", "实现", "计划测试用例", "测试状态"]
            if zh
            else [
                "ID требования",
                "Статус",
                "Источник",
                "Черновой проект",
                "Реализация",
                "Планируемые тест-кейсы",
                "Статус тестов",
            ]
        )
    else:
        columns = (
            [
                "ID",
                "类型",
                "范围",
                "状态",
                "标题",
                "描述",
                "验证方法",
                "设计草稿",
                "计划测试用例",
            ]
            if zh
            else [
                "ID",
                "Тип",
                "Область",
                "Статус",
                "Название",
                "Описание",
                "Метод проверки",
                "Черновой проект",
                "Планируемые тест-кейсы",
            ]
        )
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for item in requirements:
        case_ids = item.get("test_cases", [])
        if matrix:
            implementation = item.get("implementation", [])
            values = [
                item["id"],
                item["status"],
                cell(item.get("source"), language),
                design_cell(item, language),
                cell(implementation, language) if implementation else missing,
                cell(case_ids, language),
                "; ".join(
                    f"{case_id}: {cases.get(case_id, {}).get('status', 'UNKNOWN')}"
                    for case_id in case_ids
                ),
            ]
        else:
            values = [
                item["id"],
                item["type"],
                cell(item.get("scope", "MVP"), language),
                item["status"],
                cell(item["title"], language),
                cell(item["description"], language),
                cell(item["verification"], language),
                design_cell(item, language),
                cell(case_ids, language),
            ]
        lines.append("| " + " | ".join(str(value) for value in values) + " |")
    return "\n".join(lines)


def render_test_index(cases: dict[str, dict], language: str) -> str:
    columns = (
        ["TC", "需求ID", "范围", "状态", "标题"]
        if language == "zh-CN"
        else ["TC", "ID требования", "Область", "Статус", "Название"]
    )
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for item in cases.values():
        values = [
            item["id"],
            cell(item["requirement_ids"], language),
            item["scope"],
            item["status"],
            cell(item["title"], language),
        ]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def expected_documents(root: Path = ROOT) -> dict[Path, str]:
    requirements = json.loads((root / "docs/data/requirements.json").read_text(encoding="utf-8"))[
        "requirements"
    ]
    cases = {
        item["id"]: item
        for item in json.loads((root / "docs/data/test-cases.json").read_text(encoding="utf-8"))[
            "test_cases"
        ]
    }
    documents = {}
    for language in ("zh-CN", "ru-RU"):
        for filename, matrix in (
            ("14_Requirements_Register.md", False),
            ("07_Traceability_Matrix.md", True),
            ("06_Test_Cases.md", False),
        ):
            path = root / "docs" / language / filename
            original = path.read_text(encoding="utf-8")
            if (
                original.count(BEGIN) != 1
                or original.count(END) != 1
                or original.index(BEGIN) > original.index(END)
            ):
                raise ValueError(f"{path}: requires exactly one ordered generated block")
            start = original.index(BEGIN) + len(BEGIN)
            end = original.index(END)
            generated = (
                render_test_index(cases, language)
                if filename == "06_Test_Cases.md"
                else render(requirements, cases, language, matrix)
            )
            documents[path] = original[:start] + "\n" + generated + "\n" + original[end:]
    return documents


def check_generated(root: Path = ROOT) -> list[str]:
    try:
        return [
            f"{path.relative_to(root)}: generated register is stale"
            for path, expected in expected_documents(root).items()
            if path.read_text(encoding="utf-8") != expected
        ]
    except (OSError, ValueError, KeyError) as exc:
        return [f"register generation: {exc}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without writing files")
    options = parser.parse_args()
    if options.check:
        errors = check_generated()
        for error in errors:
            print(f"ERROR: {error}")
        if errors:
            return 1
        print("PASS: generated bilingual registers match JSON sources")
        return 0
    for path, content in expected_documents().items():
        path.write_text(content, encoding="utf-8")
        print(f"Updated {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
