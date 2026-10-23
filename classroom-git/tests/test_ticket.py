import unittest
from exercise import Ticket


class TicketTests(unittest.TestCase):
    def test_default_status(self):
        self.assertEqual(Ticket("example description").status, "new")

    def test_description_preserved(self):
        self.assertEqual(Ticket("中文说明 Русский").description, "中文说明 Русский")
