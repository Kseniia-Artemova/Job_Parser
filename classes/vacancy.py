import requests
import json
from pprint import pprint
from abc import ABC, abstractmethod
import jsonpath_ng as jp


class FindVacancy(ABC):
    _PARAMETERS = {}

    def get_parameters(self) -> dict:
        return self._PARAMETERS

    def reset_parameters(self) -> None:
        self._PARAMETERS = self.__class__._PARAMETERS

    @abstractmethod
    def _set_parameters(self, parameters: dict) -> None:
        pass

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class FindVacancyHH(FindVacancy):
    __URL = "https://api.hh.ru/vacancies"
    __HOSTS = ("hh.ru",
               "rabota.by",
               "hh1.az",
               "hh.uz",
               "hh.kz",
               "headhunter.ge",
               "headhunter.kg"
               )
    _PARAMETERS = {
        "page": 0,
        "per_page": 50,
        "text": "",
        "area": 0,
        "host": "hh.ru"
    }

    def __init__(self, text, quantity, area=0, host="hh.ru"):
        self.quantity = quantity
        parameters = {"text": text,
                      "area": area,
                      "host": host}

        self._set_parameters(parameters)

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, quantity: int):
        if type(quantity) is int and quantity >= 0:
            self.__quantity = quantity

    def _set_parameters(self, parameters: dict) -> None:
        for key, value in parameters.items():
            if self.__check_parameters(key, value):
                self._PARAMETERS[key] = value

    def __check_parameters(self, key: str, value: int | str):
        default_parameters = self.__class__._PARAMETERS
        if key not in default_parameters:
            return False
        if type(value) is not type(default_parameters[key]):
            return False
        if key == "area" and value < 0:
            return False
        if key == "host" and value not in self.__HOSTS:
            return False
        return True

    def get_info(self) -> dict:
        with requests.get(self.__URL, self._PARAMETERS) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)
        return response

    def get_vacancies(self) -> list:
        vacancies = []

        vacancies.extend(self.get_info()['items'])
        while len(vacancies) < self.quantity:
            if self._PARAMETERS["page"] == self.get_info()['pages']:
                break
            self._PARAMETERS["page"] += 1
            vacancies.extend(self.get_info()['items'])

        print(len(vacancies))
        print(len(vacancies[:self.quantity]))

        return vacancies[:self.quantity]

    @staticmethod
    def load_areas_info():
        url = "https://api.hh.ru/areas"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении списка кодов")

    @staticmethod
    def get_city_codes():
        areas = FindVacancyHH.load_areas_info()

        json_exp = jp.parse('$..id')
        matches = json_exp.find(areas)
        codes = [match.value for match in matches]
        return codes

    @staticmethod
    def get_city_id(name):
        regions = FindVacancyHH.load_areas_info()

        json_exp = jp.parse("$..areas[*]")
        matches = [match.value for match in json_exp.find(regions) if match.value.get('name') == name]

        return int(matches[0].get("id"))


class FindVacancySJ(FindVacancy):
    __WEBSITE = "https://www.superjob.ru/"
    _PARAMETERS = {}


if __name__ == '__main__':

    keywords = {
        "text": "NAME:курьер",
        "area": 1,
        "page": 1,
        "per_page": 4
    }
    vac = FindVacancyHH("Курьер", 2, 4)
    FindVacancyHH.get_city_id("Пермь")



