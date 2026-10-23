"""Capture real runs of the separately authorized classroom demonstration."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import difflib
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEMO, DATA = ROOT / "demo", ROOT / "data"
DATA.mkdir(exist_ok=True)
MODE = sys.argv[1]
manifest_path = DATA / "execution.json"
if MODE == "before":
    before = DATA / "before"
    before.mkdir(exist_ok=True)
    shutil.copy2(DEMO / "validator.py", before / "validator.py")
    shutil.copy2(DEMO / "tests/test_validator.py", before / "test_validator.py")
    manifest = {
        "scope": "INDEPENDENT_CLASSROOM_DEMONSTRATOR",
        "authorization": "用独立教学示例实际运行测试",
        "python": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "timezone": "Asia/Shanghai",
        "cwd": str(DEMO),
        "original_teacher_code_available": False,
        "original_system_tests": "NOT_RUN",
        "studyspace_business_tests": "NOT_RUN",
        "runs": [],
    }
else:
    manifest = json.loads(manifest_path.read_text())

env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def run(label, args, expected_code, expected_count):
    started = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    result = subprocess.run([sys.executable, "-m", "unittest", *args], cwd=DEMO,
                            env=env, capture_output=True, text=True)
    output = result.stdout + result.stderr
    log = DATA / (label + ".log")
    log.write_text(output)
    match = re.search(r"Ran (\d+) tests? in", output)
    count = int(match.group(1)) if match else 0
    failure_match = re.search(r"failures=(\d+)", output)
    failures = int(failure_match.group(1)) if failure_match else 0
    assert result.returncode == expected_code, output
    assert count == expected_count, output
    if expected_code:
        assert failures == 1 and "FAIL: test_tc_cf_05_rejects_1001_characters" in output, output
    else:
        assert output.rstrip().endswith("OK"), output
    item = {
        "label": label, "started_at": started,
        "command": [sys.executable, "-m", "unittest", *args],
        "exit_code": result.returncode, "tests_run": count,
        "failures": failures, "passed": count - failures,
        "log": str(log), "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
    }
    manifest["runs"].append(item)
    print(json.dumps(item, ensure_ascii=False))


def behavior(label):
    script = """import json
from validator import Validate
result = []
for size in (999, 1000, 1001, 1002):
    v = Validate('a' * size)
    result.append({'length': size, 'accepted': v.is_valid, 'error': v.error_code})
print(json.dumps(result))
"""
    r = subprocess.run([sys.executable, "-c", script], cwd=DEMO, env=env, capture_output=True, text=True, check=True)
    values = json.loads(r.stdout)
    manifest[label] = values
    return values


if MODE == "before":
    run("before-full-suite", ["discover", "-s", "tests", "-v"], 1, 18)
    values = behavior("before_behavior")
    assert values[2]["accepted"] is True
elif MODE == "after":
    assert (DATA / "before/test_validator.py").read_bytes() == (DEMO / "tests/test_validator.py").read_bytes()
    run("after-regression", ["tests.test_validator.ValidateTests.test_tc_cf_05_rejects_1001_characters", "-v"], 0, 1)
    run("after-full-suite", ["discover", "-s", "tests", "-v"], 0, 18)
    values = behavior("after_behavior")
    assert values[2]["accepted"] is False
    before_src = (DATA / "before/validator.py").read_text()
    after_src = (DEMO / "validator.py").read_text()
    (DATA / "validator.patch").write_text("".join(difflib.unified_diff(before_src.splitlines(True), after_src.splitlines(True), fromfile="before/validator.py", tofile="demo/validator.py")))
    manifest["tests_unchanged_between_runs"] = True
    manifest["before_source_sha256"] = hashlib.sha256(before_src.encode()).hexdigest()
    manifest["after_source_sha256"] = hashlib.sha256(after_src.encode()).hexdigest()
    manifest["test_source_sha256"] = hashlib.sha256((DEMO / "tests/test_validator.py").read_bytes()).hexdigest()
    manifest["demonstrator_confirmation"] = "PASS"
    manifest["original_system_confirmation"] = "NOT_RUN"
else:
    raise ValueError(MODE)

manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
