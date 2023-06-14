import requests
import json
from pprint import pprint
from abc import ABC, abstractmethod
from sources.superjob import personal_data
from sources.superjob import urls_sj
from sources.headhunter import urls_hh
import jsonpath_ng as jp
from types import NoneType
from dataclasses import dataclass


class Filter(ABC):
    _AREA_CODES = None
    _FILTER_DICTIONARY = None

    @abstractmethod
    def get_filter_dictionary(self) -> dict:
        pass

    @abstractmethod
    def get_areas_info(self) -> dict:
        pass

    @abstractmethod
    def get_areas_names(self):
        pass

    @abstractmethod
    def get_area_id(self, name):
        pass

    @abstractmethod
    def set_obligatory_parameters(self):
        pass

    @abstractmethod
    def set_extra_parameters(self):
        pass

    @abstractmethod
    def get_parameters(self):
        pass


class FilterHH(Filter):
    _AREA_CODES = urls_hh.AREA_CODES
    _FILTER_DICTIONARY = urls_hh.FILTER_DICTIONARY

    _HOSTS = {"0": "hh.ru",
              "1": "rabota.by",
              "2": "hh1.az",
              "3": "hh.uz",
              "4": "hh.kz",
              "5": "headhunter.ge",
              "6": "headhunter.kg"
              }

    def __init__(self):

        self._filter_dictionary = self.get_filter_dictionary()
        self._areas_info = self.get_areas_info()
        self._areas_names = self.get_areas_names()

        # обязательные параметры
        self.page: int = 0  # номер страницы
        self.per_page: int = 100  # количество элементов

        self.text: str = ""  # переданное значение ищется в полях вакансии, указанных в параметре search_field
        self.host: str = "hh.ru"  # доменное имя сайта
        self.only_with_salary: bool = False  # показывать вакансии только с указанием зарплаты, по умолчанию False
        self.locale: str = "RU"  # идентификатор локали

        self.set_obligatory_parameters()

        # дополнительные параметры
        self.experience: str | None = None  # опыт работы
        self.employment: str | None = None  # тип занятости
        self.schedule: str | None = None  # график работы
        self.currency: str | None = None  # код валюты, имеет смысл указывать только вместе с salary
        self.order_by: str | None = None  # сортировка списка вакансий

        self.area: str | None = None  # регион
        self.salary: int | None = None  # размер заработной платы
        self.period: int | None = None  # количество дней, в пределах которых производится поиск по вакансиям

        self.set_extra_parameters()

    def get_filter_dictionary(self) -> dict:
        url = self._FILTER_DICTIONARY
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении словаря дополнительных значений")

    def get_areas_info(self) -> dict:
        url = self._AREA_CODES
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении списка кодов")

    def get_areas_names(self) -> list[str]:
        areas = self._areas_info

        json_exp = jp.parse('$..name')
        matches = json_exp.find(areas)
        names = [match.value for match in matches]

        return names

    def get_area_id(self, name: str) -> str:
        regions = self._areas_info

        json_exp = jp.parse("$..areas[*]")
        matches = [match.value for match in json_exp.find(regions) if match.value.get('name') == name]

        if matches:
            return matches[0].get("id")

    def set_obligatory_parameters(self):

        self.text = self.ask_text()
        self.host = self.ask_host()
        self.only_with_salary = self.ask_only_with_salary()
        self.locale = self.ask_locale()

    def set_extra_parameters(self):

        self.area = self.ask_area()

        self.experience = self.ask_experience()
        self.employment = self.ask_employment()
        self.schedule = self.ask_schedule()

        self.salary = self.ask_salary()
        if self.salary:
            self.currency = self.ask_currency()
        self.period = self.ask_period()
        self.order_by = self.ask_order_by()

    @staticmethod
    def ask_text():
        return input("\nВведите слово или фразу для ключевого запроса:\n")

    def ask_host(self):
        hosts = "\n".join([f"{num} - {host}" for num, host in self._HOSTS.items()])
        choice = input(f"\nКакое доменное имя сайта использовать для запроса? "
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

    @staticmethod
    def ask_locale():
        answer = input("\nТребуется ли изменить язык локализации на английский?\n"
                       "По умолчанию стоит русская локализация. "
                       "Пожалуйста, введите ответ в формате 'да'/'нет'.\n").lower()

        while answer not in ("да", "нет"):
            answer = input("Пожалуйста, введите ответ в формате 'да'/'нет'.\n").lower()

        return "EN" if answer == "да" else "RU"

    @staticmethod
    def _check_right_answer(parameter: list, text: str):

        variations = "\n".join([f"{i} - {field['name']}" for i, field in enumerate(parameter)])
        choice = input(f"\n{text}\n{variations}\n"
                       f"Введите номер, либо нажмите Enter для пропуска.\n")

        while choice != "":
            if choice.isdigit() and 0 <= int(choice) < len(parameter):
                return choice

            choice = input(f"Введите существующий номер, либо нажмите Enter для пропуска.\n"
                           f"{variations}\n")

        return choice

    def ask_experience(self):
        experience = self._filter_dictionary["experience"]
        text = "Выберите требуемый опыт работы:"
        answer = self._check_right_answer(experience, text)

        return experience[int(answer)]["id"] if answer.isdigit() else None

    def ask_employment(self):
        employment = self._filter_dictionary["employment"]
        text = "Выберите требуемую занятость:"
        answer = self._check_right_answer(employment, text)

        return employment[int(answer)]["id"] if answer.isdigit() else None

    def ask_schedule(self):
        schedule = self._filter_dictionary["schedule"]
        text = "Выберите требуемый график:"
        answer = self._check_right_answer(schedule, text)

        return schedule[int(answer)]["id"] if answer.isdigit() else None

    def ask_currency(self):
        currency = [field for field in self._filter_dictionary["currency"] if field["in_use"]]
        text = "Выберите валюту зарплаты:"
        answer = self._check_right_answer(currency, text)

        return currency[int(answer)]["code"] if answer.isdigit() else None

    def ask_order_by(self):
        order_by = [field for field in self._filter_dictionary["vacancy_search_order"] if field["id"] != "distance"]
        text = "Выберите способ сортировки:"
        answer = self._check_right_answer(order_by, text)

        return order_by[int(answer)]["id"] if answer.isdigit() else None

    def ask_area(self):
        all_areas = sorted(self._areas_names)
        name = input("\nВведите город или населенный пункт, либо нажмите Enter для пропуска:\n")

        while name != "":

            if name == "list":
                print()
                print(*all_areas, sep="\n")
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
    def _check_right_number(text):

        answer = input(f"\nВведите {text} (целое положительное число),\n"
                       f"либо нажмите Enter для пропуска:\n")

        while answer != "":
            if answer.isdigit():
                answer = int(answer)
                break
            answer = input("Введите целое положительное число без каких-либо знаков.\n"
                           "Попробуйте еще раз:\n")

        return answer

    def ask_salary(self):
        text = "сумму зарплаты для поиска"
        salary = self._check_right_number(text)

        return salary if salary else None

    def ask_period(self):
        text = "количество дней, в пределах которых производится поиск по вакансиям"
        period = self._check_right_number(text)

        return period if period else None

    def get_parameters(self) -> dict:
        parameters = {
            "page": self.page,
            "per_page": self.per_page,
            "text": self.text,
            "host": self.host,
            "only_with_salary": self.only_with_salary,
            "locale": self.locale,

            "experience": self.experience,
            "employment": self.employment,
            "schedule": self.schedule,
            "currency": self.currency,
            "order_by": self.order_by,
            "area": self.area,
            "salary": self.salary,
            "period": self.period
        }
        return parameters


class FilterSJ(Filter):
    _AREA_CODES = urls_sj.AREA_CODES
    _FILTER_DICTIONARY = urls_sj.FILTER_DICTIONARY

    def __init__(self):

        self._filter_dictionary = self.get_filter_dictionary()
        self._areas_info = self.get_areas_info()
        self._areas_names = self.get_areas_names()

        # обязательные параметры
        self.page: int = 0
        self.count: int = 100
        self.keyword: str = ""  # ключевое слово, ищет по всей вакансии
        self.no_agreement: int = 1  # не показывать оклад «по договоренности» (когда установлено значение 1)
        self.currency: str = "rub"  # валюта

        self.order_field: str = "date"  # сортировка: по дате публикации/по сумме оклада
        self.order_direction: str = "desc"  # направление сортировки: прямая/обратная

        self.set_obligatory_parameters()

        # дополнительные параметры
        self.town: int | None = None  # ID города
        self.experience: int | None = None  # опыт работы
        self.type_of_work: int | None = None  # тип занятости
        self.payment_from: int | None = None  # сумма оклада от
        self.payment_to: int | None = None  # сумма оклада до
        self.period: int | None = None  # период публикации

        self.set_extra_parameters()

    def get_filter_dictionary(self) -> dict:
        url = self._FILTER_DICTIONARY
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении словаря дополнительных значений")

    def get_areas_info(self) -> dict:
        url = self._AREA_CODES
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении списка кодов")

    def get_areas_names(self) -> list[str]:
        areas = self._areas_info

        json_exp = jp.parse('$..title')
        matches = json_exp.find(areas)
        codes = [match.value for match in matches]

        return codes

    def get_area_id(self, name: str) -> int:
        regions = self._areas_info

        json_exp = jp.parse("$..towns[*]")
        matches = [match.value for match in json_exp.find(regions) if match.value.get('title') == name]

        if matches:
            return matches[0].get("id")

    def set_obligatory_parameters(self):

        self.keyword = self.ask_keyword()
        self.no_agreement = self.ask_no_agreement()
        self.order_field = self.ask_order_field()
        self.order_direction = self.ask_order_direction()

    def set_extra_parameters(self):

        self.town = self.ask_town()
        self.experience = self.ask_experience()
        self.type_of_work = self.ask_type_of_work()
        self.payment_from, self.payment_to = self.ask_payment_from_to()
        self.period = self.ask_period()

    @staticmethod
    def ask_keyword():
        return input("\nВведите слово или фразу для ключевого запроса:\n")

    @staticmethod
    def ask_no_agreement():
        answer = input("\nТребуется ли исключить вакансии с окладом «по договоренности»?\n"
                       "Пожалуйста, введите ответ в формате 'да'/'нет'.\n").lower()

        while answer not in ("да", "нет"):
            answer = input("Пожалуйста, введите ответ в формате 'да'/'нет'.\n").lower()

        return 1 if answer == "да" else 0

    @staticmethod
    def _check_binary_answer(text):
        answer = input(f"\n{text}\n").lower()

        while answer not in ("0", "1"):
            answer = input("Пожалуйста, введите ответ в формате числа.\n").lower()

        return answer

    def ask_order_field(self):
        text = "Сортировать вакансии по параметру '0 - дата' или '1 - сумма оклада'?\n" \
               "Пожалуйста, введите соответствующее числовое значение."

        answer = self._check_binary_answer(text)

        return "date" if answer == "0" else "payment"

    def ask_order_direction(self):
        text = "В каком направлении следует сортировать вакансии?\n" \
               "Пожалуйста, введите соответствующее числовое значение:\n" \
               "0 - в прямом\n" \
               "1 - в обратном"

        answer = self._check_binary_answer(text)

        return "asc" if answer == "0" else "desc"

    @staticmethod
    def _check_right_answer(parameter, text):
        variation = "\n".join([f"{key} - {value}" for key, value in parameter.items()])

        answer = input(f"\nВведите подходящее числовое значение для выбора {text}, "
                       f"либо нажмите Enter для пропуска:\n{variation}\n")

        while answer not in parameter:
            if answer == "":
                break
            answer = input("Пожалуйста, введите ответ в формате числа, либо нажмите Enter для пропуска:\n")

        return answer

    def ask_experience(self):
        experience = self._filter_dictionary["experience"]
        text = "опыта работы"

        answer = self._check_right_answer(experience, text)

        return answer if answer else None

    def ask_type_of_work(self):
        type_of_work = self._filter_dictionary["type_of_work"]
        text = "типа занятости"

        answer = self._check_right_answer(type_of_work, text)

        return answer if answer else None

    def ask_period(self):
        period = self._filter_dictionary["period"]
        text = "периода публикации"

        answer = self._check_right_answer(period, text)

        return answer if answer else None

    def ask_town(self):
        all_towns = sorted(self._areas_names)
        name = input("\nВведите город или населенный пункт, либо нажмите Enter для пропуска:\n")

        while name != "":

            if name == "list":
                print()
                print(*all_towns, sep="\n")
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
    def _get_number(text):

        payment = input(f"\nВведите {text} суммы зарплаты для поиска (целое положительное число),\n"
                        f"либо нажмите Enter для пропуска:\n")

        while payment != "":
            if payment.isdigit():
                payment = int(payment)
                break
            payment = input("Сумма должна быть целым положительным числом без каких-либо знаков.\n"
                            "Попробуйте еще раз:\n")

        return payment if payment else None

    def ask_payment_from_to(self):
        text = "нижнюю границу"
        payment_from = self._get_number(text)

        text = "верхнюю границу"
        payment_to = self._get_number(text)

        try:
            return sorted((payment_from, payment_to))
        except TypeError:
            return payment_from, payment_to

    def get_parameters(self) -> dict:
        parameters = {
            "page": self.page,
            "count": self.count,
            "keyword": self.keyword,
            "no_agreement": self.no_agreement,
            "currency": self.currency,
            "order_field": self.order_field,
            "order_direction": self.order_direction,

            "town": self.town,
            "experience": self.experience,
            "type_of_work": self.type_of_work,
            "payment_from": self.payment_from,
            "payment_to": self.payment_to,
            "period": self.period,
        }

        return parameters


a = FilterSJ()
print(a.get_parameters())