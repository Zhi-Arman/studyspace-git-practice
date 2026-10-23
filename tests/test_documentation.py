"""Check the real document registry, including meaningful failure-path mutations."""

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "studyspace_check_docs", PROJECT_ROOT / "scripts/check_docs.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK_DOCS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_DOCS)


@pytest.fixture
def project_copy(tmp_path):
    shutil.copytree(PROJECT_ROOT / "docs", tmp_path / "docs")
    return tmp_path


def test_actual_bilingual_documentation_and_traceability():
    assert CHECK_DOCS.validate_project(PROJECT_ROOT) == []


def test_detects_divergent_russian_document_version(project_copy):
    manifest = json.loads((project_copy / "docs/manifest.json").read_text())
    path = project_copy / "docs" / manifest["entries"][0]["ru"]
    path.write_text(
        path.read_text().replace(f"| {manifest['entries'][0]['version']} |", "| 9.9.9 |", 1)
    )
    assert any("Version differs" in issue for issue in CHECK_DOCS.validate_project(project_copy))


def test_detects_missing_test_requirement_reference(project_copy):
    path = project_copy / "docs/data/test-cases.json"
    data = json.loads(path.read_text())
    data["test_cases"][0]["requirement_ids"] = ["FR-999"]
    path.write_text(json.dumps(data, ensure_ascii=False))
    assert any(
        "unknown requirement FR-999" in issue for issue in CHECK_DOCS.validate_project(project_copy)
    )


def test_does_not_allow_claiming_pass_without_evidence(project_copy):
    path = project_copy / "docs/data/test-cases.json"
    data = json.loads(path.read_text())
    data["test_cases"][0]["status"] = "PASS"
    data["test_cases"][0].pop("evidence", None)
    path.write_text(json.dumps(data, ensure_ascii=False))
    assert any(
        "must include evidence" in issue for issue in CHECK_DOCS.validate_project(project_copy)
    )


@pytest.mark.parametrize(
    ("status", "error"),
    [
        ("APPROVED", "must include approval evidence"),
        ("IMPLEMENTED", "must include implementation paths"),
        ("VERIFIED", "must have passing linked tests"),
    ],
)
def test_requirement_status_cannot_outpace_its_evidence(project_copy, status, error):
    path = project_copy / "docs/data/requirements.json"
    data = json.loads(path.read_text())
    data["requirements"][0]["status"] = status
    data["requirements"][0]["approval"] = None
    data["requirements"][0]["implementation"] = []
    path.write_text(json.dumps(data, ensure_ascii=False))
    assert any(error in issue for issue in CHECK_DOCS.validate_project(project_copy))


def test_detects_broken_nonfunctional_identifier_in_both_languages(project_copy):
    for language in ("zh-CN", "ru-RU"):
        path = project_copy / "docs" / language / "03_SRS_IEEE830.md"
        path.write_text(path.read_text().replace("NFR-002", "N FR-002"))
    assert any(
        "broken NFR identifier" in issue for issue in CHECK_DOCS.validate_project(project_copy)
    )


def test_detects_seat_mvp_regression(project_copy):
    path = project_copy / "docs/data/requirements.json"
    data = json.loads(path.read_text())
    next(item for item in data["requirements"] if item["id"] == "FR-017")["scope"] = "FUTURE"
    path.write_text(json.dumps(data, ensure_ascii=False))
    assert any("FR-017 must remain in MVP" in e for e in CHECK_DOCS.validate_project(project_copy))


def test_detects_stale_test_scope(project_copy):
    path = project_copy / "docs/data/test-cases.json"
    data = json.loads(path.read_text())
    next(item for item in data["test_cases"] if item["id"] == "TC-017")["scope"] = "FUTURE"
    path.write_text(json.dumps(data, ensure_ascii=False))
    assert any("scope differs" in issue for issue in CHECK_DOCS.validate_project(project_copy))


def test_rejects_old_global_booking_limit(project_copy):
    path = project_copy / "docs/data/project-decisions.json"
    data = json.loads(path.read_text())
    data["booking"]["max_active_reservations_per_student"] = 1
    path.write_text(json.dumps(data, ensure_ascii=False))
    assert any(
        "contradicts DEC-016" in issue for issue in CHECK_DOCS.validate_project(project_copy)
    )


def test_rejects_reverting_to_developer_main_roles(project_copy):
    path = project_copy / "docs/data/project-decisions.json"
    data = json.loads(path.read_text())
    data["team"][2]["role_code"] = "BACKEND_DEVELOPER"
    path.write_text(json.dumps(data, ensure_ascii=False))
    assert any("contradict DEC-017" in issue for issue in CHECK_DOCS.validate_project(project_copy))
