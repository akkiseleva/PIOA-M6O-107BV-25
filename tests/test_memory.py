import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.table import DataTable
from src.db.backend.errors import (
    TableNotFoundError,
    ColumnNotFoundError,
    DuplicateTableError,
    EmptyTableNameError,
    EmptyColumnsError,
    InvalidRecordLengthError,
    RecordNotFoundError,
    InvalidColumnNameError,
    TableAlreadyExistsError,
    UnknownColumnError,
    MissingColumnError
)


class TestDBManager(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()

    def test_create_table_success(self):
        self.db.create_table("hotel", ("id", "name", "room", "check_in", "check_out"))
        self.assertIn("hotel", self.db.list_tables())

    def test_create_table_duplicate(self):
        self.db.create_table("hotel", ("id", "name"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("hotel", ("id", "name", "room"))

    def test_create_table_empty_name(self):
        with self.assertRaises(EmptyTableNameError):
            self.db.create_table("", ("id",))

    def test_create_table_no_columns(self):
        with self.assertRaises(EmptyColumnsError):
            self.db.create_table("test", ())

    def test_create_table_duplicate_columns(self):
        with self.assertRaises(InvalidColumnNameError):
            self.db.create_table("hotel", ("id", "name", "id"))

    def test_list_tables_empty(self):
        self.assertEqual(self.db.list_tables(), [])

    def test_list_tables_with_data(self):
        self.db.create_table("hotel1", ("col1",))
        self.db.create_table("hotel2", ("col1",))
        tables = self.db.list_tables()
        self.assertEqual(len(tables), 2)
        self.assertIn("hotel1", tables)
        self.assertIn("hotel2", tables)

    def test_delete_table_success(self):
        self.db.create_table("test", ("col",))
        self.db.delete_table("test")
        self.assertNotIn("test", self.db.list_tables())

    def test_delete_table_not_exists(self):
        with self.assertRaises(TableNotFoundError):
            self.db.delete_table("ghost")

    def test_rename_table_success(self):
        self.db.create_table("old", ("col",))
        self.db.rename_table("old", "new")
        self.assertIn("new", self.db.list_tables())
        self.assertNotIn("old", self.db.list_tables())

    def test_rename_table_not_exists(self):
        with self.assertRaises(TableNotFoundError):
            self.db.rename_table("ghost", "new")

    def test_rename_table_to_existing(self):
        self.db.create_table("hotel1", ("col",))
        self.db.create_table("hotel2", ("col",))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.rename_table("hotel1", "hotel2")

    def test_rename_table_empty_name(self):
        self.db.create_table("test", ("col",))
        with self.assertRaises(EmptyTableNameError):
            self.db.rename_table("test", "")

    def test_get_all_info_empty(self):
        info = self.db.get_all_info()
        self.assertEqual(info, {})

    def test_get_all_info_with_tables(self):
        self.db.create_table("hotel1", ("id", "name"))
        self.db.create_table("hotel2", ("title",))
        self.db.insert_record("hotel1", {"id": 1, "name": "John"})
        info = self.db.get_all_info()
        self.assertEqual(len(info), 2)
        self.assertIn("hotel1", info)
        self.assertIn("hotel2", info)

    def test_table_exists(self):
        self.db.create_table("test", ("col",))
        self.assertTrue(self.db.table_exists("test"))
        self.assertFalse(self.db.table_exists("ghost"))

    def test_get_columns_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.get_columns("ghost")

    def test_clear_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.clear_table("ghost")

    def test_insert_record_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.insert_record("ghost", {"id": 1})

    def test_select_records_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("ghost")

    def test_update_records_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.update_records("ghost", {"name": "Peter"})

    def test_delete_records_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.delete_records("ghost")

    def test_sort_records_database(self):
        self.db.create_table("hotel", ("id", "name", "room"))
        self.db.insert_record("hotel", {"id": 1, "name": "John", "room": 103})
        self.db.insert_record("hotel", {"id": 2, "name": "Alice", "room": 101})
        self.db.insert_record("hotel", {"id": 3, "name": "Bob", "room": 102})
        result = self.db.sort_records("hotel", "room", reverse=False)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["room"], 101)
        self.assertEqual(result[1]["room"], 102)
        self.assertEqual(result[2]["room"], 103)

    def test_sort_records_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.sort_records("ghost", "room")

    def test_table_rename_column_not_found(self):
        table = DataTable(("id", "name"), [])
        with self.assertRaises(UnknownColumnError):
            table.rename_column("ghost", "new")

    def test_table_sort_records_empty(self):
        table = DataTable(("id", "name"), [])
        result = table.sort_records("name")
        self.assertEqual(result, [])

    def test_table_update_records_unknown_field(self):
        table = DataTable(("id", "name"), [{"id": 1, "name": "John"}])
        with self.assertRaises(UnknownColumnError):
            table.update_records({"age": 20})

    def test_table_update_record_by_index_not_found(self):
        table = DataTable(("id", "name"), [{"id": 1, "name": "John"}])
        with self.assertRaises(RecordNotFoundError):
            table.update_record_by_index(5, {"name": "Peter"})

    def test_table_delete_record_by_index_not_found(self):
        table = DataTable(("id", "name"), [{"id": 1, "name": "John"}])
        with self.assertRaises(RecordNotFoundError):
            table.delete_record_by_index(5)

    def test_table_get_record_by_index_not_found(self):
        table = DataTable(("id", "name"), [{"id": 1, "name": "John"}])
        with self.assertRaises(RecordNotFoundError):
            table.get_record_by_index(5)

    def test_table_sort_records_column_not_found(self):
        table = DataTable(("id", "name"), [{"id": 1, "name": "John"}])
        with self.assertRaises(UnknownColumnError):
            table.sort_records("ghost")


if __name__ == '__main__':
    unittest.main()