from .backend.memory import *

def run():
    current = None
    while True:
        if not current:
            tables = get_tables()
            if not tables:
                cmd = input("1 - создать, 0 - выход: ")
                if cmd == "1":
                    name = input("Имя: ")
                    cols = input("Колонки: ").replace(" ", "").split(",")
                    new_table(name, cols)
                    current = name
                elif cmd == "0":
                    break
            else:
                for i, t in enumerate(tables):
                    print(f"{i + 1}. {t}")
                print("0. Назад")
                cmd = input("> ")
                if cmd.isdigit() and 0 < int(cmd) <= len(tables):
                    current = tables[int(cmd) - 1]
            continue
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Показать записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить запись")
        print("6. Сменить таблицу")
        print("0. Выход")
        cmd = input("> ")
        if cmd == "1":
            row = []
            for c in base[current]["cl"]:
                if c == "id":
                    row.append(int(input(f"{c}: ")))
                else:
                    row.append(input(f"{c}: "))
            add_rows(current, tuple(row))
        elif cmd == "2":
            for r in get_rows(current):
                print(r)
        elif cmd == "3":
            s = {}
            for c in base[current]["cl"]:
                v = input(f"{c}: ")
                if v:
                    if c == "id":
                        s[c] = int(v)
                    else:
                        s[c] = v
            for r in find_rows(current, s):
                print(r)
        elif cmd == "4":
            rid = int(input("ID: "))
            new = {}
            for c in base[current]["cl"][1:]:
                v = input(f"{c}: ")
                if v:
                    if c in ["age", "год"]:
                        new[c] = int(v)
                    else:
                        new[c] = v
            if update_row(current, rid, new):
                print("Обновлено")
            else:
                print("Ошибка")
        elif cmd == "5":
            rid = int(input("ID: "))
            if delete_row(current, rid):
                print("Удалено")
            else:
                print("Ошибка")
        elif cmd == "6":
            current = None
        elif cmd == "0":
            break