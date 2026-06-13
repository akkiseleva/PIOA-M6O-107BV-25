from .database import DBManager
from .errors import TableNotFoundError
from .table import DataTable


class MemoryDatabase(DBManager):
    def __init__(self):
        self._tables: dict[str, DataTable] = {}

    def _table_exists(self, table_name: str) -> bool:
        return table_name in self._tables

    def _list_tables(self) -> list[str]:
        return list(self._tables.keys())

    def _load_table(self, table_name: str) -> DataTable:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return self._tables[table_name]

    def _save_table(self, table_name: str, table: DataTable) -> None:
        self._tables[table_name] = table

    def _rename_table(self, old: str, new: str) -> None:
        self._tables[new] = self._tables.pop(old)

    def _delete_table(self, table_name: str) -> None:
        del self._tables[table_name]

    # Добавленные методы для совместимости с тестами
    def get_all_info(self) -> dict[str, tuple[list[str], int]]:
        result = {}
        for name, table in self._tables.items():
            result[name] = (list(table.columns), len(table.records))
        return result

    def get_columns(self, table_name: str) -> list[str]:
        table = self._load_table(table_name)
        return list(table.columns)