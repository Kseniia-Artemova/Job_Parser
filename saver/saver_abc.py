import os
from abc import ABC, abstractmethod


class Saver(ABC):
    _ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

    def __init__(self, path_file: tuple) -> None:
        self.path_file = os.path.join(self._ROOT_DIR, *path_file)

    @abstractmethod
    def add_vacancies(self, list_vacancies: list):
        pass

    @abstractmethod
    def write_vacancies(self, list_vacancies: list):
        pass

    @abstractmethod
    def clean_file(self):
        pass

    @abstractmethod
    def load_vacancies(self) -> list:
        pass
