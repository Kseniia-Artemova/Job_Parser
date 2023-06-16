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

    def __init__(self, filters) -> None:
        """
        Инициализатор для объектов класса

        :param filters: объект какого-то из класса фильтров
        """

        self.filters = filters

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, value):
        self._filters = value

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
    def get_vacancies(self, quantity=10) -> list[dict]:
        """Возвращает список вакансий в заданном количестве, если это возможно"""
        pass


class HeadHunterAPI(API):
    """
    Класс для отправки запросов на сайт с вакансиями HeadHunter
    и получения списка вакансий в соответствии с заданными параметрами
    """

    _URL = urls_hh.VACANCIES  # ссылка на сайт для запроса вакансий
    __MAX_QUANTITY = 500  # максимальное допустимое запрашиваемое количество вакансий

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

    def get_vacancies(self, quantity: int = 10) -> list:
        """Возвращает список вакансий в заданном количестве, если это возможно"""

        if type(quantity) is not int or quantity < 0:
            quantity = 10
            print("\nНе соблюдены условия указания количества вакансий:\n"
                  "Количество должно быть выражено целым неотрицательным числом.\n"
                  "Установлен параметр по умолчанию = 10")
        elif quantity > self.__MAX_QUANTITY:
            quantity = 10
            print("\nЗапрошенное количество вакансий превышает максимально возможное (500).\n"
                  "Установлен параметр по умолчанию = 10")

        vacancies = []

        print("\nПодождите, ищу запрошенные вакансии...")

        info = self.get_info()

        vacancies.extend(self.get_info().get('items'))
        while len(vacancies) < quantity:
            if self.filters.page == info.get('pages', 0):
                break

            self.filters.page += 1
            vacancies.extend(self.get_info().get('items'))

        print(f"\nНайдено {len(vacancies[:quantity])} вакансий.\n"
              f"Всего на сайте по заданным параметрам есть {info.get('found', 0)} вакансий.")

        return vacancies[:quantity]


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

    def get_info(self) -> dict:
        """Возвращает ответ на запрос, отправленный на сайт с вакансиями"""

        parameters = self.filters.get_parameters()
        headers = {"User-Agent": personal_data.USER_AGENT,
                   "X-Api-App-Id": personal_data.CLIENT_SECRET}

        with requests.get(self._URL, parameters, headers=headers) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)

        return response

    def get_vacancies(self, quantity: int = 10) -> list:
        """Возвращает список вакансий в заданном количестве, если это возможно"""

        if type(quantity) is not int or quantity < 0:
            quantity = 10
            print("\nНе соблюдены условия указания количества вакансий:\n"
                  "Количество должно быть выражено целым неотрицательным числом.\n"
                  "Установлен параметр по умолчанию = 10")
        elif quantity > self.__MAX_QUANTITY:
            quantity = 10
            print("\nЗапрошенное количество вакансий превышает максимально возможное (500).\n"
                  "Установлен параметр по умолчанию = 10")

        vacancies = []

        print("\nПодождите, ищу запрошенные вакансии...")

        total_vacancies = self.get_info().get('total')
        if total_vacancies == 0:
            return vacancies

        is_divided_entirely = total_vacancies % self.filters.count == 0
        last_page = total_vacancies // self.filters.count - is_divided_entirely

        vacancies.extend(self.get_info().get('objects'))

        while len(vacancies) < quantity:
            if self.filters.page == last_page:
                break

            self.filters.page += 1
            vacancies.extend(self.get_info().get('objects'))

        print(f"\nНайдено {len(vacancies[:quantity])} вакансий.\n"
              f"Всего на сайте по заданным параметрам есть {total_vacancies} вакансий.")

        return vacancies[:quantity]
