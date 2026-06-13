import unittest
from unittest.mock import patch
from src.db.backend.memory import MemoryDatabase
from src.db.tui import ConsoleUI


class TestConsoleUI(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()
        self.ui = ConsoleUI(db=self.db)

    def tearDown(self):
        self.ui = None
        self.db = None

    def _mock_input(self, inputs):
        self.inputs = inputs
        self.input_index = 0
        self.original_input = __builtins__['input']
        __builtins__['input'] = self._mock_input_func

    def _mock_input_func(self, prompt=""):
        if self.input_index < len(self.inputs):
            value = self.inputs[self.input_index]
            self.input_index += 1
            return value
        return ""

    def _restore_input(self):
        __builtins__['input'] = self.original_input

    def test_create_table_success(self):
        self._mock_input(["hotel", "id name room"])
        self.ui._create_table()
        self._restore_input()
        self.assertIn("hotel", self.db.list_tables())

    def test_create_table_empty_name(self):
        self._mock_input([""])
        self.ui._create_table()
        self._restore_input()
        self.assertEqual(self.db.list_tables(), [])

    def test_create_table_no_columns(self):
        self._mock_input(["test", ""])
        self.ui._create_table()
        self._restore_input()
        self.assertEqual(self.db.list_tables(), [])

    def test_create_table_duplicate(self):
        self.db.create_table("hotel", ("id", "name"))
        self._mock_input(["hotel", "id name room"])
        self.ui._create_table()
        self._restore_input()

    def test_select_table_by_number(self):
        self.db.create_table("hotel1", ("id",))
        self.db.create_table("hotel2", ("id",))
        self._mock_input(["1"])
        self.ui._select_table()
        self._restore_input()
        self.assertEqual(self.ui._current_table, "hotel1")

    def test_select_table_by_name(self):
        self.db.create_table("hotel", ("id",))
        self._mock_input(["hotel"])
        self.ui._select_table()
        self._restore_input()
        self.assertEqual(self.ui._current_table, "hotel")

    def test_select_table_no_tables(self):
        self._mock_input(["1"])
        self.ui._select_table()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_show_tables_empty(self):
        self.ui._show_tables()

    def test_show_tables_with_data(self):
        self.db.create_table("hotel1", ("id",))
        self.db.create_table("hotel2", ("id",))
        self.ui._show_tables()

    def test_show_table_info_no_table(self):
        self.ui._show_table_info()

    def test_show_table_info_success(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self.ui._show_table_info()

    def test_add_record_success(self):
        self.db.create_table("hotel", ("id", "name", "room"))
        self.ui._current_table = "hotel"
        self._mock_input(["id", "1", "name", "John", "room", "101", ""])
        self.ui._add_record()
        self._restore_input()
        records = self.db.select_records("hotel")
        self.assertEqual(len(records), 1)

    def test_add_record_no_table(self):
        self._mock_input(["id", "1", "name", "John", ""])
        self.ui._add_record()
        self._restore_input()

    def test_add_record_table_not_found(self):
        self.ui._current_table = "ghost"
        self._mock_input(["id", "1", "name", "John", ""])
        self.ui._add_record()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_show_records_success(self):
        self.db.create_table("hotel", ("id", "name", "room"))
        self.db.insert_record("hotel", {"id": 1, "name": "John", "room": 101})
        self.ui._current_table = "hotel"
        self.ui._show_records()

    def test_show_records_no_table(self):
        self.ui._show_records()

    def test_find_records_success(self):
        self.db.create_table("hotel", ("id", "name", "room"))
        self.db.insert_record("hotel", {"id": 1, "name": "John", "room": 101})
        self.ui._current_table = "hotel"
        self._mock_input(["name=John"])
        self.ui._find_records()
        self._restore_input()

    def test_find_records_no_filters(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self._mock_input([""])
        self.ui._find_records()
        self._restore_input()

    def test_clear_table_success(self):
        self.db.create_table("hotel", ("id",))
        self.db.insert_record("hotel", {"id": 1})
        self.ui._current_table = "hotel"
        self._mock_input(["д"])
        self.ui._clear_table()
        self._restore_input()
        self.assertEqual(len(self.db.select_records("hotel")), 0)

    def test_clear_table_cancel(self):
        self.db.create_table("hotel", ("id",))
        self.db.insert_record("hotel", {"id": 1})
        self.ui._current_table = "hotel"
        self._mock_input(["н"])
        self.ui._clear_table()
        self._restore_input()
        self.assertEqual(len(self.db.select_records("hotel")), 1)

    def test_rename_table_success(self):
        self.db.create_table("old", ("id",))
        self.ui._current_table = "old"
        self._mock_input(["new"])
        self.ui._rename_table()
        self._restore_input()
        self.assertIn("new", self.db.list_tables())
        self.assertEqual(self.ui._current_table, "new")

    def test_rename_table_same_name(self):
        self.db.create_table("hotel", ("id",))
        self.ui._current_table = "hotel"
        self._mock_input(["hotel"])
        self.ui._rename_table()
        self._restore_input()
        self.assertIn("hotel", self.db.list_tables())

    def test_delete_table_success(self):
        self.db.create_table("hotel", ("id",))
        self.ui._current_table = "hotel"
        self._mock_input(["hotel", "д"])
        self.ui._delete_table()
        self._restore_input()
        self.assertNotIn("hotel", self.db.list_tables())
        self.assertIsNone(self.ui._current_table)

    def test_delete_table_not_found(self):
        self.db.create_table("hotel", ("id",))
        self._mock_input(["ghost"])
        self.ui._delete_table()
        self._restore_input()

    def test_rename_column_success(self):
        self.db.create_table("hotel", ("old", "other"))
        self.ui._current_table = "hotel"
        self._mock_input(["old", "new"])
        self.ui._rename_column()
        self._restore_input()
        cols = self.db.get_columns("hotel")
        self.assertIn("new", cols)
        self.assertNotIn("old", cols)

    def test_rename_column_not_found(self):
        self.db.create_table("hotel", ("name",))
        self.ui._current_table = "hotel"
        self._mock_input(["age", "newage"])
        self.ui._rename_column()
        self._restore_input()

    def test_sort_records_success(self):
        self.db.create_table("hotel", ("id", "name", "room"))
        self.db.insert_record("hotel", {"id": 1, "name": "John", "room": 103})
        self.db.insert_record("hotel", {"id": 2, "name": "Alice", "room": 101})
        self.db.insert_record("hotel", {"id": 3, "name": "Bob", "room": 102})
        self.ui._current_table = "hotel"
        self._mock_input(["room", "1"])
        self.ui._sort_records()
        self._restore_input()

    def test_sort_records_no_table(self):
        self._mock_input(["room", "1"])
        self.ui._sort_records()
        self._restore_input()

    def test_sort_records_table_not_found(self):
        self.ui._current_table = "ghost"
        self._mock_input(["room", "1"])
        self.ui._sort_records()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_sort_records_empty_table(self):
        self.db.create_table("hotel", ("id", "name", "room"))
        self.ui._current_table = "hotel"
        self._mock_input(["room", "1"])
        self.ui._sort_records()
        self._restore_input()

    def test_update_records_cancel(self):
        self.db.create_table("hotel", ("id", "name"))
        self.db.insert_record("hotel", {"id": 1, "name": "John"})
        self.db.insert_record("hotel", {"id": 2, "name": "Jane"})
        self.ui._current_table = "hotel"
        self._mock_input(["", "all", "н"])
        self.ui._update_records()
        self._restore_input()
        records = self.db.select_records("hotel")
        self.assertEqual(len(records), 2)

    def test_delete_by_filter_cancel(self):
        self.db.create_table("hotel", ("id", "name"))
        self.db.insert_record("hotel", {"id": 1, "name": "John"})
        self.ui._current_table = "hotel"
        self._mock_input(["name=John", "all", "н"])
        self.ui._delete_by_filter()
        self._restore_input()
        records = self.db.select_records("hotel")
        self.assertEqual(len(records), 1)

    def test_add_record_missing_id(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self._mock_input(["name", "John", ""])
        self.ui._add_record()
        self._restore_input()
        records = self.db.select_records("hotel")
        self.assertEqual(len(records), 0)

    def test_find_records_unknown_column(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self._mock_input(["unknown=John"])
        self.ui._find_records()
        self._restore_input()

    def test_delete_by_filter_no_filter(self):
        self.db.create_table("hotel", ("id",))
        self.ui._current_table = "hotel"
        self._mock_input([""])
        self.ui._delete_by_filter()
        self._restore_input()

    def test_update_records_no_updates(self):
        self.db.create_table("hotel", ("id", "name"))
        self.db.insert_record("hotel", {"id": 1, "name": "John"})
        self.ui._current_table = "hotel"
        self._mock_input(["", "all", "д", ""])
        self.ui._update_records()
        self._restore_input()
        records = self.db.select_records("hotel")
        self.assertEqual(records[0]["name"], "John")

    def test_run_exit(self):
        with patch('builtins.input', side_effect=["0"]):
            self.ui.run()

    def test_run_invalid_command(self):
        with patch('builtins.input', side_effect=["invalid", "0"]):
            self.ui.run()

    def test_add_record_empty(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self._mock_input([""])
        self.ui._add_record()
        self._restore_input()
        records = self.db.select_records("hotel")
        self.assertEqual(len(records), 0)

    def test_find_records_no_results(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self._mock_input(["name=Ghost"])
        self.ui._find_records()
        self._restore_input()

    def test_clear_table_empty(self):
        self.db.create_table("hotel", ("id",))
        self.ui._current_table = "hotel"
        self._mock_input(["д"])
        self.ui._clear_table()
        self._restore_input()
        self.assertEqual(len(self.db.select_records("hotel")), 0)

    def test_rename_column_duplicate(self):
        self.db.create_table("hotel", ("name", "age"))
        self.ui._current_table = "hotel"
        self._mock_input(["name", "age"])
        self.ui._rename_column()
        self._restore_input()
        cols = self.db.get_columns("hotel")
        self.assertEqual(cols, ["name", "age"])

    def test_show_table_info_not_selected(self):
        self.ui._show_table_info()

    def test_show_records_empty_table(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self.ui._show_records()

    def test_find_records_invalid_filter_format(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self._mock_input(["name"])
        self.ui._find_records()
        self._restore_input()

    def test_update_records_invalid_choice(self):
        self.db.create_table("hotel", ("id", "name"))
        self.db.insert_record("hotel", {"id": 1, "name": "John"})
        self.ui._current_table = "hotel"
        self._mock_input(["", "abc"])
        self.ui._update_records()
        self._restore_input()

    def test_delete_by_filter_invalid_choice(self):
        self.db.create_table("hotel", ("id", "name"))
        self.db.insert_record("hotel", {"id": 1, "name": "John"})
        self.ui._current_table = "hotel"
        self._mock_input(["name=John", "abc"])
        self.ui._delete_by_filter()
        self._restore_input()

    def test_rename_column_table_not_found(self):
        self.ui._current_table = "ghost"
        self._mock_input(["old", "new"])
        self.ui._rename_column()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_select_table_invalid_choice(self):
        self.db.create_table("hotel1", ("id",))
        self.db.create_table("hotel2", ("id",))
        self._mock_input(["3"])
        self.ui._select_table()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_select_table_by_name_invalid(self):
        self.db.create_table("hotel1", ("id",))
        self._mock_input(["ghost"])
        self.ui._select_table()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_show_table_info_table_not_found(self):
        self.ui._current_table = "ghost"
        self.ui._show_table_info()
        self.assertIsNone(self.ui._current_table)

    def test_add_record_table_not_found_after_check(self):
        self.ui._current_table = "ghost"
        self._mock_input(["id", "1", "name", "John", ""])
        self.ui._add_record()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_find_records_table_not_found(self):
        self.ui._current_table = "ghost"
        self._mock_input(["name=John"])
        self.ui._find_records()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_update_records_table_not_found(self):
        self.ui._current_table = "ghost"
        self._mock_input(["", "all", "д", "name=Peter"])
        self.ui._update_records()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_delete_by_filter_table_not_found(self):
        self.ui._current_table = "ghost"
        self._mock_input(["name=John", "all", "д"])
        self.ui._delete_by_filter()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_clear_table_not_found(self):
        self.ui._current_table = "ghost"
        self._mock_input(["д"])
        self.ui._clear_table()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_rename_column_table_not_found_in_method(self):
        self.ui._current_table = "ghost"
        self._mock_input(["old", "new"])
        self.ui._rename_column()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_sort_records_table_not_found(self):
        self.ui._current_table = "ghost"
        self._mock_input(["room", "1"])
        self.ui._sort_records()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_create_table_invalid_first_column(self):
        self._mock_input(["hotel", "name id room"])
        self.ui._create_table()
        self._restore_input()
        self.assertEqual(self.db.list_tables(), [])

    def test_add_record_empty_after_id_check(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self._mock_input(["id", "1", "name", "", ""])
        self.ui._add_record()
        self._restore_input()
        records = self.db.select_records("hotel")
        self.assertEqual(len(records), 0)

    def test_update_records_no_matches(self):
        self.db.create_table("hotel", ("id", "name"))
        self.db.insert_record("hotel", {"id": 1, "name": "John"})
        self.ui._current_table = "hotel"
        self._mock_input(["name=Ghost"])
        self.ui._update_records()
        self._restore_input()

    def test_create_table_duplicate_name(self):
        self.db.create_table("hotel", ("id", "name"))
        self._mock_input(["hotel", "id name room"])
        self.ui._create_table()
        self._restore_input()

    def test_select_table_invalid_number(self):
        self.db.create_table("hotel1", ("id",))
        self.db.create_table("hotel2", ("id",))
        self._mock_input(["3"])
        self.ui._select_table()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_select_table_invalid_name(self):
        self.db.create_table("hotel1", ("id",))
        self._mock_input(["ghost"])
        self.ui._select_table()
        self._restore_input()
        self.assertIsNone(self.ui._current_table)

    def test_show_table_info_no_table_selected(self):
        self.ui._show_table_info()

    def test_show_records_no_table_selected(self):
        self.ui._show_records()

    def test_find_records_no_table_selected(self):
        self._mock_input(["name=John"])
        self.ui._find_records()
        self._restore_input()

    def test_update_records_no_table_selected(self):
        self._mock_input(["", "all", "д", "name=Peter"])
        self.ui._update_records()
        self._restore_input()

    def test_delete_by_filter_no_table_selected(self):
        self._mock_input(["name=John", "all", "д"])
        self.ui._delete_by_filter()
        self._restore_input()

    def test_clear_table_no_table_selected(self):
        self._mock_input(["д"])
        self.ui._clear_table()
        self._restore_input()

    def test_delete_table_no_tables(self):
        self._mock_input(["hotel"])
        self.ui._delete_table()
        self._restore_input()

    def test_delete_table_empty_name(self):
        self.db.create_table("hotel", ("id",))
        self._mock_input([""])
        self.ui._delete_table()
        self._restore_input()
        self.assertIn("hotel", self.db.list_tables())

    def test_rename_table_no_table_selected(self):
        self.ui._rename_table()

    def test_rename_table_empty_new_name(self):
        self.db.create_table("hotel", ("id",))
        self.ui._current_table = "hotel"
        self._mock_input([""])
        self.ui._rename_table()
        self._restore_input()
        self.assertEqual(self.ui._current_table, "hotel")

    def test_rename_table_same_name(self):
        self.db.create_table("hotel", ("id",))
        self.ui._current_table = "hotel"
        self._mock_input(["hotel"])
        self.ui._rename_table()
        self._restore_input()
        self.assertEqual(self.ui._current_table, "hotel")

    def test_rename_column_no_table_selected(self):
        self.ui._rename_column()

    def test_rename_column_empty_old(self):
        self.db.create_table("hotel", ("name", "age"))
        self.ui._current_table = "hotel"
        self._mock_input([""])
        self.ui._rename_column()
        self._restore_input()

    def test_rename_column_empty_new(self):
        self.db.create_table("hotel", ("name", "age"))
        self.ui._current_table = "hotel"
        self._mock_input(["name", ""])
        self.ui._rename_column()
        self._restore_input()
        cols = self.db.get_columns("hotel")
        self.assertEqual(cols, ["name", "age"])

    def test_sort_records_no_column(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self._mock_input([""])
        self.ui._sort_records()
        self._restore_input()

    def test_sort_records_invalid_column(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self._mock_input(["ghost", "1"])
        self.ui._sort_records()
        self._restore_input()

    def test_sort_records_empty_table(self):
        self.db.create_table("hotel", ("id", "name"))
        self.ui._current_table = "hotel"
        self._mock_input(["name", "1"])
        self.ui._sort_records()
        self._restore_input()

if __name__ == '__main__':
    unittest.main()