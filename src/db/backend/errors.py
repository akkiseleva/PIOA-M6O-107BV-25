class TableError(Exception):
    pass

class TableNotFoundError(TableError):
    pass

class ColumnNotFoundError(TableError):
    pass

class DuplicateTableError(TableError):
    pass

class EmptyTableNameError(TableError):
    pass

class EmptyColumnsError(TableError):
    pass

class InvalidRecordLengthError(TableError):
    pass

class RecordNotFoundError(TableError):
    pass

class InvalidColumnNameError(TableError):
    pass

class TableAlreadyExistsError(TableError):
    pass

class MissingColumnError(TableError):
    pass

class UnknownColumnError(TableError):
    pass

class InvalidStorageDataError(TableError):
    pass