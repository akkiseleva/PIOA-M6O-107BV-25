tables = {}

def create_table(name, fields):
    tables[name] = (fields, [])

def get_tables():
    return list(tables.keys())

def get_fields(table):
    return tables[table][0]

def add_record(table, record):
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
    fields = tables[table][0]
    for i, rec in enumerate(tables[table][1]):
        if rec[0] == rec_id:
            new = list(rec)
            for key, val in new_data.items():
                if key in fields:
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
