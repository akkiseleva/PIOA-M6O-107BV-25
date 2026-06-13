from typing import Any
from .errors import MissingColumnError, UnknownColumnError, ColumnNotFoundError, RecordNotFoundError


class DataTable:
    def __init__(self, columns: tuple[str, ...], records: list[dict[str, Any]] | None = None):
        self.columns = columns
        self.records: list[dict[str, Any]] = []
        if records is not None:
            for record in records:
                self.insert_record(record)

    def insert_record(self, record: dict[str, Any]) -> None:
        missing = [col for col in self.columns if col not in record]
        if missing:
            raise MissingColumnError(f"Отсутствует поле: {missing[0]}")
        extra = [col for col in record if col not in self.columns]
        if extra:
            raise UnknownColumnError(f"Лишнее поле: {extra[0]}")
        self.records.append(record.copy())

    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        unknown = [key for key in filters if key not in self.columns]
        if unknown:
            raise UnknownColumnError(f"Поле '{unknown[0]}' не существует")
        if not filters:
            return [r.copy() for r in self.records]
        result = []
        for rec in self.records:
            if all(rec.get(k) == v for k, v in filters.items()):
                result.append(rec.copy())
        return result

    def update_records(self, updates: dict[str, Any], **filters: Any) -> int:
        unknown = [key for key in updates if key not in self.columns]
        if unknown:
            raise UnknownColumnError(f"Поле '{unknown[0]}' не существует")
        updated = 0
        for rec in self.records:
            if all(rec.get(k) == v for k, v in filters.items()):
                for k, v in updates.items():
                    rec[k] = v
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
            if all(rec.get(k) == v for k, v in filters.items()):
                deleted += 1
            else:
                to_keep.append(rec)
        self.records = to_keep
        return deleted

    def clear(self) -> None:
        self.records.clear()

    def rename_column(self, old: str, new: str) -> None:
        if old not in self.columns:
            raise UnknownColumnError(f"Колонка '{old}' не найдена")
        if new in self.columns:
            raise UnknownColumnError(f"Колонка '{new}' уже существует")
        idx = list(self.columns).index(old)
        new_cols = list(self.columns)
        new_cols[idx] = new
        self.columns = tuple(new_cols)
        for rec in self.records:
            if old in rec:
                rec[new] = rec.pop(old)

    def get_record_by_index(self, index: int) -> dict[str, Any]:
        if 0 <= index < len(self.records):
            return self.records[index].copy()
        raise RecordNotFoundError(f"Запись с индексом {index} не найдена")

    def delete_record_by_index(self, index: int) -> None:
        if 0 <= index < len(self.records):
            del self.records[index]
        else:
            raise RecordNotFoundError(f"Запись с индексом {index} не найдена")

    def update_record_by_index(self, index: int, updates: dict[str, Any]) -> None:
        if not (0 <= index < len(self.records)):
            raise RecordNotFoundError(f"Запись с индексом {index} не найдена")
        unknown = [key for key in updates if key not in self.columns]
        if unknown:
            raise UnknownColumnError(f"Неизвестное поле: {unknown[0]}")
        for key, value in updates.items():
            self.records[index][key] = value

    def sort_records(self, column: str, reverse: bool = False) -> list[dict[str, Any]]:
        if column not in self.columns:
            raise UnknownColumnError(f"Колонка '{column}' не найдена")
        return sorted(self.records, key=lambda x: x.get(column), reverse=reverse)