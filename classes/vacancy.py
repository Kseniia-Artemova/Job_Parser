from dataclasses import dataclass
import requests
from abc import ABC, abstractmethod
from sources.headhunter import urls_hh
from sources.superjob import urls_sj
import jsonpath_ng as jp
from pprint import pprint


class Vacancy(ABC):

    @classmethod
    @abstractmethod
    def build_filter(cls, values: dict):
        pass

    @abstractmethod
    def get_parameters(self):
        pass

    @classmethod
    @abstractmethod
    def get_filter_dictionary(cls) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def get_areas_info() -> dict:
        pass

    @classmethod
    @abstractmethod
    def get_areas_names(cls):
        pass

    @classmethod
    @abstractmethod
    def get_area_id(cls, name):
        pass


@dataclass
class VacancyHeadHunter(Vacancy):

    HOSTS = ("hh.ru",
             "rabota.by",
             "hh1.az",
             "hh.uz",
             "hh.kz",
             "headhunter.ge",
             "headhunter.kg"
             )

    # обязательные параметры
    page: int = 0       # номер страницы
    per_page: int = 100     # количество элементов
    text: str = ""      # переданное значение ищется в полях вакансии, указанных в параметре search_field
    host: str = "hh.ru"     # доменное имя сайта
    only_with_salary: bool = False      # показывать вакансии только с указанием зарплаты, по умолчанию False

    # дополнительные параметры
    search_field: str | None = None     # область поиска
    experience: str | None = None       # опыт работы
    employment: str | None = None       # тип занятости
    schedule: str | None = None     # график работы
    area: str | None = None     # регион, можно указать несколько значений
    salary: int | None = None       # размер заработной платы
    currency: str | None = None     # код валюты, имеет смысл указывать только вместе с salary
    period: int | None = None       # количество дней, в пределах которых производится поиск по вакансиям
    order_by: str | None = None     # сортировка списка вакансий
    locale: str | None = None       # идентификатор локали

    @classmethod
    def get_filter_dictionary(cls) -> dict:
        url = urls_hh.FILTER_DICTIONARY
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении словаря дополнительных значений")

    @staticmethod
    def get_areas_info() -> dict:
        url = urls_hh.AREA_CODES
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении списка кодов")

    @classmethod
    def get_areas_names(cls) -> list[str]:
        areas = cls.get_areas_info()

        json_exp = jp.parse('$..name')
        matches = json_exp.find(areas)
        names = [match.value for match in matches]

        return names

    @classmethod
    def get_area_id(cls, name: str) -> str:
        name = name.capitalize()
        regions = cls.get_areas_info()

        json_exp = jp.parse("$..areas[*]")
        matches = [match.value for match in json_exp.find(regions) if match.value.get('name') == name]

        if matches:
            return matches[0].get("id")

    @classmethod
    def build_filter(cls, values: dict) -> "VacancyHeadHunter":
        return cls(**values)

    def get_parameters(self) -> dict:
        return self.__dict__


@dataclass
class VacancySuperJob(Vacancy):

    # обязательные параметры
    # page: int = 0
    # per_page: int = 100
    keyword: str = ""       # ключевое слово, ищет по всей вакансии

    # only_with_salary: bool = False
    no_agreement: int = 1       # не показывать оклад «по договоренности» (когда установлено значение 1)

    # дополнительные параметры

    # search_field: str | None = None
    keywords: dict | None = None        # расширенный поиск ключевых слов

    # experience: str | None = None
    experience: int | None = None       # опыт работы

    # employment: str | None = None
    type_of_work: int | None = None     # тип занятости

    schedule: str | None = None
    area: str | None = None

    # salary: int | None = None
    payment_from: int | None = None     # сумма оклада от
    payment_to: int | None = None       # сумма оклада до

    currency: str | None = None

    # period: int | None = None
    period: int | None = None       # период публикации

    # order_by: str | None = None
    order_field: str | None = None      # сортировка: по дате публикации/по сумме оклада
    order_direction: str | None = None      # направление сортировки: прямая/обратная

    locale: str | None = None

    @classmethod
    def get_filter_dictionary(cls) -> dict:
        url = urls_sj.FILTER_DICTIONARY
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении словаря дополнительных значений")

    @staticmethod
    def get_areas_info() -> dict:
        url = urls_sj.AREA_CODES
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении списка кодов")

    @classmethod
    def get_areas_names(cls) -> list[str]:
        areas = cls.get_areas_info()

        json_exp = jp.parse('$..title')
        matches = json_exp.find(areas)
        codes = [match.value for match in matches]

        return codes

    @classmethod
    def get_area_id(cls, name: str) -> int:
        name = name.capitalize()
        regions = cls.get_areas_info()

        json_exp = jp.parse("$..towns[*]")
        matches = [match.value for match in json_exp.find(regions) if match.value.get('title') == name]

        if matches:
            return matches[0].get("id")




