import requests
import json
from pprint import pprint
from abc import ABC, abstractmethod
from sources.superjob.secret_key import ID, SECRET_KEY
from sources.headhunter import urls_hh
from classes.vacancy import VacancyHeadHunter, VacancySuperJob


class API(ABC):
    _URL = None

    @abstractmethod
    def set_parameters(self, vacancy):
        pass

    @abstractmethod
    def reset_parameters(self):
        pass

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class HeadHunterAPI(API):
    _URL = urls_hh.VACANCIES

    def __init__(self, max_quantity=10):
        self.__vacancy = None
        self.max_quantity = max_quantity

    @property
    def max_quantity(self):
        return self.__max_quantity

    @max_quantity.setter
    def max_quantity(self, max_quantity: int):
        if type(max_quantity) is int and max_quantity >= 0:
            self.__max_quantity = max_quantity

    @property
    def vacancy(self):
        return self.__vacancy

    def get_info(self) -> dict:
        parameters = self.vacancy.get_parameters()
        with requests.get(self._URL, parameters) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)
        return response

    def get_vacancies(self) -> list:
        vacancies = []

        vacancies.extend(self.get_info()['items'])
        while len(vacancies) < self.max_quantity:
            if self.vacancy.page == self.get_info()['pages']:
                break
            self.vacancy.page += 1
            vacancies.extend(self.get_info()['items'])

        return vacancies[:self.max_quantity]

    def set_parameters(self, vacancy):
        if isinstance(vacancy, VacancyHeadHunter):
            self.__vacancy = vacancy

    def reset_parameters(self):
        self.__vacancy = None


class SuperJobAPI(API):
    _URL = "https://api.superjob.ru/2.0/vacancies/"
    __MAX_QUANTITY = 500
    _PARAMETERS = {
        "keyword": "",

    }

    def _set_parameters(self, parameters: dict):
        pass

    def get_info(self):
        pass

    def get_vacancies(self):
        pass


if __name__ == '__main__':

    keywords = {
        "text": "NAME:курьер",
        "area": 1,
        "page": 1,
        "per_page": 4
    }





