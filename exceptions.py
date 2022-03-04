STATUSES = []
ERROR_MESSAGE = []


class EndpointUrl(Exception):
    """
    Класс исключения.
    Который срабатывает при отсутствии эндпоинта API.
    """

    pass


class HomeworkNewStatus(Exception):
    """
    Класс исключения.
    Срабатывает когда статус проверки домашки не обновился.
    """

    pass


class DictIsNotEmpty(Exception):
    """
    Класс исключения.
    Срабатывает когда в ответе от API содержится пустой словарь.
    """

    pass


class ResponseNotList(Exception):
    """
    Класс исключения.
    Срабатывает когда в ответе от API
    Под ключом "homeworks",
    домашки приходят не в виде списка.
    """

    pass


def new_status(homework_status):
    """
    Функция ищет в словаре 'STATUSES' статус проверки домашки.
    Если находит, то срабатывает ошибка класса исключения 'HomeworkNewStatus'.
    Если не находит то добавляет в словарь запись с новым  статусом.
    """
    if homework_status in STATUSES:
        raise HomeworkNewStatus
    STATUSES.append(homework_status)


def error_message(message):
    """
    Функция ищет в словаре 'ERROR_MESSAGE' сообщения с ошибками.
    Если находит, то возвращает True.
    Если не находит то добавляет в словарь запись с новой ошибкой.
    """
    if message in ERROR_MESSAGE:
        return True
    ERROR_MESSAGE.append(message)
