import requests
import json
from pprint import pprint
from abc import ABC, abstractmethod
from sources.superjob import personal_data
from sources.superjob import urls_sj
from sources.headhunter import urls_hh
import jsonpath_ng as jp
from types import NoneType


class API(ABC):
    _URL = None
    _PARAMETERS = {}

    def __init__(self, max_quantity=10):
        self.max_quantity = max_quantity
        self.set_filter_dictionary()
        self.set_parameters()

    @property
    def max_quantity(self) -> int:
        return self._max_quantity

    @max_quantity.setter
    def max_quantity(self, max_quantity: int):
        if type(max_quantity) is int and max_quantity >= 0:
            self._max_quantity = max_quantity

    def get_parameters(self) -> dict:
        return self._PARAMETERS

    def set_parameters(self):
        if self._PARAMETERS == self.__class__._PARAMETERS:
            filters = self.choice_filters()
            for key, value in filters.items():
                if self._check_parameters(key, value):
                    self._PARAMETERS[key] = value
        else:
            print("Сначала сбросьте фильтр при помощи reset_parameters().")

    @abstractmethod
    def _check_parameters(self, key, value):
        pass

    def reset_parameters(self):
        self._PARAMETERS = self.__class__._PARAMETERS

    @abstractmethod
    def set_filter_dictionary(self):
        pass

    @staticmethod
    @abstractmethod
    def get_areas_info():
        pass

    @abstractmethod
    def get_areas_names(self):
        pass

    @abstractmethod
    def get_area_id(self, name: str) -> str:
        pass

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass

    @abstractmethod
    def choice_filters(self):
        pass


class HeadHunterAPI(API):
    _URL = urls_hh.VACANCIES
    _HOSTS = {"0": "hh.ru",
              "1": "rabota.by",
              "2": "hh1.az",
              "3": "hh.uz",
              "4": "hh.kz",
              "5": "headhunter.ge",
              "6": "headhunter.kg"
              }

    _PARAMETERS = {
        "page": 0,
        "per_page": 100,

        "text": "",
        "host": "hh.ru",
        "only_with_salary": False,
        "locale": "RU",

        "search_field": "",
        "experience": "",
        "employment": "",
        "schedule": "",
        "area": "",
        "salary": 0,
        "currency": "",
        "period": 0,
        "order_by": ""
    }

    def get_info(self) -> dict:
        parameters = {key: value for key, value in self._PARAMETERS.items() if value}
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

    def set_filter_dictionary(self):
        url = urls_hh.FILTER_DICTIONARY
        response = requests.get(url)
        if response.status_code != 200:
            raise requests.RequestException("Ошибка при получении словаря дополнительных значений")
        self._filter_dictionary = response.json()

    @staticmethod
    def get_areas_info() -> dict:
        url = urls_hh.AREA_CODES
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении списка кодов")

    def get_areas_names(self) -> list[str]:
        areas = self.get_areas_info()

        json_exp = jp.parse('$..name')
        matches = json_exp.find(areas)
        names = [match.value for match in matches]

        return names

    def get_area_id(self, name: str) -> str:
        name = name.capitalize()
        regions = self.get_areas_info()

        json_exp = jp.parse("$..areas[*]")
        matches = [match.value for match in json_exp.find(regions) if match.value.get('name') == name]

        if matches:
            return matches[0].get("id")

    def _check_parameters(self, key, value):
        if key not in self._PARAMETERS:
            return False
        if type(value) not in (type(self._PARAMETERS[key]), NoneType):
            return False
        if key in ("page", "salary", "period") and (value is not None) and (value < 0):
            return False
        return True

    def choice_filters(self):

        filters = {}

        filters["text"] = self.ask_text()
        filters["host"] = self.ask_host()
        filters["only_with_salary"] = self.ask_only_with_salary()
        filters["search_field"] = self.ask_search_field()
        filters["experience"] = self.ask_experience()
        filters["employment"] = self.ask_employment()
        filters["schedule"] = self.ask_schedule()
        filters["area"] = self.ask_area()
        filters["salary"] = self.ask_salary()
        if filters["salary"]:
            filters["currency"] = self.ask_currency()
        filters["period"] = self.ask_period()
        filters["order_by"] = self.ask_order_by()
        filters["locale"] = self.ask_locale()

        return filters

    @staticmethod
    def ask_text():
        return input("\nВведите слово или фразу для ключевого запроса:\n")

    def ask_host(self):
        hosts = "\n".join([f"{num} - {host}" for num, host in self._HOSTS.items()])
        choice = input(f"\nКакое доменное имя сайта использовать для запроса?"
                       f"По умолчанию используется 'hh.ru'.\n"
                       f"Доступны варианты:\n{hosts}\n"
                       f"Введите номер выбранного домена или '0' чтобы оставить значение по умолчанию.\n")
        while choice not in self._HOSTS:
            choice = input("Неверный номер. Пожалуйста, повторите попытку:\n")
        return self._HOSTS[choice]

    @staticmethod
    def ask_only_with_salary():
        answer = input("\nВыводить только вакансии с указанием заработной платы? "
                       "Пожалуйста, введите ответ в формате 'да'/'нет'.\n").lower()
        while answer not in ("да", "нет"):
            answer = input("Пожалуйста, введите ответ в формате 'да'/'нет'.\n").lower()
        return True if answer == "да" else False

    def ask_search_field(self):
        fields = self._filter_dictionary["vacancy_search_fields"]
        variations = "\n".join([f"{i} - {field['name']}" for i, field in enumerate(fields)])

        choice = input(f"\nВыберите, где искать ключевое слово:\n{variations}\n"
                       f"По умолчанию поиск везде. Введите номер, либо нажмите Enter для пропуска.\n")

        while choice != "":
            if choice.isdigit() and 0 <= int(choice) < len(fields):
                break

            choice = input(f"Введите существующий номер, либо нажмите Enter для пропуска.\n"
                           f"{variations}\n")

        return fields[int(choice)]["id"] if choice.isdigit() else None

    def ask_experience(self):
        experience = self._filter_dictionary["experience"]
        variations = "\n".join([f"{i} - {field['name']}" for i, field in enumerate(experience)])
        choice = input(f"\nВыберите требуемый опыт работы:\n{variations}\n"
                       f"Введите номер, либо нажмите Enter для пропуска.\n")

        while choice != "":
            if choice.isdigit() and 0 <= int(choice) < len(experience):
                break

            choice = input(f"Введите существующий номер, либо нажмите Enter для пропуска.\n"
                           f"{variations}\n")

        return experience[int(choice)]["id"] if choice.isdigit() else None

    def ask_employment(self):
        employment = self._filter_dictionary["employment"]
        variations = "\n".join([f"{i} - {field['name']}" for i, field in enumerate(employment)])
        choice = input(f"\nВыберите требуемую занятость:\n{variations}\n"
                       f"Введите номер, либо нажмите Enter для пропуска.\n")

        while choice != "":
            if choice.isdigit() and 0 <= int(choice) < len(employment):
                break

            choice = input(f"Введите существующий номер, либо нажмите Enter для пропуска.\n"
                           f"{variations}\n")

        return employment[int(choice)]["id"] if choice.isdigit() else None

    def ask_schedule(self):
        schedule = self._filter_dictionary["schedule"]
        variations = "\n".join([f"{i} - {field['name']}" for i, field in enumerate(schedule)])
        choice = input(f"\nВыберите требуемый график:\n{variations}\n"
                       f"Введите номер, либо нажмите Enter для пропуска.\n")

        while choice != "":
            if choice.isdigit() and 0 <= int(choice) < len(schedule):
                break

            choice = input(f"Введите существующий номер, либо нажмите Enter для пропуска.\n"
                           f"{variations}\n")

        return schedule[int(choice)]["id"] if choice.isdigit() else None

    def ask_area(self):
        all_areas = self.get_areas_names()
        name = input("\nВведите город или населенный пункт, либо нажмите Enter для пропуска:\n")

        while name != "":

            if name == "list":
                print()
                print(*sorted(all_areas), sep="\n")
                print()
                name = input("Попробуйте ещё раз:\n")

            elif name not in all_areas:
                print(f"Не могу найти такой населенный пункт.\n"
                      f"Для вызова списка городов введите 'list'.\n"
                      f"Соблюдайте регистр.")
                name = input("Попробуйте ещё раз:\n")

            else:
                break

        return self.get_area_id(name)

    @staticmethod
    def ask_salary():
        salary = input("\nВведите сумму зарплаты для поиска (целое положительное число),\n"
                       "либо нажмите Enter для пропуска:\n")
        while salary != "":
            if salary.isdigit():
                salary = int(salary)
                break
            salary = input("Сумма должна быть целым положительным числом без каких-либо знаков.\n"
                           "Попробуйте еще раз:\n")

        return salary if salary else None

    def ask_currency(self):
        currency = [field for field in self._filter_dictionary["currency"] if field["in_use"]]
        variations = "\n".join([f"{i} - {field['name']}" for i, field in enumerate(currency)])
        choice = input(f"\nВыберите валюту зарплаты:\n{variations}\n"
                       f"Введите номер, либо нажмите Enter для пропуска.\n")

        while choice != "":
            if choice.isdigit() and 0 <= int(choice) < len(currency):
                break

            choice = input(f"Введите существующий номер, либо нажмите Enter для пропуска.\n"
                           f"{variations}\n")

        return currency[int(choice)]["code"] if choice.isdigit() else None

    @staticmethod
    def ask_period():
        period = input("\nВведите количество дней, в пределах которых производится поиск по вакансиям,\n"
                       "либо нажмите Enter для пропуска:\n")
        while period != "":
            if period.isdigit():
                period = int(period)
                break
            period = input("Количество дней должно быть целым положительным числом без каких-либо знаков.\n"
                           "Попробуйте еще раз:\n")

        return period if period else None

    def ask_order_by(self):
        order_by = [field for field in self._filter_dictionary["vacancy_search_order"] if field["id"] != "distance"]
        variations = "\n".join([f"{i} - {field['name']}" for i, field in enumerate(order_by)])
        choice = input(f"\nВыберите способ сортировки:\n{variations}\n"
                       f"Введите номер, либо нажмите Enter для пропуска.\n")

        while choice != "":
            if choice.isdigit() and 0 <= int(choice) < len(order_by):
                break

            choice = input(f"Введите существующий номер, либо нажмите Enter для пропуска.\n"
                           f"{variations}\n")

        return order_by[int(choice)]["id"] if choice.isdigit() else None

    @staticmethod
    def ask_locale():
        answer = input("\nТребуется ли изменить язык локализации на английский?\n"
                       "По умолчанию стоит русская локализация. "
                       "Пожалуйста, введите ответ в формате 'да'/'нет'.\n").lower()

        while answer not in ("да", "нет"):
            answer = input("Пожалуйста, введите ответ в формате 'да'/'нет'.\n").lower()

        return "EN" if answer == "да" else "RU"


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
        "currency": "rub",
        "period": 0,
        "order_field": "date",
        "order_direction": "desc"
    }

    @property
    def max_quantity(self) -> int:
        return self._max_quantity

    @max_quantity.setter
    def max_quantity(self, max_quantity: int):
        if type(max_quantity) is int and 0 <= max_quantity <= self.__MAX_QUANTITY:
            self._max_quantity = max_quantity
        else:
            print("Запрошенное количество вакансий превышает максимально возможное (500).\n"
                  "Установлен параметр по умолчанию = 10")

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

    def set_filter_dictionary(self):
        url = urls_sj.FILTER_DICTIONARY
        response = requests.get(url)
        if response.status_code != 200:
            raise requests.RequestException("Ошибка при получении словаря дополнительных значений")
        self._filter_dictionary = response.json()

    @staticmethod
    def get_areas_info() -> dict:
        url = urls_sj.AREA_CODES
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении списка кодов")

    def get_areas_names(self) -> list[str]:
        areas = self.get_areas_info()

        json_exp = jp.parse('$..title')
        matches = json_exp.find(areas)
        codes = [match.value for match in matches]

        return codes

    def get_area_id(self, name: str) -> int:
        name = name.capitalize()
        regions = self.get_areas_info()

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

    def choice_filters(self):

        filter = {}

        filter["keyword"] = self.ask_keyword()
        filter["no_agreement"] = self.ask_no_agreement()
        filter["experience"] = self.ask_experience()
        filter["type_of_work"] = self.ask_type_of_work()
        filter["town"] = self.ask_town()
        filter["payment_from"], filter["payment_to"] = self.ask_payment_from_to()
        filter["period"] = self.ask_period()
        filter["order_field"] = self.ask_order_field()
        filter["order_direction"] = self.ask_order_direction()

        return filter

    @staticmethod
    def ask_keyword():
        key = input("\nВведите слово или фразу для ключевого запроса:\n")
        keys = len(key.strip().split())
        return key if keys == 1 else keys

    @staticmethod
    def ask_no_agreement():
        answer = input("\nТребуется ли исключить вакансии с окладом «по договоренности»?\n"
                       "Пожалуйста, введите ответ в формате 'да'/'нет'.\n").lower()

        while answer not in ("да", "нет"):
            answer = input("Пожалуйста, введите ответ в формате 'да'/'нет'.\n").lower()

        return 1 if answer == "да" else 0

    # @staticmethod
    # def ask_keywords():
    #     keywords = {
    #         "srws": {
    #             "1": "должность",
    #             "2": "название компании",
    #             "3": "должностные обязанности",
    #             "4": "требования к квалификации",
    #             "5": "условия работы",
    #             "10": "весь текст вакансии"
    #         },
    #         "skwc": {
    #             "and": "все слова",
    #             "or": "хотя бы одно слово",
    #             "particular": "точную фразу",
    #             "nein": "слова-исключения",
    #         }
    #     }
    #
    #     srws = "\n".join([f"{key} - {value}" for key, value in keywords["srws"].items()])
    #     answer_srws = input(f"\nВыберите, где искать ключевые слова. Введите число, соответсвующее ответу,\n"
    #                         f"либо нажмите Enter для пропуска:\n{srws}\n")
    #     while answer_srws not in keywords["srws"]:
    #         if answer_srws == "":
    #             break
    #         answer_srws = input("Введите число, соответсвующее ответу,\n"
    #                             "либо нажмите Enter для пропуска:\n")
    #
    #     skwc = "\n".join([f"{key} - {value}" for key, value in keywords["skwc"].items()])
    #     answer_skwc = input(f"\nВыберите, как искать ключевые слова. Введите опцию, соответсвующую ответу,\n"
    #                         f"либо нажмите Enter для пропуска:\n{skwc}\n").lower()
    #     while answer_skwc not in keywords["skwc"]:
    #         if answer_skwc == "":
    #             break
    #         answer_skwc = input("Введите опцию, соответсвующую ответу,\n"
    #                             "либо нажмите Enter для пропуска:\n").lower()
    #
    #     return answer_srws, answer_skwc

    def ask_experience(self):
        experience = self._filter_dictionary["experience"]
        variation = "\n".join([f"{key} - {value}" for key, value in experience.items()])

        answer = input(f"\nВведите подходящее числовое значение для выбора опыта работы, "
                       f"либо нажмите Enter для пропуска:\n{variation}\n")

        while answer not in experience:
            if answer == "":
                break
            answer = input("Пожалуйста, введите ответ в формате числа, либо нажмите Enter для пропуска:\n")

        return answer

    def ask_type_of_work(self):
        type_of_work = self._filter_dictionary["type_of_work"]
        variation = "\n".join([f"{key} - {value}" for key, value in type_of_work.items()])

        answer = input(f"\nВведите подходящее числовое значение для выбора типа занятости, "
                       f"либо нажмите Enter для пропуска:\n{variation}\n")

        while answer not in type_of_work:
            if answer == "":
                break
            answer = input("Пожалуйста, введите ответ в формате числа, либо нажмите Enter для пропуска:\n")

        return answer

    def ask_town(self):
        all_towns = self.get_areas_names()
        name = input("\nВведите город или населенный пункт, либо нажмите Enter для пропуска:\n")

        while name != "":

            if name == "list":
                print()
                print(*sorted(all_towns), sep="\n")
                print()
                name = input("Попробуйте ещё раз:\n")

            elif name not in all_towns:
                print(f"Не могу найти такой населенный пункт.\n"
                      f"Для вызова списка городов введите 'list'.\n"
                      f"Соблюдайте регистр.")
                name = input("Попробуйте ещё раз:\n")

            else:
                break

        return self.get_area_id(name)

    @staticmethod
    def ask_payment_from_to():
        payment_from = input("\nВведите нижнюю границу суммы зарплаты для поиска (целое положительное число),\n"
                             "либо нажмите Enter для пропуска:\n")
        while payment_from != "":
            if payment_from.isdigit():
                payment_from = int(payment_from)
                break
            payment_from = input("Сумма должна быть целым положительным числом без каких-либо знаков.\n"
                                 "Попробуйте еще раз:\n")

        payment_to = input("\nВведите верхнюю границу суммы зарплаты для поиска (целое положительное число),\n"
                           "либо нажмите Enter для пропуска:\n")
        while payment_to != "":
            if payment_to.isdigit():
                payment_to = int(payment_to)
                break
            payment_to = input("Сумма должна быть целым положительным числом без каких-либо знаков.\n"
                               "Попробуйте еще раз:\n")

        try:
            return sorted((payment_from, payment_to))
        except TypeError:
            return payment_from, payment_to

    def ask_period(self):
        period = self._filter_dictionary["period"]
        variation = "\n".join([f"{key} - {value}" for key, value in period.items()])

        answer = input(f"\nВведите подходящее числовое значение для выбора периода публикации, "
                       f"либо нажмите Enter для пропуска:\n{variation}\n")

        while answer not in period:
            if answer == "":
                break
            answer = input("Пожалуйста, введите ответ в формате числа, либо нажмите Enter для пропуска:\n")

        return answer

    @staticmethod
    def ask_order_field():
        answer = input("\nСортировать вакансии по параметру '0 - дата' или '1 - сумма оклада'?\n"
                       "Пожалуйста, введите соответствующее числовое значение.\n").lower()

        while answer not in ("0", "1"):
            answer = input("Пожалуйста, введите ответ в формате числа.\n").lower()

        return "date" if answer == "0" else "payment"

    @staticmethod
    def ask_order_direction():
        answer = input("\nВ каком направлении следует сортировать вакансии?\n"
                       "Пожалуйста, введите соответствующее числовое значение:\n"
                       "0 - в прямом\n"
                       "1 - в обратном\n")

        while answer not in ("0", "1"):
            answer = input("Пожалуйста, введите ответ в формате числа.\n")

        return "asc" if answer == "0" else "desc"


if __name__ == '__main__':
    keywords = {
        "count": 10,
        "keyword": "java",
        "town": "Москва"
    }

    a = SuperJobAPI()
    print(a.get_info())
