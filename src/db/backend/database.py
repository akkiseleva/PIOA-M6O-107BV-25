from abc import ABC, abstractmethod
from typing import Any
from .errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    EmptyTableNameError,
    EmptyColumnsError,
    InvalidColumnNameError
)
from .table import DataTable


class DBManager(ABC):
    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        if not table_name or not table_name.strip():
            raise EmptyTableNameError("Имя таблицы не может быть пустым")
        if not columns:
            raise EmptyColumnsError("Таблица должна содержать хотя бы одну колонку")
        if len(columns) != len(set(columns)):
            raise InvalidColumnNameError("Названия колонок не должны повторяться")
        if self._table_exists(table_name):
            raise TableAlreadyExistsError(f"Таблица '{table_name}' уже существует")
        self._save_table(table_name, DataTable(columns))

    def insert_record(self, table_name: str, record: dict[str, Any]) -> None:
        table = self._load_table(table_name)
        table.insert_record(record)
        self._save_table(table_name, table)

    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        return self._load_table(table_name).select_records(**filters)

    def update_records(self, table_name: str, updates: dict[str, Any], **filters: Any) -> int:
        table = self._load_table(table_name)
        updated = table.update_records(updates, **filters)
        if updated:
            self._save_table(table_name, table)
        return updated

    def delete_records(self, table_name: str, **filters: Any) -> int:
        table = self._load_table(table_name)
        deleted = table.delete_records(**filters)
        if deleted:
            self._save_table(table_name, table)
        return deleted

    def clear_table(self, table_name: str) -> None:
        table = self._load_table(table_name)
        table.clear()
        self._save_table(table_name, table)

    def table_exists(self, table_name: str) -> bool:
        return self._table_exists(table_name)

    def list_tables(self) -> list[str]:
        return self._list_tables()

    def rename_table(self, old: str, new: str) -> None:
        if not new or not new.strip():
            raise EmptyTableNameError("Новое имя таблицы не может быть пустым")
        if not self._table_exists(old):
            raise TableNotFoundError(f"Таблица '{old}' не найдена")
        if self._table_exists(new):
            raise TableAlreadyExistsError(f"Таблица '{new}' уже существует")
        self._rename_table(old, new)

    def delete_table(self, table_name: str) -> None:
        if not self._table_exists(table_name):
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        self._delete_table(table_name)

    def rename_column(self, table_name: str, old: str, new: str) -> None:
        table = self._load_table(table_name)
        table.rename_column(old, new)
        self._save_table(table_name, table)

    def sort_records(self, table_name: str, column: str, reverse: bool = False) -> list[dict[str, Any]]:
        table = self._load_table(table_name)
        return table.sort_records(column, reverse)

    # Методы для совместимости с тестами
    def get_all_info(self) -> dict[str, tuple[list[str], int]]:
        result = {}
        for name in self._list_tables():
            table = self._load_table(name)
            result[name] = (list(table.columns), len(table.records))
        return result

    def get_columns(self, table_name: str) -> list[str]:
        table = self._load_table(table_name)
        return list(table.columns)

    @abstractmethod
    def _table_exists(self, table_name: str) -> bool:
        pass

    @abstractmethod
    def _list_tables(self) -> list[str]:
        pass

    @abstractmethod
    def _load_table(self, table_name: str) -> DataTable:
        pass

    @abstractmethod
    def _save_table(self, table_name: str, table: DataTable) -> None:
        pass

    @abstractmethod
    def _rename_table(self, old: str, new: str) -> None:
        pass

    @abstractmethod
    def _delete_table(self, table_name: str) -> None:
        pass