type StudentRecord = tuple[int, str, str, int, str]
Student: list[StudentRecord] = []

def create_record(
        student_id: int,
        first_name: str,
        second_name: str,
        age: int,
        sex: str,
) -> StudentRecord:
    if age < 0:
        raise ValueError("Поле age не может быть отрицательным")
    if any(record[0] == student_id for record in Student):
        raise ValueError(f"Запись с id={student_id} уже существует.")
    new_record: StudentRecord = (
        student_id,
        first_name.strip(),
        second_name.strip(),
        age,
        sex.strip(),
    )
    Student.append(new_record)
    return new_record


def select_record(
    student_id: int | None = None,
    first_name: str | None = None,
    second_name: str | None = None,
    age: int | None = None,
    sex: str | None = None,
) -> list[StudentRecord]:
    if (
        student_id is None
        and first_name is None
        and second_name is None
        and age is None
        and sex is None
    ):
        return Student.copy()
    result: list[StudentRecord] = []
    for record in Student:
        if student_id is not None and record[0] != student_id:
            continue
        if first_name is not None and record[1] != first_name:
            continue
        if second_name is not None and record[2] != second_name:
            continue
        if age is not None and record[3] != age:
            continue
        if sex is not None and record[4] != sex:
            continue
        result.append(record)
    return result


def update_record(
    student_id: int,
    first_name: str | None = None,
    second_name: str | None = None,
    age: int | None = None,
    sex: str | None = None,
) -> StudentRecord | None:
    for i, record in enumerate(Student):
        if record[0] == student_id:
            new_record = (
                student_id,
                first_name if first_name is not None else record[1],
                second_name if second_name is not None else record[2],
                age if age is not None else record[3],
                sex if sex is not None else record[4],
            )
            Student[i] = new_record
            return new_record
    raise ValueError(f"Запись с id={student_id} не найдена")

def delete_record(student_id: int) -> bool:
    for i, record in enumerate(Student):
        if record[0] == student_id:
            Student.pop(i)
            return True
    return False


