import tempfile
import unittest
from src.db.backend.file import FileDatabase
from src.db.backend.errors import TableNotFoundError, TableAlreadyExistsError


class TestFileDatabase(unittest.TestCase):
    def test_create_and_select(self):
        with tempfile.TemporaryDirectory() as d:
            db = FileDatabase(d)
            db.create_table("hotel", ("id", "name", "room", "check_in", "check_out"))
            db.insert_record("hotel", {"id": 1, "name": "John", "room": 101, "check_in": "2024-01-01", "check_out": "2024-01-05"})
            records = db.select_records("hotel")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["name"], "John")

    def test_data_persists(self):
        with tempfile.TemporaryDirectory() as d:
            db1 = FileDatabase(d)
            db1.create_table("hotel", ("id", "name"))
            db1.insert_record("hotel", {"id": 1, "name": "John"})
            db2 = FileDatabase(d)
            records = db2.select_records("hotel")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["name"], "John")

    def test_select_with_filter(self):
        with tempfile.TemporaryDirectory() as d:
            db = FileDatabase(d)
            db.create_table("hotel", ("id", "name"))
            db.insert_record("hotel", {"id": 1, "name": "John"})
            db.insert_record("hotel", {"id": 2, "name": "Jane"})
            records = db.select_records("hotel", name="Jane")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["id"], 2)

    def test_table_not_found(self):
        with tempfile.TemporaryDirectory() as d:
            db = FileDatabase(d)
            with self.assertRaises(TableNotFoundError):
                db.select_records("ghost")

    def test_create_duplicate_table(self):
        with tempfile.TemporaryDirectory() as d:
            db = FileDatabase(d)
            db.create_table("hotel", ("id", "name"))
            with self.assertRaises(TableAlreadyExistsError):
                db.create_table("hotel", ("id", "name"))

    def test_delete_table(self):
        with tempfile.TemporaryDirectory() as d:
            db = FileDatabase(d)
            db.create_table("hotel", ("id", "name"))
            db.delete_table("hotel")
            self.assertNotIn("hotel", db.list_tables())

    def test_rename_table(self):
        with tempfile.TemporaryDirectory() as d:
            db = FileDatabase(d)
            db.create_table("old", ("id", "name"))
            db.rename_table("old", "new")
            self.assertIn("new", db.list_tables())
            self.assertNotIn("old", db.list_tables())

    def test_clear_table(self):
        with tempfile.TemporaryDirectory() as d:
            db = FileDatabase(d)
            db.create_table("hotel", ("id", "name"))
            db.insert_record("hotel", {"id": 1, "name": "John"})
            db.clear_table("hotel")
            records = db.select_records("hotel")
            self.assertEqual(len(records), 0)


if __name__ == '__main__':
    unittest.main()