from src.db.backend.memory import DBManager
from src.db.backend.errors import (
    TableNotFoundError,
    ColumnNotFoundError,
    DuplicateTableError,
    EmptyTableNameError,
    EmptyColumnsError,
    RecordNotFoundError,
    InvalidColumnNameError
)


class ConsoleUI:
    def __init__(self, db=None):
        self._current_table: str | None = None
        self._db = db if db is not None else DBManager()

    def run(self) -> None:
        while True:
            if self._current_table:
                print(f"\nТекущая таблица: {self._current_table}")
            self._print_menu()

            action = input("Выберите действие: ").strip()

            if action == "1":
                self._create_table()
            elif action == "2":
                self._select_table()
            elif action == "3":
                self._show_tables()
            elif action == "4":
                self._show_table_info()
            elif action == "5":
                self._add_record()
            elif action == "6":
                self._show_records()
            elif action == "7":
                self._find_records()
            elif action == "8":
                self._update_records()
            elif action in ("9.1", "91"):
                self._delete_by_filter()
            elif action in ("9.2", "92"):
                self._clear_table()
            elif action == "10":
                self._delete_table()
            elif action == "11":
                self._rename_table()
            elif action == "12":
                self._rename_column()
            elif action == "13":
                self._sort_records()
            elif action == "0":
                print("Выход из программы.")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")

    def _print_menu(self) -> None:
        print("\n=== Управление базами данных ===")
        print("1. Создать таблицу")
        print("2. Выбрать таблицу")
        print("3. Список таблиц")
        print("4. Информация о таблице")
        print("5. Добавить запись")
        print("6. Все записи")
        print("7. Поиск")
        print("8. Обновить записи")
        print("9. Удалить записи:")
        print("   9.1. По фильтру")
        print("   9.2. Очистить таблицу")
        print("10. Удалить таблицу")
        print("11. Переименовать таблицу")
        print("12. Переименовать колонку")
        print("13. Сортировка")
        print("0. Выход")

    def _create_table(self) -> None:
        print("\n--- Создание таблицы ---")
        name = input("Имя таблицы: ").strip()
        if not name:
            print("Ошибка: имя не может быть пустым")
            return
        cols_input = input("Колонки через пробел (первое id): ").strip().split()
        if not cols_input:
            print("Ошибка: нужны колонки")
            return
        if cols_input[0] != "id":
            print("Ошибка: первая колонка должна быть id")
            return
        try:
            self._db.create_table(name, cols_input)
            print(f"Таблица '{name}' создана")
        except (DuplicateTableError, EmptyTableNameError, EmptyColumnsError, InvalidColumnNameError) as e:
            print(f"Ошибка: {e}")

    def _select_table(self) -> None:
        tables = self._db.list_tables()
        if not tables:
            print("Нет таблиц")
            return
        print("\nДоступные таблицы:")
        for i, t in enumerate(tables, 1):
            print(f"{i}. {t}")
        choice = input("Выберите номер или имя: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(tables):
                self._current_table = tables[idx]
                print(f"Текущая таблица: {self._current_table}")
                return
        elif choice in tables:
            self._current_table = choice
            print(f"Текущая таблица: {self._current_table}")
            return
        print("Неверный выбор")

    def _show_tables(self) -> None:
        tables = self._db.list_tables()
        if not tables:
            print("Нет таблиц")
            return
        print("\nСписок таблиц:")
        for name in tables:
            try:
                records = self._db.select_records(name)
                print(f"  {name}: {len(records)} записей")
            except Exception:
                print(f"  {name}: ошибка")

    def _show_table_info(self) -> None:
        if not self._current_table:
            print("Сначала выберите таблицу")
            return
        if not self._db.table_exists(self._current_table):
            print(f"Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return
        records = self._db.select_records(self._current_table)
        print(f"\nТаблица: {self._current_table}")
        print(f"Записей: {len(records)}")

    def _add_record(self) -> None:
        if not self._current_table:
            print("Сначала выберите таблицу")
            return
        if not self._db.table_exists(self._current_table):
            print(f"Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return
        print(f"\nДобавление в таблицу '{self._current_table}'")
        record = {}
        print("Вводите пары: колонка → значение")
        print("Чтобы закончить, оставьте название колонки пустым и нажмите Enter")
        while True:
            key = input("Название колонки: ").strip()
            if not key:
                break
            value = input(f"Значение для {key}: ").strip()
            if value:
                record[key] = value
        if not record:
            print("Запись пуста")
            return
        if "id" not in record:
            print("Ошибка: запись должна содержать поле id")
            return
        try:
            self._db.insert_record(self._current_table, record)
            print("Запись добавлена")
        except Exception as e:
            print(f"Ошибка: {e}")

    def _show_records(self) -> None:
        if not self._current_table:
            print("Сначала выберите таблицу")
            return
        if not self._db.table_exists(self._current_table):
            print(f"Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return
        records = self._db.select_records(self._current_table)
        if not records:
            print("Нет записей")
            return
        print(f"\nЗаписи таблицы '{self._current_table}':")
        for i, r in enumerate(records, 1):
            print(f"{i}. {r}")

    def _find_records(self) -> None:
        if not self._current_table:
            print("Сначала выберите таблицу")
            return
        if not self._db.table_exists(self._current_table):
            print(f"Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return
        print(f"\nПоиск в таблице '{self._current_table}'")
        print("Формат: колонка=значение, несколько через пробел")
        filter_str = input("Фильтр (Enter - все записи): ").strip()
        filters = {}
        if filter_str:
            for item in filter_str.split():
                if '=' in item:
                    k, v = item.split('=', 1)
                    filters[k.strip()] = v.strip()
        try:
            records = self._db.select_records(self._current_table, **filters)
            if not records:
                print("Записей не найдено")
                return
            print(f"\nНайдено {len(records)} записей:")
            for i, r in enumerate(records, 1):
                print(f"{i}. {r}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def _update_records(self) -> None:
        if not self._current_table:
            print("Сначала выберите таблицу")
            return
        if not self._db.table_exists(self._current_table):
            print(f"Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return
        print(f"\nОбновление в таблице '{self._current_table}'")
        filter_str = input("Фильтр (колонка=значение): ").strip()
        filters = {}
        if filter_str:
            for item in filter_str.split():
                if '=' in item:
                    k, v = item.split('=', 1)
                    filters[k.strip()] = v.strip()
        try:
            all_records = self._db.select_records(self._current_table)
            cols = self._db.get_columns(self._current_table)
            found_with_indexes = []
            for idx, rec in enumerate(all_records):
                match = True
                for key, val in filters.items():
                    if key not in cols:
                        match = False
                        break
                    if str(rec.get(key)) != str(val):
                        match = False
                        break
                if match:
                    found_with_indexes.append((idx, rec))
            if not found_with_indexes:
                print("Записей не найдено")
                return
            print(f"\nНайдено {len(found_with_indexes)} записей:")
            for i, (_, rec) in enumerate(found_with_indexes, 1):
                print(f"{i}. {rec}")
            print("\nВыберите записи для обновления (номера через пробел, 'all' - все):")
            choice = input("-> ").strip().lower()
            if not choice:
                return
            updates_str = input("Что обновлять (колонка=значение): ").strip()
            updates = {}
            if updates_str:
                for item in updates_str.split():
                    if '=' in item:
                        k, v = item.split('=', 1)
                        updates[k.strip()] = v.strip()
            if not updates:
                print("Нет данных для обновления")
                return
            indexes_to_update = []
            if choice == 'all':
                for idx, _ in found_with_indexes:
                    indexes_to_update.append(idx)
            else:
                for num in choice.split():
                    try:
                        sel_idx = int(num) - 1
                        if 0 <= sel_idx < len(found_with_indexes):
                            real_idx, _ = found_with_indexes[sel_idx]
                            indexes_to_update.append(real_idx)
                    except ValueError:
                        pass
            indexes_to_update = sorted(set(indexes_to_update), reverse=True)
            if not indexes_to_update:
                print("Ничего не выбрано")
                return
            confirm = input("\nВы уверены? (д/н): ").strip().lower()
            if confirm in ('д', 'yes', 'y', 'да'):
                for idx in indexes_to_update:
                    self._db.update_records(self._current_table, updates, **{k: all_records[idx].get(k) for k in cols})
                print(f"Обновлено {len(indexes_to_update)} записей")
        except Exception as e:
            print(f"Ошибка: {e}")

    def _delete_by_filter(self) -> None:
        if not self._current_table:
            print("Сначала выберите таблицу")
            return
        if not self._db.table_exists(self._current_table):
            print(f"Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return
        print(f"\nУдаление по фильтру из таблицы '{self._current_table}'")
        filter_str = input("Фильтр (колонка=значение): ").strip()
        if not filter_str:
            print("Нужен фильтр")
            return
        filters = {}
        for item in filter_str.split():
            if '=' in item:
                k, v = item.split('=', 1)
                filters[k.strip()] = v.strip()
        if not filters:
            print("Некорректный фильтр")
            return
        try:
            all_records = self._db.select_records(self._current_table)
            cols = self._db.get_columns(self._current_table)
            found_with_indexes = []
            for idx, rec in enumerate(all_records):
                match = True
                for key, val in filters.items():
                    if key not in cols:
                        match = False
                        break
                    if str(rec.get(key)) != str(val):
                        match = False
                        break
                if match:
                    found_with_indexes.append((idx, rec))
            if not found_with_indexes:
                print("Записей не найдено")
                return
            print(f"\nНайдено {len(found_with_indexes)} записей:")
            for i, (_, rec) in enumerate(found_with_indexes, 1):
                print(f"{i}. {rec}")
            print("\nВыберите записи для удаления (номера через пробел, 'all' - все):")
            choice = input("-> ").strip().lower()
            if not choice:
                return
            indexes_to_delete = []
            if choice == 'all':
                for idx, _ in found_with_indexes:
                    indexes_to_delete.append(idx)
            else:
                for num in choice.split():
                    try:
                        sel_idx = int(num) - 1
                        if 0 <= sel_idx < len(found_with_indexes):
                            real_idx, _ = found_with_indexes[sel_idx]
                            indexes_to_delete.append(real_idx)
                    except ValueError:
                        pass
            indexes_to_delete = sorted(set(indexes_to_delete), reverse=True)
            if not indexes_to_delete:
                print("Ничего не выбрано")
                return
            confirm = input("\nВы уверены? (д/н): ").strip().lower()
            if confirm in ('д', 'yes', 'y', 'да'):
                for idx in indexes_to_delete:
                    self._db.delete_records(self._current_table, **{k: all_records[idx].get(k) for k in cols})
                print(f"Удалено {len(indexes_to_delete)} записей")
        except Exception as e:
            print(f"Ошибка: {e}")

    def _clear_table(self) -> None:
        if not self._current_table:
            print("Сначала выберите таблицу")
            return
        if not self._db.table_exists(self._current_table):
            print(f"Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return
        count = len(self._db.select_records(self._current_table))
        if count == 0:
            print("Таблица уже пуста")
            return
        confirm = input("\nВы уверены? (д/н): ").strip().lower()
        if confirm in ('д', 'yes', 'y', 'да'):
            self._db.clear_table(self._current_table)
            print("Таблица очищена")

    def _delete_table(self) -> None:
        tables = self._db.list_tables()
        if not tables:
            print("Нет таблиц")
            return
        print("\nДоступные таблицы:")
        for i, t in enumerate(tables, 1):
            print(f"{i}. {t}")
        name = input("Имя таблицы для удаления: ").strip()
        if not name:
            return
        if name not in tables:
            print(f"Таблица '{name}' не найдена")
            return
        confirm = input(f"Вы уверены, что хотите удалить таблицу '{name}'? (д/н): ").strip().lower()
        if confirm in ('д', 'yes', 'y', 'да'):
            self._db.delete_table(name)
            if self._current_table == name:
                self._current_table = None
            print(f"Таблица '{name}' удалена")

    def _rename_table(self) -> None:
        if not self._current_table:
            print("Сначала выберите таблицу")
            return
        print(f"\nПереименование таблицы '{self._current_table}'")
        new_name = input("Новое имя: ").strip()
        if not new_name:
            print("Имя не может быть пустым")
            return
        if new_name == self._current_table:
            print("Имя совпадает со старым")
            return
        try:
            self._db.rename_table(self._current_table, new_name)
            self._current_table = new_name
            print(f"Таблица переименована в '{new_name}'")
        except (TableNotFoundError, DuplicateTableError, EmptyTableNameError) as e:
            print(f"Ошибка: {e}")

    def _rename_column(self) -> None:
        if not self._current_table:
            print("Сначала выберите таблицу")
            return
        if not self._db.table_exists(self._current_table):
            print(f"Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return
        old = input("Старое название колонки: ").strip()
        if not old:
            return
        new = input("Новое название колонки: ").strip()
        if not new:
            return
        try:
            self._db.rename_column(self._current_table, old, new)
            print("Колонка переименована")
        except (TableNotFoundError, ColumnNotFoundError) as e:
            print(f"Ошибка: {e}")

    def _sort_records(self) -> None:
        if not self._current_table:
            print("Сначала выберите таблицу")
            return
        if not self._db.table_exists(self._current_table):
            print(f"Таблица '{self._current_table}' не найдена")
            self._current_table = None
            return
        column = input("Колонка для сортировки: ").strip()
        if not column:
            return
        print("1. По возрастанию")
        print("2. По убыванию")
        order = input("Выберите (1/2): ").strip()
        reverse = (order == "2")
        try:
            result = self._db.sort_records(self._current_table, column, reverse)
            if not result:
                print("Нет записей")
                return
            print(f"\nСортировка по колонке '{column}':")
            for i, r in enumerate(result, 1):
                print(f"{i}. {r}")
        except Exception as e:
            print(f"Ошибка: {e}")


def run() -> None:
    ui = ConsoleUI()
    ui.run()