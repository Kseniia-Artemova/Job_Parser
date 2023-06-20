from abc import ABC, abstractmethod


class Filter(ABC):
    """Абстрактный класс для описания фильтра запроса"""

    _AREA_CODES_URL: str  # ссылка на ресурс, возвращающий весь перечень регионов/городов
    _FILTER_DICTIONARY_URL: str  # ссылка на ресурс, возвращающий словари со значениями для фильтра

    def __init__(self):
        """
        Инициализатор фильтра. Устанавливает значения фильтра по умолчанию,
        либо запрашивает более специализированную настройку у пользователя
        """

        self.parameters = {}

    def get_all_parameters(self) -> dict:
        """Возвращает все параметры фильтра в формате словаря"""

        return self.parameters

    def get_request_parameters(self) -> dict:

        request_parameters = {key: value for key, value in self.parameters.items() if value is not None}

        return request_parameters

    @abstractmethod
    def set_request_parameters(self):
        pass

    @abstractmethod
    def get_filtering_parameters(self):
        pass

    @abstractmethod
    def set_filtering_parameters(self):
        pass

    @abstractmethod
    def get_filter_dictionary(self) -> dict:
        """Возвращает словарь, содержащий надлежащие значения для фильтра"""
        pass

    @abstractmethod
    def get_areas_info(self) -> dict | list[dict]:
        """
        Возвращает коллекцию, содержащую информацию о городах и регионах,
        которые можно указывать для поиска
        """
        pass

    @abstractmethod
    def get_areas_names(self) -> list:
        """
        Возвращает список, содержащий города и регионы,
        которые можно указывать для поиска
        """
        pass

    @abstractmethod
    def get_area_id(self, name: str) -> str | int:
        """
        Возвращает id, который кодирует переданный
        функции город или регион
        """
        pass