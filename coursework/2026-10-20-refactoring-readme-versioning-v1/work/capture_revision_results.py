"""Capture the existing employee tests and their actual returned values."""

import copy
import importlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "code"
records = []
for label, module in [("before", "employees_original"), ("after", "employees_refactored")]:
    env = os.environ.copy()
    env["EMPLOYEE_MODULE"] = module
    args = [sys.executable, "-m", "unittest", "-v", "test_employees.py"]
    result = subprocess.run(args, cwd=CODE, env=env, text=True, capture_output=True)
    output = result.stdout + result.stderr
    (ROOT / f"artifacts/employee-revision-{label}.log").write_text(output)
    assert result.returncode == 0 and "Ran 2 tests" in output and output.rstrip().endswith("OK"), output
    records.append({"module": module, "exit_code": result.returncode, "passed": 2, "total": 2})

sys.path.insert(0, str(CODE))
tests = importlib.import_module("test_employees")
original = importlib.import_module("employees_original")
refactored = importlib.import_module("employees_refactored")
fixture = tests.EmployeeFilterTests()
fixture.setUp()
employees = fixture.employees
before_input = copy.deepcopy(employees)
cases = []
for test_id, original_function, new_function, expected in [
    ("T1", original.f, refactored.employees_with_unused_vacation,
     ["Anna Ivanova", "Maria Volkova", "Anna Ivanova"]),
    ("T2", original.g, refactored.employees_with_sick_leave, ["Ivan Petrov"]),
]:
    old_result = original_function(employees, "IT")
    new_result = new_function(employees, "IT")
    assert old_result == new_result == expected
    cases.append({"id": test_id, "department": "IT", "expected": expected,
                  "original_actual": old_result, "refactored_actual": new_result, "status": "PASS"})
assert employees == before_input
data = {"date": "2026-10-20", "python": platform.python_version(), "platform": platform.system(),
        "test_runs": records, "cases": cases, "input_unchanged": True,
        "f_alias_preserved": refactored.f is refactored.employees_with_unused_vacation,
        "g_alias_preserved": refactored.g is refactored.employees_with_sick_leave}
(ROOT / "artifacts/employee-revision-results.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
print(json.dumps(data, ensure_ascii=False, indent=2))
