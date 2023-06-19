def find_value(collection, aim: str) -> str | None:
    """
    Находит и возвращает значение во вложенных коллекциях
    (словари, списки, кортежи, множества) через рекурсию
    """

    if isinstance(collection, dict):

        for key, value in collection.items():
            if key == aim:
                return value
            elif isinstance(value, (dict, list, tuple, set)):
                result = find_value(value, aim)
                if result:
                    return result
    else:
        try:
            for el in collection:
                if el == aim:
                    return el
                elif isinstance(el, (dict, list, tuple, set)):
                    result = find_value(el, aim)
                    if result:
                        return result
        except TypeError:
            return None


def i_input(*args, **kwargs) -> str:
    """
    Функция для замещения стандартного input,
    позволяет прервать программу на любом этапе ввода,
    если введенное пользователем слово это 'stop'
    """

    result = input(*args, **kwargs)
    if result == "stop":
        print("\nСпасибо и всего доброго!")
        quit()
    return result


def get_binary_answer(text: str) -> str:
    """
    Вспомогательная функция для получения и валидации бинарных ответов
    (да/нет, 0/1, то/это)

    :param text: строка с вопросом, описывающая ситуацию и варианты ответа
    :return: выбранный вариант ответа '0' или '1'
    """

    answer = i_input(f"\n{text}\n")

    while answer not in ("0", "1"):
        answer = i_input("Пожалуйста, введите ответ в формате числа в заданном диапазоне значений.\n")

    return answer

