import requests
import json
from pprint import pprint
from abc import ABC, abstractmethod
from sources.superjob import personal_data
from sources.superjob import urls_sj
from sources.headhunter import urls_hh
import jsonpath_ng as jp


class API(ABC):
    _URL = None
    _PARAMETERS = {}

    def __init__(self, max_quantity=10):
        self.max_quantity = max_quantity

    @property
    def max_quantity(self) -> int:
        return self._max_quantity

    @max_quantity.setter
    def max_quantity(self, max_quantity: int):
        if type(max_quantity) is int and max_quantity >= 0:
            self._max_quantity = max_quantity

    def get_parameters(self) -> dict:
        return self._PARAMETERS

    def set_parameters(self, filters: dict):
        for key, value in filters.items():
            if self._check_parameters(key, value):
                self._PARAMETERS[key] = value

    @abstractmethod
    def _check_parameters(self, key, value):
        pass

    def reset_parameters(self):
        self._PARAMETERS = self.__class__._PARAMETERS

    @classmethod
    @abstractmethod
    def get_filter_dictionary(cls):
        pass

    @staticmethod
    @abstractmethod
    def get_areas_info():
        pass

    @classmethod
    @abstractmethod
    def get_areas_names(cls):
        pass

    @classmethod
    @abstractmethod
    def get_area_id(cls, name: str) -> str:
        pass

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class HeadHunterAPI(API):

    _URL = urls_hh.VACANCIES
    _HOSTS = ("hh.ru",
              "rabota.by",
              "hh1.az",
              "hh.uz",
              "hh.kz",
              "headhunter.ge",
              "headhunter.kg"
              )

    _PARAMETERS = {
            "page": 0,
            "per_page": 100,
            "text": "",
            "host": "hh.ru",
            "only_with_salary": False,

            "search_field": "",
            "experience": "",
            "employment": "",
            "schedule": "",
            "area": "",
            "salary": 0,
            "currency": "",
            "period": 0,
            "order_by": "",
            "locale": ""
        }

    def get_info(self) -> dict:
        parameters = self._PARAMETERS
        with requests.get(self._URL, parameters) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)
        return response

    def get_vacancies(self) -> list:
        vacancies = []

        vacancies.extend(self.get_info()['items'])
        while len(vacancies) < self.max_quantity:
            if self._PARAMETERS["page"] == self.get_info()['pages']:
                break

            self._PARAMETERS["page"] += 1
            vacancies.extend(self.get_info()['items'])

        return vacancies[:self.max_quantity]

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

    def _check_parameters(self, key, value):
        if key not in self._PARAMETERS:
            return False
        if type(value) != type(self._PARAMETERS[key]):
            return False
        if key in ("page", "salary", "period") and value < 0:
            return False
        return True


class SuperJobAPI(API):

    _URL = "https://api.superjob.ru/2.0/vacancies/"
    __MAX_QUANTITY = 500

    _PARAMETERS = {
        "page": 0,
        "count": 100,
        "keyword": "",
        "no_agreement": 1,

        "keywords": {},
        "experience": 0,
        "type_of_work": 0,
        "town": 0,
        "payment_from": 0,
        "payment_to": 0,
        "currency": "",
        "period": 0,
        "order_field": "",
        "order_direction": ""
    }

    @property
    def max_quantity(self) -> int:
        return self._max_quantity

    @max_quantity.setter
    def max_quantity(self, max_quantity: int):
        if type(max_quantity) is int and 0 <= max_quantity <= self.__MAX_QUANTITY:
            self._max_quantity = max_quantity

    def get_info(self):
        parameters = self._PARAMETERS
        headers = {"User-Agent": personal_data.USER_AGENT,
                   "X-Api-App-Id": personal_data.CLIENT_SECRET}

        with requests.get(self._URL, parameters, headers=headers) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)

        return response

    def get_vacancies(self):
        vacancies = []
        total_pages = self.get_info()['total']
        is_divided_entirely = total_pages % self._PARAMETERS["count"] == 0
        last_page = total_pages // self._PARAMETERS["count"] - is_divided_entirely

        vacancies.extend(self.get_info()['objects'])
        while len(vacancies) < self.max_quantity:
            if self._PARAMETERS["page"] == last_page:
                break

            self._PARAMETERS["page"] += 1
            vacancies.extend(self.get_info()['objects'])

        print(len(vacancies))

        return vacancies[:self.max_quantity]

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

    def _check_parameters(self, key, value):
        if key not in self._PARAMETERS:
            return False
        if type(value) != type(self._PARAMETERS[key]):
            return False
        if key in ("page", "experience", "type_of_work", "payment_from",
                   "payment_to", "period", "count") and value < 0:
            return False
        if key == "count" and value > 100:
            return False
        return True


if __name__ == '__main__':
    keywords = {
        "count": 10,
        "keyword": "java",
        "town": "Москва"
    }

    api = SuperJobAPI(30)
    api.set_parameters(keywords)
    pprint(api.get_vacancies())


