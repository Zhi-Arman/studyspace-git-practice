#!/usr/bin/env python3
"""Validate the proposed contract and its links to coursework; no business API is called."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qs

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate_spec

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/api/openapi.yaml"
COURSEWORK = ROOT / "coursework"
METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}


def load_coursework(folder: str) -> dict:
    return json.loads((COURSEWORK / folder / "data/content.json").read_text(encoding="utf-8"))


def validate_contract() -> dict:
    spec = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    validate_spec(spec)
    checks = 1

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        if not condition:
            raise ValueError(message)
        checks += 1

    def resolve(value: dict) -> dict:
        if "$ref" not in value:
            return value
        reference = value["$ref"]
        require(reference.startswith("#/"), f"Only local references allowed: {reference}")
        target = spec
        for part in reference[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        return target

    def schema_validator(schema: dict) -> Draft202012Validator:
        # components is retained as the resolution root for all local schema references.
        root_schema = {"components": spec["components"], **schema}
        return Draft202012Validator(root_schema, format_checker=FormatChecker())

    examples = 0

    def check_example(schema: dict, value: object, label: str) -> None:
        nonlocal examples
        errors = list(schema_validator(schema).iter_errors(value))
        require(not errors, f"{label}: {'; '.join(error.message for error in errors)}")
        examples += 1

    def visit(value: object) -> None:
        if isinstance(value, dict):
            if "$ref" in value:
                resolve(value)
            if "schema" in value:
                if "example" in value:
                    check_example(value["schema"], value["example"], "media/parameter example")
                for entry in value.get("examples", {}).values():
                    if "value" in entry:
                        check_example(value["schema"], entry["value"], "media example")
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(spec)
    schemas = spec["components"]["schemas"]
    for name, schema in schemas.items():
        check_example({"$ref": f"#/components/schemas/{name}"}, schema["example"], name)

    operations = {}
    for path, path_item in spec["paths"].items():
        for method, operation in path_item.items():
            if method in METHODS:
                require(operation["operationId"] not in operations, "Duplicate operationId")
                operations[operation["operationId"]] = (path, method, operation)
                require(operation["security"] == [{"bearerAuth": []}], "Missing security")
                for status, response in operation["responses"].items():
                    if status.startswith("4"):
                        schema = resolve(response)["content"]["application/json"]["schema"]
                        require(
                            schema == {"$ref": "#/components/schemas/Error"},
                            "Error drift",
                        )

    task1 = load_coursework("2026-10-16-endpoint-list-v1")
    expected_endpoints = {row["method_path"] for row in task1["rows"]}
    actual_endpoints = {f"{method.upper()} {path}" for path, method, _ in operations.values()}
    require(expected_endpoints == actual_endpoints, "Task 1 endpoint coverage differs")
    for row in task1["rows"]:
        operation = next(
            operation
            for path, method, operation in operations.values()
            if f"{method.upper()} {path}" == row["method_path"]
        )
        expected_ids = set(
            re.findall(
                r"(?:US|DEC|OPEN)-\d+|SP-(?:FR|NFR|IF|DR)-\d+",
                row["requirement_story"]["zh"],
            )
        )
        require(
            expected_ids <= set(operation["x-traceability"]),
            f"{row['method_path']}: requirement/story traceability drift",
        )
    task2 = load_coursework("2026-10-16-operation-summary-v1")
    for row in task2["rows"]:
        matching = [op for _, _, op in operations.values() if op["x-operation-id"] == row["id"]]
        require(len(matching) == 1, f"Missing/duplicate operation {row['id']}")
        statuses = set(re.findall(r"\b[1-5]\d{2}\b", row["success"]["zh"] + row["errors"]["zh"]))
        require(
            set(matching[0]["responses"]) == statuses,
            f"{row['id']}: Task 2 status drift",
        )
    task3 = load_coursework("2026-10-16-data-schemas-v1")
    require(set(schemas) == {row["schema"] for row in task3["rows"]}, "Task 3 schema drift")
    for row in task3["rows"]:
        schema = schemas[row["schema"]]
        require(schema["x-coursework-id"] == row["id"], "Task 3 schema ID drift")
        example = row["example"]
        if isinstance(example, str):
            example = {key: values[0] for key, values in parse_qs(example.lstrip("?")).items()}
        elif row["schema"] == "Error":
            example = example["zh"]
        require(example == schema["example"], f"{row['schema']}: Task 3 example drift")
        require(set(schema["required"]) == set(example), f"{row['schema']}: required drift")

    policy = json.loads((ROOT / "docs/data/project-decisions.json").read_text())["booking"]
    rules = spec["x-business-rules"]
    for contract_key, policy_key in (
        ("timezone", "timezone"),
        ("interval", "interval"),
        ("minimum-duration-minutes", "min_duration_minutes"),
        ("maximum-duration-hours", "max_duration_hours"),
        ("time-step-minutes", "time_granularity_minutes"),
    ):
        require(rules[contract_key] == policy[policy_key], f"Policy drift: {contract_key}")
    require(
        rules["advance-calendar-days"] == len(policy["booking_day_offsets"]),
        "Day drift",
    )
    require(
        rules["default-opening-hours"]
        == f"{policy['default_opening']['start']}-{policy['default_opening']['end']}",
        "Opening-hours drift",
    )

    # Check important rejection boundaries without claiming server-side business tests.
    invalid_examples = []
    booking = schemas["BookingCreateRequest"]["example"]
    for field, value in (
        ("seat_id", ""),
        ("seat_id", "x" * 129),
        ("start", "not-a-time"),
    ):
        invalid_examples.append(("BookingCreateRequest", {**booking, field: value}))
    invalid_examples.append(("BookingCreateRequest", {**booking, "user_id": "client-author"}))
    missing = copy.deepcopy(booking)
    del missing["end"]
    invalid_examples.append(("BookingCreateRequest", missing))
    review = schemas["IdentityReviewDecisionRequest"]["example"]
    invalid_examples.append(("IdentityReviewDecisionRequest", {**review, "decision": "PENDING"}))
    for name, example in invalid_examples:
        require(
            not schema_validator({"$ref": f"#/components/schemas/{name}"}).is_valid(example),
            f"{name}: invalid example accepted",
        )

    return {
        "contract": str(CONTRACT.relative_to(ROOT)),
        "sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
        "openapi": spec["openapi"],
        "operations": len(operations),
        "schemas": len(schemas),
        "validated_examples": examples,
        "rejection_examples": len(invalid_examples),
        "checks": checks,
        "result": "PASS",
        "business_tests": "NOT_RUN",
        "implementation_status": spec["x-implementation-status"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Optional static-validation JSON report")
    args = parser.parse_args()
    try:
        result = validate_contract()
    except (ValueError, KeyError, OSError) as exc:
        print(f"FAIL: {exc}")
        return 1
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("Static contract checks only; business API tests remain NOT_RUN.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
