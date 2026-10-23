"""Independent classroom demonstrator of description validation.

This initial version deliberately contains the exercise's upper-bound error.
"""

from dataclasses import dataclass


MAX_DESCRIPTION_LENGTH = 1000


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    normalized_description: str | None = None
    error_code: str | None = None


def Validate(description: object) -> ValidationResult:
    """Validate 1..1000 Unicode code points after stripping outer whitespace."""
    if not isinstance(description, str):
        return ValidationResult(False, error_code="DESCRIPTION_TYPE")

    text = description.strip()
    if not text:
        return ValidationResult(False, error_code="DESCRIPTION_REQUIRED")

    if len(text) > MAX_DESCRIPTION_LENGTH + 1:
        return ValidationResult(False, error_code="DESCRIPTION_TOO_LONG")

    return ValidationResult(True, normalized_description=text)
