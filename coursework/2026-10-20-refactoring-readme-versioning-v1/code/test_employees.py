"""Two characterization tests that can run before and after refactoring."""

import importlib
import os
import unittest

employee_module = importlib.import_module(
    os.environ.get("EMPLOYEE_MODULE", "employees_refactored")
)


class EmployeeFilterTests(unittest.TestCase):
    def setUp(self):
        self.employees = [
            ("Anna", "Ivanova", "IT", 5, 0),
            ("Ivan", "Petrov", "IT", 0, 2),
            ("Olga", "Sidorova", "HR", 7, 3),
            ("Petr", "Orlov", "IT", -1, 0),
            ("Maria", "Volkova", "IT", 1, -2),
            ("Anna", "Ivanova", "IT", 5, 0),
        ]

    def test_vacation_filters_department_and_positive_days(self):
        self.assertEqual(
            employee_module.f(self.employees, "IT"),
            ["Anna Ivanova", "Maria Volkova", "Anna Ivanova"],
        )

    def test_sick_leave_uses_sick_days_instead_of_vacation(self):
        self.assertEqual(
            employee_module.g(self.employees, "IT"),
            ["Ivan Petrov"],
        )


if __name__ == "__main__":
    unittest.main()
