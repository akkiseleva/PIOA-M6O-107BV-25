base = {}
def new_table(name, columns):
    base[name] = {"cl": columns, "rows": []}

def get_tables():
    return list(base.keys())

def add_rows(table, row):
    base[table]["rows"].append(row)

def get_rows(table):
    return base[table]["rows"]

def find_rows(table, search):
    result = []
    cols = base[table]["cl"]
    for row in base[table]["rows"]:
        ok = True
        for key, val in search.items():
            if row[cols.index(key)] != val:
                ok = False
                break
        if ok:
            result.append(row)
    return result

def update_row(table, row_id, new):
    cols = base[table]["cl"]
    for i, row in enumerate(base[table]["rows"]):
        if row[0] == row_id:
            new_row = list(row)
            for key, val in new.items():
                new_row[cols.index(key)] = val
            base[table]["rows"][i] = tuple(new_row)
            return True
    return False

def delete_row(table, row_id):
    for i, row in enumerate(base[table]["rows"]):
        if row[0] == row_id:
            base[table]["rows"].pop(i)
            return True
    return False






