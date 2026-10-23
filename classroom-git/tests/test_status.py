import unittest
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
