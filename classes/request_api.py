import requests
import json

from abc import ABC, abstractmethod
from types import NoneType

from sources.superjob import personal_data
from sources.superjob import urls_sj
from sources.headhunter import urls_hh

from classes.filter import FilterHH, FilterSJ


class API(ABC):
    """
    Абстрактный класс для отправки запросов на сайт с вакансиями
    и получения списка вакансий в соответствии с заданными параметрами
    """

    _URL = None  # ссылка на сайт для запроса вакансий

    def __init__(self, filters, max_quantity: int) -> None:
        """
        Инициализатор для объектов класса

        :param filters: объект какого-то из класса фильтров
        :param max_quantity: желаемое количество вакансий
        """

        self.filters = filters
        self._max_quantity = 10
        self.max_quantity = max_quantity

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, value):
        self._filters = value

    @property
    def max_quantity(self) -> int:
        return self._max_quantity

    @max_quantity.setter
    def max_quantity(self, value: int) -> None:
        if type(value) is int and value >= 0:
            self._max_quantity = value

    def get_parameters(self) -> dict:
        """Возвращает установленные параметры фильтра"""

        return self.filters.get_parameters()

    def set_parameters(self, filters) -> None:
        """Установить фильтр"""

        self.filters = filters

    def reset_parameters(self) -> None:
        """Сбросить фильтр"""

        self.filters = None

    @abstractmethod
    def get_info(self) -> list[dict]:
        """Возвращает ответ на запрос, отправленный на сайт с вакансиями"""
        pass

    @abstractmethod
    def get_vacancies(self) -> list[dict]:
        """Возвращает список вакансий"""
        pass


class HeadHunterAPI(API):
    """
    Класс для отправки запросов на сайт с вакансиями HeadHunter
    и получения списка вакансий в соответствии с заданными параметрами
    """

    _URL = urls_hh.VACANCIES  # ссылка на сайт для запроса вакансий

    @property
    def filters(self) -> FilterHH | None:
        return self._filters

    @filters.setter
    def filters(self, value: FilterHH | None) -> None:
        """Установка фильтра, после проверки на принадлежность к подходящему классу"""

        if isinstance(value, (FilterHH, NoneType)):
            self._filters = value

    def get_info(self) -> dict:
        """Возвращает ответ на запрос, отправленный на сайт с вакансиями"""

        parameters = self.filters.get_parameters()
        with requests.get(self._URL, parameters) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)
        return response

    def get_vacancies(self) -> list:
        """Возвращает список вакансий"""

        vacancies = []

        vacancies.extend(self.get_info()['items'])
        while len(vacancies) < self.max_quantity:
            if self.filters.page == self.get_info()['pages']:
                break

            self.filters.page += 1
            vacancies.extend(self.get_info()['items'])

        return vacancies[:self.max_quantity]


class SuperJobAPI(API):
    """
    Класс для отправки запросов на сайт с вакансиями SuperJob
    и получения списка вакансий в соответствии с заданными параметрами
    """

    _URL = urls_sj.VACANCIES  # ссылка на сайт для запроса вакансий
    __MAX_QUANTITY = 500  # максимальное допустимое запрашиваемое количество вакансий

    @property
    def filters(self) -> FilterSJ | None:
        return self._filters

    @filters.setter
    def filters(self, value: FilterSJ | None) -> None:
        """Установка фильтра, после проверки на принадлежность к подходящему классу"""

        if isinstance(value, (FilterSJ, NoneType)):
            self._filters = value

    @property
    def max_quantity(self) -> int:
        return self._max_quantity

    @max_quantity.setter
    def max_quantity(self, value: int) -> None:
        """Устанавливает запрашиваемое количество вакансий,
        если оно больше нуля и меньше максимального допустимого значения"""

        if type(value) is int and 0 <= value <= self.__MAX_QUANTITY:
            self._max_quantity = value
        elif value > self.__MAX_QUANTITY:
            print("Запрошенное количество вакансий превышает максимально возможное (500).\n"
                  "Установлен параметр по умолчанию = 10")
        else:
            print("Отрицательное число использовать нельзя.\n"
                  "Установлен параметр по умолчанию = 10")

    def get_info(self) -> dict:
        """Возвращает ответ на запрос, отправленный на сайт с вакансиями"""

        parameters = self.filters.get_parameters()
        headers = {"User-Agent": personal_data.USER_AGENT,
                   "X-Api-App-Id": personal_data.CLIENT_SECRET}

        with requests.get(self._URL, parameters, headers=headers) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)

        return response

    def get_vacancies(self) -> list:
        """Возвращает список вакансий"""

        vacancies = []

        total_vacancies = self.get_info()['total']
        if total_vacancies == 0:
            return vacancies

        is_divided_entirely = total_vacancies % self.filters.count == 0
        last_page = total_vacancies // self.filters.count - is_divided_entirely

        vacancies.extend(self.get_info()['objects'])

        while len(vacancies) < self.max_quantity:
            if self.filters.page == last_page:
                break

            self.filters.page += 1
            vacancies.extend(self.get_info()['objects'])

        return vacancies[:self.max_quantity]
