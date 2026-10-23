#!/usr/bin/env python3
"""Check bilingual structure and traceability; this does not assess translation quality."""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {"zh-CN", "ru-RU"}
ID_PATTERN = re.compile(
    r"(?<![A-Za-z0-9-])(?:FR|NFR|BR|TC|RISK|OPEN|ADR|DEC)-\d{3,4}(?![A-Za-z0-9-])"
)
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*)(?:\.?\s|$)", re.MULTILINE)


def metadata(text: str, key: str) -> str | None:
    match = re.search(rf"^\|\s*{re.escape(key)}\s*\|\s*([^|]+?)\s*\|", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def numbered_sections(text: str) -> list[str]:
    return HEADING_PATTERN.findall(text)


def validate_project(root: Path = PROJECT_ROOT) -> list[str]:
    errors: list[str] = []
    docs = root / "docs"

    def read_json(relative: str) -> dict:
        try:
            value = json.loads((root / relative).read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise ValueError("top-level object required")
            return value
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
            return {}

    def bilingual(value: object, label: str) -> None:
        if not isinstance(value, dict) or set(value) != LANGUAGES:
            errors.append(f"{label}: expected zh-CN and ru-RU fields")
        elif any(not text for text in value.values()):
            errors.append(f"{label}: empty translation")

    manifest = read_json("docs/manifest.json")
    entries = manifest.get("entries", [])
    if not entries:
        errors.append("manifest: no document pairs")
    listed: set[Path] = set()
    document_ids: set[str] = set()
    for entry in entries:
        doc_id = entry.get("id", "<missing>")
        if doc_id in document_ids:
            errors.append(f"manifest: duplicate {doc_id}")
        document_ids.add(doc_id)
        texts = []
        for lang, key in (("zh-CN", "zh"), ("ru-RU", "ru")):
            path = docs / entry.get(key, "<missing>")
            if not path.resolve().is_relative_to(docs.resolve()):
                errors.append(f"{doc_id}: path outside docs")
                continue
            if path in listed:
                errors.append(f"{doc_id}: duplicate path {path.name}")
            listed.add(path)
            try:
                content = path.read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(f"{doc_id} {lang}: {exc}")
                continue
            texts.append(content)
            if re.search(r"(?<![A-Za-z])N\s+FR-\d{3}", content):
                errors.append(f"{doc_id} {lang}: broken NFR identifier contains whitespace")
            expected = {
                "Doc-ID": doc_id,
                "Version": entry.get("version"),
                "Status": entry.get("status"),
                "Updated": entry.get("updated", manifest.get("updated")),
                "Language": lang,
            }
            for key_name, value in expected.items():
                if metadata(content, key_name) != value:
                    errors.append(f"{doc_id} {lang}: {key_name} differs from manifest ({value})")
        if len(texts) == 2:
            if numbered_sections(texts[0]) != numbered_sections(texts[1]):
                errors.append(f"{doc_id}: section numbering differs between languages")
            if set(ID_PATTERN.findall(texts[0])) != set(ID_PATTERN.findall(texts[1])):
                errors.append(f"{doc_id}: stable identifier sets differ between languages")
            if entry.get("sections") and numbered_sections(texts[0]) != entry["sections"]:
                errors.append(f"{doc_id}: section numbering differs from manifest")
    for directory in (docs / "zh-CN", docs / "ru-RU", docs / "decisions"):
        for path in directory.rglob("*.md"):
            if path.name != "README.md" and path not in listed:
                errors.append(f"manifest: unregistered formal document {path.relative_to(docs)}")

    requirements = read_json("docs/data/requirements.json")
    cases = read_json("docs/data/test-cases.json")
    policy = read_json("docs/data/project-decisions.json")
    decision_ids = {item.get("id") for item in policy.get("decisions", [])}
    for decision in policy.get("decisions", []):
        for key in ("title", "description"):
            bilingual(decision.get(key), f"{decision.get('id')}.{key}")
        if decision.get("status") not in {
            "CONFIRMED",
            "DELEGATED",
            "PREFERENCE",
            "OPEN",
        }:
            errors.append(f"{decision.get('id')}: unknown decision status")
    if "DEC-016" in decision_ids:
        booking = policy.get("booking", {})
        if "max_active_reservations_per_student" in booking:
            errors.append("global active-reservation limit contradicts DEC-016")
        if booking.get("max_concurrent_reservations_per_student") != 1 or not booking.get(
            "allow_multiple_non_overlapping_reservations"
        ):
            errors.append("student interval policy contradicts DEC-016")
    if "DEC-017" in decision_ids:
        team = policy.get("team", [])
        roles = {item.get("role_code") for item in team}
        if len(team) != 4 or roles != {
            "ANALYST_TZ",
            "DOCUMENT_EDITOR",
            "TESTER",
            "PROJECT_MANAGER",
        }:
            errors.append("classroom roles contradict DEC-017")
    req_items = requirements.get("requirements", [])
    tc_items = cases.get("test_cases", [])
    if not req_items or not tc_items:
        errors.append("requirements/test_cases: nonempty registries required")
    req_map: dict[str, dict] = {}
    tc_map: dict[str, dict] = {}
    for item in req_items:
        req_id = item.get("id", "")
        kind = item.get("type")
        if kind not in {"FR", "NFR", "BR"} or not re.fullmatch(rf"{kind}-\d{{3}}", req_id):
            errors.append(f"requirement: invalid ID/type {req_id}")
        if req_id in req_map:
            errors.append(f"requirement: duplicate {req_id}")
        req_map[req_id] = item
        for decision_id in item.get("decision_ids", []):
            if decision_id not in decision_ids:
                errors.append(f"{req_id}: unknown decision {decision_id}")
        for key in ("title", "description", "verification"):
            bilingual(item.get(key), f"{req_id}.{key}")
        if item.get("status") not in {
            "PROPOSED",
            "APPROVED",
            "IMPLEMENTED",
            "VERIFIED",
            "RETIRED",
        }:
            errors.append(f"{req_id}: unknown status")
        if item.get("status") in {"APPROVED", "IMPLEMENTED", "VERIFIED"}:
            approval = item.get("approval") or {}
            if not isinstance(approval, dict) or not all(
                approval.get(key) for key in ("approved_by", "approved_at", "evidence")
            ):
                errors.append(f"{req_id}: approved requirement must include approval evidence")
        if item.get("status") in {"IMPLEMENTED", "VERIFIED"} and not item.get("implementation"):
            errors.append(f"{req_id}: implemented requirement must include implementation paths")
        for implementation in item.get("implementation", []):
            path_text = (
                implementation
                if isinstance(implementation, str)
                else implementation.get("path", "")
            )
            if not path_text or not (root / path_text).is_file():
                errors.append(f"{req_id}: implementation does not exist: {path_text}")
        if not item.get("design"):
            errors.append(f"{req_id}: missing proposed design reference")
        for target in item.get("design", []):
            path_text = target if isinstance(target, str) else target.get("document", "")
            if not (root / path_text).is_file():
                errors.append(f"{req_id}: missing design document {path_text}")
            elif isinstance(target, dict) and target.get("section"):
                text = (root / path_text).read_text(encoding="utf-8")
                if target["section"] not in numbered_sections(text):
                    errors.append(f"{req_id}: design section {target['section']} does not exist")
    for item in tc_items:
        tc_id = item.get("id", "")
        if not re.fullmatch(r"TC-\d{3}", tc_id):
            errors.append(f"test case: invalid ID {tc_id}")
        if tc_id in tc_map:
            errors.append(f"test case: duplicate {tc_id}")
        tc_map[tc_id] = item
        for key in ("title", "preconditions", "steps", "expected_result"):
            bilingual(item.get(key), f"{tc_id}.{key}")
        if item.get("status") not in {"NOT_RUN", "PASS", "FAIL", "BLOCKED", "RETIRED"}:
            errors.append(f"{tc_id}: unknown status")
        if item.get("status") in {"PASS", "FAIL"} and not item.get("evidence"):
            errors.append(f"{tc_id}: executed test must include evidence")
        if not item.get("requirement_ids"):
            errors.append(f"{tc_id}: no requirement references")
        for req_id in item.get("requirement_ids", []):
            if req_id not in req_map:
                errors.append(f"{tc_id}: unknown requirement {req_id}")
            elif tc_id not in req_map[req_id].get("test_cases", []):
                errors.append(f"{tc_id}/{req_id}: reverse reference missing")
            elif len(item.get("requirement_ids", [])) == 1:
                if item.get("scope") != req_map[req_id].get("scope"):
                    errors.append(f"{tc_id}/{req_id}: scope differs")
    for req_id, item in req_map.items():
        if not item.get("test_cases"):
            errors.append(f"{req_id}: no planned verification case")
        for tc_id in item.get("test_cases", []):
            if tc_id not in tc_map:
                errors.append(f"{req_id}: unknown test case {tc_id}")
            elif req_id not in tc_map[tc_id].get("requirement_ids", []):
                errors.append(f"{req_id}/{tc_id}: reverse reference missing")
        if item.get("status") == "VERIFIED" and any(
            tc_map.get(tc_id, {}).get("status") != "PASS" for tc_id in item.get("test_cases", [])
        ):
            errors.append(f"{req_id}: verified requirement must have passing linked tests")
    if policy.get("booking", {}).get("unit") == "SEAT":
        if req_map.get("FR-017", {}).get("scope") != "MVP":
            errors.append("seat decision: FR-017 must remain in MVP")
    for label, register in (
        ("requirements", requirements),
        ("test_cases", cases),
        ("project_decisions", policy),
    ):
        if register.get("version") != manifest.get("version"):
            errors.append(f"{label}: version differs from manifest")
    return errors


def main() -> int:
    errors = validate_project()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAIL: {len(errors)} documentation consistency issue(s)")
        return 1
    print("PASS: bilingual document metadata, section/ID parity and requirement/test references")
    print("Structural validation only; translation and requirements approval need human review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
