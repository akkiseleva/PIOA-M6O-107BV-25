import json
from pathlib import Path
from typing import Any
from .database import DBManager
from .errors import TableNotFoundError, InvalidStorageDataError
from .table import DataTable


class FileDatabase(DBManager):
    def __init__(self, directory: str = "data"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _get_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"

    def _table_exists(self, table_name: str) -> bool:
        return self._get_path(table_name).exists()

    def _list_tables(self) -> list[str]:
        return [p.stem for p in self.directory.glob("*.json")]

    def _load_table(self, table_name: str) -> DataTable:
        path = self._get_path(table_name)
        if not path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise InvalidStorageDataError("Ошибка чтения файла") from e
        if "columns" not in data or "records" not in data:
            raise InvalidStorageDataError("Некорректная структура файла")
        return DataTable(tuple(data["columns"]), data["records"])

    def _save_table(self, table_name: str, table: DataTable) -> None:
        data = {
            "columns": list(table.columns),
            "records": [r.copy() for r in table.records]
        }
        with open(self._get_path(table_name), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _rename_table(self, old: str, new: str) -> None:
        self._get_path(old).rename(self._get_path(new))

    def _delete_table(self, table_name: str) -> None:
        self._get_path(table_name).unlink()