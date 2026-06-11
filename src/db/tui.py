from .backend.memory import *

current = None

def create_hotel_table():
    if not table_exists("Гостиница"):
        create_table("Гостиница", ["id", "имя", "комната", "заезд", "выезд"])
        print("Таблица 'Гостиница' создана")

def print_menu():
    print(f"\n=== {current} ===")
    print("1. Добавить запись")
    print("2. Все записи")
    print("3. Найти")
    print("4. Обновить")
    print("5. Удалить")
    print("6. Сменить таблицу")
    print("0. Выход")

def add_record_dialog():
    fields = get_fields(current)
    row = []
    for f in fields:
        val = input(f"{f}: ")
        if f == "id" or "возраст" in f or "лет" in f:
            val = int(val) if val.isdigit() else val
        row.append(val)
    add_record(current, tuple(row))
    print("Добавлено")

def show_all():
    records = get_all(current)
    if not records:
        print("Нет записей")
    else:
        for r in records:
            print(r)

def find_dialog():
    fields = get_fields(current)
    filters = {}
    for f in fields:
        val = input(f"{f} (Enter - пропустить): ")
        if val:
            if f == "id":
                try:
                    val = int(val)
                except ValueError:
                    print("Ошибка: ID должен быть числом. Фильтр по ID пропущен.")
                    continue
            filters[f] = val
    results = find_records(current, filters)
    if results:
        for r in results:
            print(r)
    else:
        print("Не найдено")

def update_dialog():
    try:
        rid = int(input("ID записи: "))
    except ValueError:
        print("Ошибка: ID должен быть числом")
        return
    fields = get_fields(current)
    new = {}
    for f in fields[1:]:
        val = input(f"Новый {f} (Enter - без изменений): ")
        if val:
            if "возраст" in f or "лет" in f:
                try:
                    val = int(val)
                except ValueError:
                    print(f"Ошибка: поле '{f}' должно быть числом")
                    return
            new[f] = val
    try:
        if update_record(current, rid, new):
            print("Обновлено")
        else:
            print("ID не найден")
    except ValueError as e:
        print(f"Ошибка: {e}")

def delete_dialog():
    try:
        rid = int(input("ID записи: "))
    except ValueError:
        print("Ошибка: ID должен быть числом")
        return
    try:
        if delete_record(current, rid):
            print("Удалено")
        else:
            print("ID не найден")
    except ValueError as e:
        print(f"Ошибка: {e}")

def select_table():
    global current
    tlist = get_tables()
    if not tlist:
        print("Нет таблиц")
        return False
    print("\nДоступные таблицы:")
    for i, t in enumerate(tlist, 1):
        print(f"{i}. {t}")
    choice = input("Выберите номер: ")
    if choice.isdigit() and 1 <= int(choice) <= len(tlist):
        current = tlist[int(choice) - 1]
        return True
    return False

def create_table_dialog():
    global current
    name = input("Имя таблицы: ").strip()
    if not name:
        print("Ошибка: имя таблицы не может быть пустым")
        return
    fields_input = input("Поля через запятую (первое - id): ").strip()
    if not fields_input:
        print("Ошибка: нужно указать хотя бы одно поле")
        return
    fields = [f.strip() for f in fields_input.split(",")]
    if not fields:
        print("Ошибка: список полей пуст")
        return
    if fields[0] != "id":
        print("Ошибка: первое поле должно называться 'id'")
        return
    try:
        create_table(name, fields)
        current = name
        print(f"Таблица '{name}' создана")
    except ValueError as e:
        print(f"Ошибка: {e}")

def run():
    global current
    create_hotel_table()

    while True:
        if not current:
            print("\n=== УПРАВЛЕНИЕ ТАБЛИЦАМИ ===")
            print("1. Создать таблицу")
            print("2. Выбрать таблицу")
            print("0. Выход")
            cmd = input("> ")
            if cmd == "1":
                create_table_dialog()
            elif cmd == "2":
                if select_table():
                    continue
            elif cmd == "0":
                break
            continue

        print_menu()
        cmd = input("> ")

        if cmd == "1":
            add_record_dialog()
        elif cmd == "2":
            show_all()
        elif cmd == "3":
            find_dialog()
        elif cmd == "4":
            update_dialog()
        elif cmd == "5":
            delete_dialog()
        elif cmd == "6":
            current = None
        elif cmd == "0":
            break