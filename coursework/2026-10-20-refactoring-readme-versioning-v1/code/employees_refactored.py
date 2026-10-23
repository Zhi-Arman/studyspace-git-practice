"""Filter employee tuples while preserving the classroom code's behavior."""

from collections.abc import Iterable

EmployeeRecord = tuple[str, str, str, int, int]
FIRST_NAME = 0
LAST_NAME = 1
DEPARTMENT = 2
VACATION_DAYS = 3
SICK_DAYS = 4


def _names_with_positive_days(
    employees: Iterable[EmployeeRecord], department: str, day_index: int
) -> list[str]:
    """Return matching full names in input order, including duplicates."""
    return [
        employee[FIRST_NAME] + " " + employee[LAST_NAME]
        for employee in employees
        if employee[DEPARTMENT] == department and employee[day_index] > 0
    ]


def employees_with_unused_vacation(
    employees: Iterable[EmployeeRecord], department: str
) -> list[str]:
    """Return full names with unused vacation days greater than zero.

    Args: employees contains (first name, last name, department,
        unused vacation days, sick days); department is an exact match.
    Returns: names joined by one space; input order and duplicates kept.
    """
    return _names_with_positive_days(employees, department, VACATION_DAYS)


def employees_with_sick_leave(
    employees: Iterable[EmployeeRecord], department: str
) -> list[str]:
    """Return full names with recorded sick days greater than zero.

    Args: employees uses the same five-field tuple format;
        department is compared exactly, including letter case.
    Returns: ordered full names; an empty list when nothing matches.
    """
    return _names_with_positive_days(employees, department, SICK_DAYS)


# Keep the original calling interface available.
f = employees_with_unused_vacation
g = employees_with_sick_leave
