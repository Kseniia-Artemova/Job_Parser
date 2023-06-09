import requests


def get_city_codes_hh() -> list:
    url = "https://api.hh.ru/areas"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    raise requests.RequestException("Ошибка при получении списка кодов")


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


def recursive_append_id(data, result_list):
    if isinstance(data, dict):
        if "id" in data:
            result_list.append(data["id"])
        for key, item in data.items():
            recursive_append_id(data, result_list)
    elif isinstance(data, list):
        for item in data:
            recursive_append_id(data, result_list)
