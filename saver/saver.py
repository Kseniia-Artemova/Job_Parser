import json
import os
from abc import ABC, abstractmethod
from vacancy.vacancy_hh import VacancyHeadHunter
from vacancy.vacancy_sj import VacancySuperJob
from filter.filter_hh import FilterHH
from filter.filter_sj import FilterSJ


class Saver(ABC):

    _PATH_FILE = None

    def __init__(self) -> None:

        root_dir = os.path.dirname(os.path.dirname(__file__))
        path_file = os.path.join(root_dir, *self._PATH_FILE)

        self.path_file = path_file

    @property
    def path_file(self) -> str:
        return self._path_file

    @path_file.setter
    def path_file(self, path_file) -> None:
        if not os.path.exists(path_file):
            raise FileNotFoundError("Файл по указанному пути не существует")
        self._path_file = path_file

    @abstractmethod
    def add_vacancies(self, dict_vacancies: list):
        pass

    @abstractmethod
    def write_vacancies(self, dict_vacancies: list):
        pass

    @abstractmethod
    def clean_file(self):
        pass

    @abstractmethod
    def load_all_vacancies(self):
        pass

    @abstractmethod
    def load_definite_vacancies(self, filter_obj_hh: FilterHH = None, filter_obj_sj: FilterSJ = None):
        pass


class JSONSaver(Saver):

    _PATH_FILE = "vacancies", "vacancies.json"

    def add_vacancies(self, dict_vacancies: list) -> None:
        with open(self.path_file, "a", encoding="utf-8") as json_file:
            json.dump(dict_vacancies, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))
            json_file.write("\n")

        print(f"\nВакансии добавлены в файл {self.path_file}")

    def write_vacancies(self, dict_vacancies: list) -> None:
        with open(self.path_file, "w", encoding="utf-8") as json_file:
            json.dump(dict_vacancies, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))

        print(f"\nВакансии записаны в файл {self.path_file}")

    def clean_file(self) -> None:
        with open(self.path_file, "w", encoding="utf-8") as json_file:
            pass

        print(f"\nИнформация была стёрта из файла {self.path_file} ")

    def load_all_vacancies(self) -> list:
        with open(self.path_file, "r", encoding="utf-8") as json_file:
            vacancies = json.load(json_file)

        list_vacancies = []

        for vacancy in vacancies:
            if "hh.ru" in vacancy.get("url", ""):
                vacancy = VacancyHeadHunter(vacancy)
            elif "superjob.ru" in vacancy.get("link", ""):
                vacancy = VacancySuperJob(vacancy)
            else:
                continue
            list_vacancies.append(vacancy)

        return list_vacancies

    def load_definite_vacancies(self, filter_obj_hh: FilterHH = None, filter_obj_sj: FilterSJ = None) -> list:

        if filter_obj_hh:
            print("\nУстановка фильтра для HeadHunter")
            filter_obj_hh.set_filtering_parameters()
        if filter_obj_sj:
            print("\nУстановка фильтра для SuperJob")
            filter_obj_sj.set_filtering_parameters()

        with open(self.path_file, "r", encoding="utf-8") as json_file:
            vacancies = json.load(json_file)

        list_vacancies = []

        for vacancy in vacancies:
            if "hh.ru" in vacancy.get("url", ""):
                if filter_obj_hh and filter_obj_hh.compare_parameters(vacancy):
                    vacancy = VacancyHeadHunter(vacancy)
                    list_vacancies.append(vacancy)
            elif "superjob.ru" in vacancy.get("link", ""):
                if filter_obj_sj and filter_obj_sj.compare_parameters(vacancy):
                    vacancy = VacancySuperJob(vacancy)
                    list_vacancies.append(vacancy)

        return list_vacancies
