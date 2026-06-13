from typing import Any
from .errors import (
    TableNotFoundError,
    ColumnNotFoundError,
    DuplicateTableError,
    EmptyTableNameError,
    EmptyColumnsError,
    InvalidRecordLengthError,
    RecordNotFoundError,
    InvalidColumnNameError
)


class DataTable:
    def __init__(self, name: str, columns: list[str]):
        self.name = name
        self.columns = columns.copy()
        self.records: list[tuple[Any, ...]] = []

    def add_record(self, record: tuple[Any, ...]) -> None:
        if len(record) != len(self.columns):
            raise InvalidRecordLengthError(
                f"Ожидается {len(self.columns)} полей, получено {len(record)}"
            )
        self.records.append(record)

    def get_records(self, **filters: Any) -> list[tuple[Any, ...]]:
        if not filters:
            return self.records.copy()
        result = []
        for rec in self.records:
            if self._matches(rec, filters):
                result.append(rec)
        return result

    def update_records(self, updates: dict[str, Any], **filters: Any) -> int:
        invalid = [k for k in updates if k not in self.columns]
        if invalid:
            raise ColumnNotFoundError(f"Неизвестные поля: {', '.join(invalid)}")
        updated = 0
        for i, rec in enumerate(self.records):
            if self._matches(rec, filters):
                new_rec = list(rec)
                for key, val in updates.items():
                    new_rec[self.columns.index(key)] = val
                self.records[i] = tuple(new_rec)
                updated += 1
        return updated

    def delete_records(self, **filters: Any) -> int:
        if not filters:
            count = len(self.records)
            self.records.clear()
            return count
        to_keep = []
        deleted = 0
        for rec in self.records:
            if self._matches(rec, filters):
                deleted += 1
            else:
                to_keep.append(rec)
        self.records = to_keep
        return deleted

    def clear(self) -> None:
        self.records.clear()

    def rename_column(self, old_name: str, new_name: str) -> None:
        if old_name not in self.columns:
            raise ColumnNotFoundError(f"Колонка '{old_name}' не найдена")
        if new_name in self.columns:
            raise ColumnNotFoundError(f"Колонка '{new_name}' уже существует")
        idx = self.columns.index(old_name)
        self.columns[idx] = new_name

    def get_record_by_index(self, index: int) -> tuple[Any, ...]:
        if 0 <= index < len(self.records):
            return self.records[index]
        raise RecordNotFoundError(f"Запись с индексом {index} не найдена")

    def delete_record_by_index(self, index: int) -> None:
        if 0 <= index < len(self.records):
            del self.records[index]
        else:
            raise RecordNotFoundError(f"Запись с индексом {index} не найдена")

    def update_record_by_index(self, index: int, updates: dict[str, Any]) -> None:
        if not (0 <= index < len(self.records)):
            raise RecordNotFoundError(f"Запись с индексом {index} не найдена")
        invalid = [k for k in updates if k not in self.columns]
        if invalid:
            raise ColumnNotFoundError(f"Неизвестные поля: {', '.join(invalid)}")
        new_rec = list(self.records[index])
        for key, val in updates.items():
            new_rec[self.columns.index(key)] = val
        self.records[index] = tuple(new_rec)

    def sort_records(self, column: str, reverse: bool = False) -> list[tuple[Any, ...]]:
        if column not in self.columns:
            raise ColumnNotFoundError(f"Колонка '{column}' не найдена")
        idx = self.columns.index(column)
        return sorted(self.records, key=lambda r: r[idx], reverse=reverse)

    def _matches(self, record: tuple, filters: dict) -> bool:
        for key, val in filters.items():
            if key not in self.columns:
                raise ColumnNotFoundError(
                    f"Колонка '{key}' не найдена. Доступные колонки: {self.columns}"
                )
            if record[self.columns.index(key)] != val:
                return False
        return True


class DBManager:
    def __init__(self):
        self._tables: dict[str, DataTable] = {}

    def create_table(self, name: str, columns: list[str]) -> DataTable:
        name = name.strip()
        if not name:
            raise EmptyTableNameError("Имя таблицы не может быть пустым")
        if not columns:
            raise EmptyColumnsError("Нужно указать хотя бы одну колонку")
        if len(columns) != len(set(columns)):
            raise InvalidColumnNameError("Названия колонок не должны повторяться")
        if name in self._tables:
            raise DuplicateTableError(f"Таблица '{name}' уже существует")
        table = DataTable(name, columns.copy())
        self._tables[name] = table
        return table

    def list_tables(self) -> list[str]:
        return list(self._tables.keys())

    def get_table(self, name: str) -> DataTable | None:
        return self._tables.get(name)

    def get_columns(self, name: str) -> list[str]:
        table = self._tables.get(name)
        if not table:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        return table.columns.copy()

    def delete_table(self, name: str) -> None:
        if name not in self._tables:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        del self._tables[name]

    def clear_table(self, name: str) -> None:
        table = self._tables.get(name)
        if not table:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        table.clear()

    def rename_table(self, old_name: str, new_name: str) -> None:
        old = old_name.strip()
        new = new_name.strip()
        if not old or not new:
            raise EmptyTableNameError("Имя таблицы не может быть пустым")
        if old not in self._tables:
            raise TableNotFoundError(f"Таблица '{old}' не найдена")
        if new in self._tables:
            raise DuplicateTableError(f"Таблица '{new}' уже существует")
        table = self._tables.pop(old)
        table.name = new
        self._tables[new] = table

    def rename_column(self, table_name: str, old_col: str, new_col: str) -> None:
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        table.rename_column(old_col, new_col)

    def table_exists(self, name: str) -> bool:
        return name in self._tables

    def get_all_info(self) -> dict[str, tuple[list[str], int]]:
        result = {}
        for name, table in self._tables.items():
            result[name] = (table.columns.copy(), len(table.records))
        return result

    def insert_record(self, table_name: str, record: tuple) -> None:
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        table.add_record(record)

    def select_records(self, table_name: str, **filters) -> list[tuple]:
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.get_records(**filters)

    def update_records(self, table_name: str, updates: dict, **filters) -> int:
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.update_records(updates, **filters)

    def update_records_by_indexes(self, table_name: str, indexes: list[int], updates: dict) -> int:
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        updated = 0
        for idx in sorted(indexes, reverse=True):
            if 0 <= idx < len(table.records):
                try:
                    table.update_record_by_index(idx, updates)
                    updated += 1
                except (ColumnNotFoundError, RecordNotFoundError):
                    raise
        return updated

    def delete_records(self, table_name: str, **filters) -> int:
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.delete_records(**filters)

    def delete_records_by_indexes(self, table_name: str, indexes: list[int]) -> int:
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        deleted = 0
        for idx in sorted(indexes, reverse=True):
            if 0 <= idx < len(table.records):
                del table.records[idx]
                deleted += 1
        return deleted

    def sort_records(self, table_name: str, column: str, reverse: bool = False) -> list[tuple]:
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.sort_records(column, reverse)