tables = {}

def create_table(name, fields):
    if name in tables:
        raise ValueError(f"Таблица '{name}' уже существует")
    if not fields:
        raise ValueError("Таблица должна содержать хотя бы одно поле")
    tables[name] = (fields, [])

def get_tables():
    return list(tables.keys())

def get_fields(table):
    if table not in tables:
        raise ValueError(f"Таблица '{table}' не существует")
    return tables[table][0]


def add_record(table, record):
    if table not in tables:
        raise ValueError(f"Таблица '{table}' не существует")
    fields = tables[table][0]
    if len(record) != len(fields):
        raise ValueError(f"Ожидается {len(fields)} полей, получено {len(record)}")
    tables[table][1].append(record)
    return record

def get_all(table):
    return tables[table][1].copy()

def find_records(table, filters):
    fields = tables[table][0]
    result = []
    for rec in tables[table][1]:
        match = True
        for key, val in filters.items():
            if key not in fields:
                match = False
                break
            idx = fields.index(key)
            if rec[idx] != val:
                match = False
                break
        if match:
            result.append(rec)
    return result

def update_record(table, rec_id, new_data):
    if table not in tables:
        raise ValueError(f"Таблица '{table}' не существует")

    fields = tables[table][0]

    # Проверяем, что все ключи из new_data существуют в таблице
    for key in new_data:
        if key not in fields:
            raise ValueError(f"Поле '{key}' не существует в таблице '{table}'. Доступные поля: {fields}")

    for i, rec in enumerate(tables[table][1]):
        if rec[0] == rec_id:
            new = list(rec)
            for key, val in new_data.items():
                new[fields.index(key)] = val
            tables[table][1][i] = tuple(new)
            return True
    return False

def delete_record(table, rec_id):
    for i, rec in enumerate(tables[table][1]):
        if rec[0] == rec_id:
            tables[table][1].pop(i)
            return True
    return False

def table_exists(name):
    return name in tables
