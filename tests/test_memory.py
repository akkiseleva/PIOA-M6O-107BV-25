import unittest
from src.db.backend.memory import DBManager, DataTable
from src.db.backend.errors import (
    TableNotFoundError,
    ColumnNotFoundError,
    DuplicateTableError,
    EmptyTableNameError,
    EmptyColumnsError,
    InvalidRecordLengthError,
    RecordNotFoundError,
    InvalidColumnNameError
)


class TestDBManager(unittest.TestCase):
    def setUp(self):
        self.db = DBManager()

    def test_create_table_success(self):
        self.db.create_table("hotel", ["id", "name", "room", "check_in", "check_out"])
        self.assertIn("hotel", self.db.list_tables())
        self.assertEqual(self.db.get_columns("hotel"), ["id", "name", "room", "check_in", "check_out"])

    def test_create_table_duplicate(self):
        self.db.create_table("hotel", ["id", "name"])
        with self.assertRaises(DuplicateTableError):
            self.db.create_table("hotel", ["id", "name", "room"])

    def test_create_table_empty_name(self):
        with self.assertRaises(EmptyTableNameError):
            self.db.create_table("", ["id"])

    def test_create_table_no_columns(self):
        with self.assertRaises(EmptyColumnsError):
            self.db.create_table("test", [])

    def test_create_table_duplicate_columns(self):
        with self.assertRaises(InvalidColumnNameError):
            self.db.create_table("hotel", ["id", "name", "id"])

    def test_list_tables_empty(self):
        self.assertEqual(self.db.list_tables(), [])

    def test_list_tables_with_data(self):
        self.db.create_table("hotel1", ["col1"])
        self.db.create_table("hotel2", ["col1"])
        tables = self.db.list_tables()
        self.assertEqual(len(tables), 2)
        self.assertIn("hotel1", tables)
        self.assertIn("hotel2", tables)

    def test_delete_table_success(self):
        self.db.create_table("test", ["col"])
        self.db.delete_table("test")
        self.assertNotIn("test", self.db.list_tables())

    def test_delete_table_not_exists(self):
        with self.assertRaises(TableNotFoundError):
            self.db.delete_table("ghost")

    def test_rename_table_success(self):
        self.db.create_table("old", ["col"])
        self.db.rename_table("old", "new")
        self.assertNotIn("old", self.db.list_tables())
        self.assertIn("new", self.db.list_tables())

    def test_rename_table_not_exists(self):
        with self.assertRaises(TableNotFoundError):
            self.db.rename_table("ghost", "new")

    def test_rename_table_to_existing(self):
        self.db.create_table("hotel1", ["col"])
        self.db.create_table("hotel2", ["col"])
        with self.assertRaises(DuplicateTableError):
            self.db.rename_table("hotel1", "hotel2")

    def test_rename_table_empty_name(self):
        self.db.create_table("test", ["col"])
        with self.assertRaises(EmptyTableNameError):
            self.db.rename_table("test", "")

    def test_get_all_info_empty(self):
        info = self.db.get_all_info()
        self.assertEqual(info, {})

    def test_get_all_info_with_tables(self):
        self.db.create_table("hotel1", ["id", "name"])
        self.db.create_table("hotel2", ["title"])
        self.db.insert_record("hotel1", (1, "John"))
        info = self.db.get_all_info()
        self.assertEqual(len(info), 2)
        self.assertIn("hotel1", info)
        self.assertIn("hotel2", info)

    def test_table_exists(self):
        self.db.create_table("test", ["col"])
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
            self.db.insert_record("ghost", (1, "John", 101, "2024-01-01", "2024-01-05"))

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
        self.db.create_table("hotel", ["id", "name", "room"])
        self.db.insert_record("hotel", (1, "John", 103))
        self.db.insert_record("hotel", (2, "Alice", 101))
        self.db.insert_record("hotel", (3, "Bob", 102))
        result = self.db.sort_records("hotel", "room", reverse=False)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][2], 101)
        self.assertEqual(result[1][2], 102)
        self.assertEqual(result[2][2], 103)

    def test_sort_records_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.sort_records("ghost", "room")


class TestDataTable(unittest.TestCase):
    def setUp(self):
        self.table = DataTable("hotel", ["id", "name", "room", "check_in", "check_out"])

    def test_table_initialization(self):
        self.assertEqual(self.table.name, "hotel")
        self.assertEqual(self.table.columns, ["id", "name", "room", "check_in", "check_out"])
        self.assertEqual(len(self.table.records), 0)

    def test_add_record_success(self):
        record = (1, "John", 101, "2024-01-01", "2024-01-05")
        self.table.add_record(record)
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0], record)

    def test_add_record_wrong_length(self):
        record = (1, "John", 101)
        with self.assertRaises(InvalidRecordLengthError):
            self.table.add_record(record)

    def test_add_multiple_records(self):
        records = [
            (1, "John", 101, "2024-01-01", "2024-01-05"),
            (2, "Jane", 102, "2024-01-02", "2024-01-06"),
            (3, "Bob", 103, "2024-01-03", "2024-01-07")
        ]
        for rec in records:
            self.table.add_record(rec)
        self.assertEqual(len(self.table.records), 3)
        self.assertEqual(self.table.records, records)

    def test_get_records_no_filters(self):
        records = [
            (1, "John", 101, "2024-01-01", "2024-01-05"),
            (2, "Jane", 102, "2024-01-02", "2024-01-06"),
            (3, "Bob", 103, "2024-01-03", "2024-01-07")
        ]
        for rec in records:
            self.table.add_record(rec)
        result = self.table.get_records()
        self.assertEqual(result, records)

    def test_get_records_with_filter(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Jane", 102, "2024-01-02", "2024-01-06"))
        self.table.add_record((3, "John", 103, "2024-01-03", "2024-01-07"))
        result = self.table.get_records(name="John")
        self.assertEqual(len(result), 2)
        self.assertIn((1, "John", 101, "2024-01-01", "2024-01-05"), result)
        self.assertIn((3, "John", 103, "2024-01-03", "2024-01-07"), result)

    def test_get_records_multiple_filters(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Jane", 102, "2024-01-02", "2024-01-06"))
        self.table.add_record((3, "John", 103, "2024-01-03", "2024-01-07"))
        result = self.table.get_records(name="John", room=101)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (1, "John", 101, "2024-01-01", "2024-01-05"))

    def test_get_records_filter_not_found(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        result = self.table.get_records(name="Ghost")
        self.assertEqual(result, [])

    def test_get_records_invalid_column(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        with self.assertRaises(ColumnNotFoundError):
            self.table.get_records(phone="123")

    def test_update_records_no_filters(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Jane", 102, "2024-01-02", "2024-01-06"))
        updated = self.table.update_records({"name": "Peter", "room": 200})
        self.assertEqual(updated, 2)
        records = self.table.records
        self.assertEqual(records[0], (1, "Peter", 200, "2024-01-01", "2024-01-05"))
        self.assertEqual(records[1], (2, "Peter", 200, "2024-01-02", "2024-01-06"))

    def test_update_records_with_filter(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Jane", 102, "2024-01-02", "2024-01-06"))
        self.table.add_record((3, "John", 103, "2024-01-03", "2024-01-07"))
        updated = self.table.update_records({"room": 999}, name="John")
        self.assertEqual(updated, 2)
        john_records = self.table.get_records(name="John")
        for rec in john_records:
            self.assertEqual(rec[2], 999)
        jane_record = self.table.get_records(name="Jane")[0]
        self.assertEqual(jane_record[2], 102)

    def test_update_records_multiple_fields(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        updated = self.table.update_records({"name": "Jonathan", "room": 999})
        self.assertEqual(updated, 1)
        record = self.table.records[0]
        self.assertEqual(record, (1, "Jonathan", 999, "2024-01-01", "2024-01-05"))

    def test_update_records_no_matches(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        updated = self.table.update_records({"name": "Peter"}, name="Ghost")
        self.assertEqual(updated, 0)
        self.assertEqual(self.table.records[0], (1, "John", 101, "2024-01-01", "2024-01-05"))

    def test_update_records_unknown_field_raises_error(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        with self.assertRaises(ColumnNotFoundError):
            self.table.update_records({"agge": 30})

    def test_delete_records_no_filters(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Jane", 102, "2024-01-02", "2024-01-06"))
        deleted = self.table.delete_records()
        self.assertEqual(deleted, 2)
        self.assertEqual(len(self.table.records), 0)

    def test_delete_records_with_filter(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Jane", 102, "2024-01-02", "2024-01-06"))
        self.table.add_record((3, "John", 103, "2024-01-03", "2024-01-07"))
        deleted = self.table.delete_records(name="John")
        self.assertEqual(deleted, 2)
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0], (2, "Jane", 102, "2024-01-02", "2024-01-06"))

    def test_delete_records_no_matches(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        deleted = self.table.delete_records(name="Ghost")
        self.assertEqual(deleted, 0)
        self.assertEqual(len(self.table.records), 1)

    def test_delete_records_multiple_filters(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "John", 102, "2024-01-02", "2024-01-06"))
        self.table.add_record((3, "Jane", 103, "2024-01-03", "2024-01-07"))
        deleted = self.table.delete_records(name="John", room=101)
        self.assertEqual(deleted, 1)
        self.assertEqual(len(self.table.records), 2)
        self.assertIn((2, "John", 102, "2024-01-02", "2024-01-06"), self.table.records)
        self.assertIn((3, "Jane", 103, "2024-01-03", "2024-01-07"), self.table.records)

    def test_clear_table(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Jane", 102, "2024-01-02", "2024-01-06"))
        self.table.clear()
        self.assertEqual(len(self.table.records), 0)

    def test_rename_column_success(self):
        self.table.rename_column("name", "full_name")
        self.assertIn("full_name", self.table.columns)
        self.assertNotIn("name", self.table.columns)

    def test_rename_column_not_exists(self):
        with self.assertRaises(ColumnNotFoundError):
            self.table.rename_column("ghost", "new")

    def test_rename_column_to_existing_raises_error(self):
        with self.assertRaises(ColumnNotFoundError):
            self.table.rename_column("name", "room")

    def test_get_record_by_index(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Jane", 102, "2024-01-02", "2024-01-06"))
        record = self.table.get_record_by_index(0)
        self.assertEqual(record, (1, "John", 101, "2024-01-01", "2024-01-05"))
        record = self.table.get_record_by_index(1)
        self.assertEqual(record, (2, "Jane", 102, "2024-01-02", "2024-01-06"))

    def test_get_record_by_index_not_found(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        with self.assertRaises(RecordNotFoundError):
            self.table.get_record_by_index(5)

    def test_delete_record_by_index(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Jane", 102, "2024-01-02", "2024-01-06"))
        self.table.delete_record_by_index(0)
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0], (2, "Jane", 102, "2024-01-02", "2024-01-06"))

    def test_delete_record_by_index_not_found(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        with self.assertRaises(RecordNotFoundError):
            self.table.delete_record_by_index(5)

    def test_update_record_by_index(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        self.table.update_record_by_index(0, {"name": "Jonathan", "room": 999})
        self.assertEqual(self.table.records[0], (1, "Jonathan", 999, "2024-01-01", "2024-01-05"))

    def test_update_record_by_index_not_found(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        with self.assertRaises(RecordNotFoundError):
            self.table.update_record_by_index(5, {"name": "Jonathan"})

    def test_sort_records_ascending(self):
        self.table.add_record((1, "John", 103, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Alice", 101, "2024-01-02", "2024-01-06"))
        self.table.add_record((3, "Bob", 102, "2024-01-03", "2024-01-07"))
        result = self.table.sort_records("room", reverse=False)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], (2, "Alice", 101, "2024-01-02", "2024-01-06"))
        self.assertEqual(result[1], (3, "Bob", 102, "2024-01-03", "2024-01-07"))
        self.assertEqual(result[2], (1, "John", 103, "2024-01-01", "2024-01-05"))

    def test_sort_records_descending(self):
        self.table.add_record((1, "John", 103, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Alice", 101, "2024-01-02", "2024-01-06"))
        self.table.add_record((3, "Bob", 102, "2024-01-03", "2024-01-07"))
        result = self.table.sort_records("room", reverse=True)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], (1, "John", 103, "2024-01-01", "2024-01-05"))
        self.assertEqual(result[1], (3, "Bob", 102, "2024-01-03", "2024-01-07"))
        self.assertEqual(result[2], (2, "Alice", 101, "2024-01-02", "2024-01-06"))

    def test_sort_records_by_string_column(self):
        self.table.add_record((1, "John", 103, "2024-01-01", "2024-01-05"))
        self.table.add_record((2, "Alice", 101, "2024-01-02", "2024-01-06"))
        self.table.add_record((3, "Bob", 102, "2024-01-03", "2024-01-07"))
        result = self.table.sort_records("name", reverse=False)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], (2, "Alice", 101, "2024-01-02", "2024-01-06"))
        self.assertEqual(result[1], (3, "Bob", 102, "2024-01-03", "2024-01-07"))
        self.assertEqual(result[2], (1, "John", 103, "2024-01-01", "2024-01-05"))

    def test_sort_records_column_not_found(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        with self.assertRaises(ColumnNotFoundError):
            self.table.sort_records("ghost", reverse=False)

    def test_sort_records_empty_table(self):
        result = self.table.sort_records("room", reverse=False)
        self.assertEqual(result, [])

    def test_get_record_by_index_not_found(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        with self.assertRaises(RecordNotFoundError):
            self.table.get_record_by_index(5)

    def test_delete_record_by_index_not_found(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        with self.assertRaises(RecordNotFoundError):
            self.table.delete_record_by_index(5)

    def test_update_record_by_index_not_found(self):
        self.table.add_record((1, "John", 101, "2024-01-01", "2024-01-05"))
        with self.assertRaises(RecordNotFoundError):
            self.table.update_record_by_index(5, {"name": "Jonathan"})


if __name__ == '__main__':
    unittest.main()