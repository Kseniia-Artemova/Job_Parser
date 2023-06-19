import requests
import json

from abc import ABC, abstractmethod
from types import NoneType

from sources.superjob import personal_data
from sources.superjob import urls_sj
from sources.headhunter import urls_hh

from filter.filter_hh import FilterHH
from filter.filter_sj import FilterSJ


class API(ABC):
    """
    Абстрактный класс для отправки запросов на сайт с вакансиями
    и получения списка вакансий в соответствии с заданными параметрами
    """

    _URL = None  # ссылка на сайт для запроса вакансий
    _MAX_QUANTITY = 500  # максимальное допустимое запрашиваемое количество вакансий

    def __init__(self, request_filter, quantity=10) -> None:
        """
        Инициализатор для объектов класса

        :param request_filter: объект какого-то из класса фильтров
        :param quantity: желаемое количество вакансий
        """

        self.request_filter = request_filter
        self.quantity = quantity

    @property
    def request_filter(self):
        return self._request_filter

    @request_filter.setter
    def request_filter(self, value):
        self._request_filter = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):

        if type(value) is int and 0 <= value < 500:
            self._quantity = value
        else:
            self._quantity = 10
            print("\nНе соблюдены условия указания количества вакансий:\n"
                  "Количество должно быть выражено целым неотрицательным числом\n"
                  "и не превышать максимальное возможное значение = 500\n"
                  "Установлен параметр по умолчанию = 10")

    def get_parameters(self) -> dict:
        """Возвращает установленные параметры фильтра"""

        return self.request_filter.get_request_parameters()

    @abstractmethod
    def get_info(self) -> list[dict]:
        """Возвращает ответ на запрос, отправленный на сайт с вакансиями"""
        pass

    @abstractmethod
    def get_vacancies(self) -> list[dict]:
        """Возвращает список вакансий в заданном количестве, если это возможно"""
        pass


class HeadHunterAPI(API):
    """
    Класс для отправки запросов на сайт с вакансиями HeadHunter
    и получения списка вакансий в соответствии с заданными параметрами
    """

    _URL = urls_hh.VACANCIES  # ссылка на сайт для запроса вакансий

    @property
    def request_filter(self) -> FilterHH | None:
        return self._request_filter

    @request_filter.setter
    def request_filter(self, value: FilterHH | None) -> None:
        """Установка фильтра, после проверки на принадлежность к подходящему классу"""

        if isinstance(value, (FilterHH, NoneType)):
            self._request_filter = value

    def get_info(self) -> dict:
        """Возвращает ответ на запрос, отправленный на сайт с вакансиями"""

        parameters = self.request_filter.get_request_parameters()

        with requests.get(self._URL, parameters) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)

        return response

    def get_vacancies(self) -> list:
        """Возвращает список вакансий в заданном количестве, если это возможно"""

        vacancies = []

        print("\nПодождите, ищу запрошенные вакансии...")

        info = self.get_info()

        vacancies.extend(self.get_info().get('items'))
        while len(vacancies) < self.quantity:
            if self.request_filter.parameters["page"] == info.get('pages', 0):
                break

            self.request_filter.parameters["page"] += 1
            vacancies.extend(self.get_info().get('items'))

        print(f"\nНайдено {len(vacancies[:self.quantity])} вакансий.\n"
              f"Всего на сайте по заданным параметрам есть {info.get('found', 0)} вакансий.")

        return vacancies[:self.quantity]


class SuperJobAPI(API):
    """
    Класс для отправки запросов на сайт с вакансиями SuperJob
    и получения списка вакансий в соответствии с заданными параметрами
    """

    _URL = urls_sj.VACANCIES  # ссылка на сайт для запроса вакансий

    @property
    def request_filter(self) -> FilterSJ | None:
        return self._request_filter

    @request_filter.setter
    def request_filter(self, value: FilterSJ | None) -> None:
        """Установка фильтра, после проверки на принадлежность к подходящему классу"""

        if isinstance(value, (FilterSJ, NoneType)):
            self._request_filter = value

    def get_info(self) -> dict:
        """Возвращает ответ на запрос, отправленный на сайт с вакансиями"""

        parameters = self.request_filter.get_request_parameters()
        headers = {"User-Agent": personal_data.USER_AGENT,
                   "X-Api-App-Id": personal_data.CLIENT_SECRET}

        with requests.get(self._URL, parameters, headers=headers) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)

        return response

    def get_vacancies(self) -> list:
        """Возвращает список вакансий в заданном количестве, если это возможно"""

        vacancies = []

        print("\nПодождите, ищу запрошенные вакансии...")

        total_vacancies = self.get_info().get('total')
        if total_vacancies == 0:
            return vacancies

        is_divided_entirely = total_vacancies % self.request_filter.parameters["count"] == 0
        last_page = total_vacancies // self.request_filter.parameters["count"] - is_divided_entirely

        vacancies.extend(self.get_info().get('objects'))

        while len(vacancies) < self.quantity:
            if self.request_filter.parameters["page"] == last_page:
                break

            self.request_filter.parameters["page"] += 1
            vacancies.extend(self.get_info().get('objects'))

        print(f"\nНайдено {len(vacancies[:self.quantity])} вакансий.\n"
              f"Всего на сайте по заданным параметрам есть {total_vacancies} вакансий.")

        return vacancies[:self.quantity]
