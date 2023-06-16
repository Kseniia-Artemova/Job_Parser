import json
import os
from abc import ABC, abstractmethod


class Saver(ABC):

    def __init__(self, path):
        self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError("Файл по указанному пути не существует")
        self._path = path

    @abstractmethod
    def add_vacancies(self, dict_vacancies):
        pass

    @abstractmethod
    def rewrite_vacancies(self, dict_vacancies):
        pass

    @abstractmethod
    def clean_file(self, dict_vacancies):
        pass

    @abstractmethod
    def load_all_vacancies(self):
        pass

    @abstractmethod
    def load_definite_vacancies(self, dict_filters):
        pass


class JSONSaver(Saver):

    def add_vacancies(self, dict_vacancies):
        with open(self.path, "aw", encoding="utf-8") as json_file:
            json.dump(dict_vacancies, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))

        print(f"Вакансии добавлены в файл {self.path}")

    def rewrite_vacancies(self, dict_vacancies):
        with open(self.path, "w", encoding="utf-8") as json_file:
            json.dump(dict_vacancies, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))

        print(f"Вакансии записаны в файл {self.path}")

    def clean_file(self, dict_vacancies):
        with open(self.path, "w", encoding="utf-8") as json_file:
            pass

        print(f"Информация была стёрта из файла {self.path} ")

    def load_all_vacancies(self):
        with open(self.path, "r", encoding="utf-8") as json_file:
            vacancies = json.load(json_file)

    # Аргумент object_hook используется для преобразования JSON объектов в пользовательский тип данных. Он вызывается для каждого словаря в JSON данных.
    #
    # Например, предположим, что вы хотите преобразовать JSON объекты в экземпляры пользовательского класса. Вот пример:
    #
    # python
    # Copy code
    # import json
    #
    # class Person:
    #     def __init__(self, name, age):
    #         self.name = name
    #         self.age = age
    #
    #     def __repr__(self):
    #         return f'Person(name={self.name}, age={self.age})'
    #
    # def dict_to_person(dict_obj):
    #     return Person(dict_obj['name'], dict_obj['age'])
    #
    # json_data = '{"name": "John Doe", "age": 30}'
    # data = json.loads(json_data, object_hook=dict_to_person)
    #
    # print(data)
    # В этом примере, json.loads возвращает экземпляр класса Person, созданный из данных в JSON строке. Функция dict_to_person вызывается для каждого словаря в JSON данных, и она возвращает экземпляр класса Person, созданный из этого словаря.
