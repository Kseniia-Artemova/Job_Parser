from dataclasses import dataclass
import requests
from abc import ABC, abstractmethod
from sources.headhunter import urls_hh
from sources.superjob import urls_sj
import jsonpath_ng as jp
from pprint import pprint
from functools import total_ordering


class Vacancy(ABC):

    def __init__(self, vacancy_dict: dict) -> None:
        for key, value in vacancy_dict.items():
            setattr(self, key, value)

    def get_parameters(self) -> dict:
        return self.__dict__

    def _check_currency(self, other):
        rub = ("rub", "RUR")

        if isinstance(other, Vacancy):
            if self.get_currency() == other.get_currency():
                return True
            elif self.get_currency() in rub and other.get_currency() in rub:
                return True

            return False

    def __eq__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() == other.get_min_salary()

    def __ne__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() != other.get_min_salary()

    def __lt__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() < other.get_min_salary()

    def __le__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() <= other.get_min_salary()

    def __gt__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() > other.get_min_salary()

    def __ge__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() >= other.get_min_salary()

    @abstractmethod
    def get_min_salary(self):
        pass

    @abstractmethod
    def get_currency(self):
        pass


class VacancyHeadHunter(Vacancy):
    pass

    def get_min_salary(self):
        salary_min = self.__dict__.get("salary").get("from")
        salary_max = self.__dict__.get("salary").get("to")
        if any((salary_min, salary_max)):
            salary = [salary for salary in (salary_min, salary_max) if type(salary) is int]
            return min(salary)

    def get_currency(self):
        return self.__dict__.get("salary").get("currency")


class VacancySuperJob(Vacancy):

    def get_min_salary(self):
        salary_min = self.__dict__.get("payment_from")
        salary_max = self.__dict__.get("payment_to")
        if any((salary_min, salary_max)):
            salary = [salary for salary in (salary_min, salary_max) if type(salary) is int]
            return min(salary)

    def get_currency(self):
        return self.__dict__.get("currency")





