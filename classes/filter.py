import requests
from abc import ABC, abstractmethod
import jsonpath_ng as jp

from sources.superjob import urls_sj
from sources.headhunter import urls_hh

from tools.utils import i_input


class Filter(ABC):
    """Абстрактный класс для описания фильтра запроса"""

    _AREA_CODES_URL: str  # ссылка на ресурс, возвращающий весь перечень регионов/городов
    _FILTER_DICTIONARY_URL: str  # ссылка на ресурс, возвращающий словари со значениями для фильтра

    def __init__(self) -> None:
        """
        Инициализатор фильтра. Устанавливает значения фильтра по умолчанию,
        либо запрашивает более специализированную настройку у пользователя
        """

        text = "Настроить фильтр или использовать параметры по умолчанию?\n" \
               "0 - использовать параметры по умолчанию\n" \
               "1 - настроить фильтр самостоятельно"

        answer = self._check_binary_answer(text)

        if answer == "1":
            self.set_obligatory_parameters()
            self.set_extra_parameters()

    @staticmethod
    def _check_binary_answer(text: str) -> str:
        """
        Вспомогательная функция для валидации бинарных ответов
        (да/нет, 0/1, то/это)

        :param text: строка с вопросом, описывающая ситуацию и варианты ответа
        :return: выбранный вариант ответа '0' или '1'
        """

        answer = i_input(f"\n{text}\n")

        while answer not in ("0", "1"):
            answer = i_input("Пожалуйста, введите ответ в формате числа в заданном диапазоне значений.\n")

        return answer

    def get_parameters(self) -> dict:
        """
        Возвращает словарь, содержащий только те значения,
        которые не равны None
        """

        return {key: value for key, value in self.get_all_parameters().items() if value is not None}

    @abstractmethod
    def get_filter_dictionary(self) -> dict:
        """Возвращает словарь, содержащий надлежащие значения для фильтра"""
        pass

    @abstractmethod
    def get_areas_info(self) -> dict | list[dict]:
        """
        Возвращает коллекцию, содержащую информацию о городах и регионах,
        которые можно указывать для поиска
        """
        pass

    @abstractmethod
    def get_areas_names(self) -> list:
        """
        Возвращает список, содержащий города и регионы,
        которые можно указывать для поиска
        """
        pass

    @abstractmethod
    def get_area_id(self, name: str) -> str | int:
        """
        Возвращает id, который кодирует переданный
        функции город или регион
        """
        pass

    @abstractmethod
    def set_obligatory_parameters(self) -> None:
        """Устанавливает все обязательные значения фильтра"""
        pass

    @abstractmethod
    def set_extra_parameters(self) -> None:
        """Устанавливает дополнительные значения фильтра"""
        pass

    @abstractmethod
    def get_all_parameters(self) -> dict:
        """Возвращает все параметры фильтра в формате словаря"""
        pass


class FilterHH(Filter):
    """Класс для настройки фильтра запроса на сайт HeadHunter"""

    # ссылка на ресурс, возвращающий весь перечень регионов/городов
    _AREA_CODES = urls_hh.AREA_CODES
    # ссылка на ресурс, возвращающий словари со значениями для фильтра
    _FILTER_DICTIONARY = urls_hh.FILTER_DICTIONARY

    # словарь с возможными доменами для поиска
    _HOSTS = {"0": "hh.ru",
              "1": "rabota.by",
              "2": "hh1.az",
              "3": "hh.uz",
              "4": "hh.kz",
              "5": "headhunter.ge",
              "6": "headhunter.kg"
              }

    def __init__(self) -> None:
        """
        Инициализатор фильтра. Устанавливает все обязательные
        и дополнительные параметры фильтра
        """

        self._filter_dictionary = self.get_filter_dictionary()
        self._areas_info = self.get_areas_info()
        self._areas_names = self.get_areas_names()

        self.text: str = self.ask_text()  # ключевое слово, ищет по всей вакансии

        # обязательные параметры
        self.page: int = 0  # номер страницы
        self.per_page: int = 100  # количество элементов

        self.host: str = "hh.ru"  # доменное имя сайта
        self.only_with_salary: bool = False  # показывать вакансии только с указанием зарплаты, по умолчанию False
        self.locale: str = "RU"  # идентификатор локали

        # дополнительные параметры
        self.experience: str | None = None  # опыт работы
        self.employment: str | None = None  # тип занятости
        self.schedule: str | None = None  # график работы
        self.currency: str | None = None  # код валюты, имеет смысл указывать только вместе с salary
        self.order_by: str | None = None  # сортировка списка вакансий

        self.area: str | None = None  # регион
        self.salary: int | None = None  # размер заработной платы
        self.period: int | None = None  # количество дней, в пределах которых производится поиск по вакансиям

        super().__init__()

    def __str__(self):
        parameters = "\n".join([f"{key}: {value}" for key, value in self.get_parameters().items()])
        return f"Фильтр для поиска на HeadHunter. Значения:\n" \
               f"{parameters}"

    def __repr__(self):
        parameters = ", ".join([f"'{key}'={repr(value)}" for key, value in self.get_all_parameters().items()])
        return f"{self.__class__.__name__}({parameters})"

    def get_filter_dictionary(self) -> dict:
        """
        Возвращает словарь, содержащий надлежащие значения
        для некоторых параметров фильтра
        """

        url = self._FILTER_DICTIONARY
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении словаря дополнительных значений")

    def get_areas_info(self) -> list[dict]:
        """
        Возвращает список словарей, содержащих информацию о городах,
        доступных для поиска вакансий на сайте
        """

        url = self._AREA_CODES
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении списка кодов")

    def get_areas_names(self) -> list[str]:
        """
        Возвращает список городов и других субъектов,
        доступных для поиска вакансий на сайте
        """

        areas = self._areas_info

        json_exp = jp.parse('$..name')
        matches = json_exp.find(areas)
        names = [match.value for match in matches]

        return names

    def get_area_id(self, name: str) -> str:
        """
        Возвращает id переданного функции субъекта,
        если он есть в списке доступных
        """

        regions = self._areas_info

        json_exp = jp.parse("$..areas[*]")
        matches = [match.value for match in json_exp.find(regions) if match.value.get('name') == name]

        if matches:
            return matches[0].get("id")

    def set_obligatory_parameters(self) -> None:
        """Устанавливает обязательные параметры функции"""

        self.host = self.ask_host()
        self.only_with_salary = self.ask_only_with_salary()
        self.locale = self.ask_locale()

    def set_extra_parameters(self) -> None:
        """Устанавливает дополнительные параметры функции"""

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
    def ask_text() -> str:
        """Запрашивает у пользователя ключевые слова для поиска и возвращает их"""

        return i_input("\nВведите слово или фразу для ключевого запроса:\n")

    def ask_host(self) -> str:
        """
        Запрашивает у пользователя и возвращает выбранное
        доменное имя сайта для запроса
        """

        hosts = "\n".join([f"{num} - {host}" for num, host in self._HOSTS.items()])
        choice = i_input(f"\nКакое доменное имя сайта использовать для запроса? "
                       f"По умолчанию используется 'hh.ru'.\n"
                       f"Доступны варианты:\n{hosts}\n"
                       f"Введите номер выбранного домена или '0' чтобы оставить значение по умолчанию.\n")
        while choice not in self._HOSTS:
            choice = i_input("Неверный номер. Пожалуйста, повторите попытку:\n")
        return self._HOSTS[choice]

    def ask_only_with_salary(self) -> bool:
        """
        Запрашивает у пользователя возвращает значение, в зависимости от которого
        запрос будет включать или игнорировать вакансии без указания заработной платы
        """

        text = "Выводить только вакансии с указанием заработной платы? " \
               "Пожалуйста, введите ответ в формате числа.\n" \
               "0 - нет\n" \
               "1 - да"

        answer = self._check_binary_answer(text)

        return True if answer == "1" else False

    def ask_locale(self) -> str:
        """
        Запрашивает у пользователя возвращает значение локализации
        в зависимости от выбора пользователя
        """

        text = "Требуется ли изменить язык локализации на английский?\n" \
               "По умолчанию стоит русская локализация. " \
               "Пожалуйста, введите ответ в формате числа.\n" \
               "0 - нет\n" \
               "1 - да"

        answer = self._check_binary_answer(text)

        return "EN" if answer == "1" else "RU"

    @staticmethod
    def _check_right_answer(parameter: list, text: str) -> str:
        """
        Вспомогательная функция для валидации ответа пользователя,
        если значения параметра фильтра ограничены и указаны в словаре сайта
        """

        variations = "\n".join([f"{i} - {field['name']}" for i, field in enumerate(parameter)])
        choice = i_input(f"\n{text}\n{variations}\n"
                       f"Введите номер, либо нажмите Enter для пропуска.\n")

        while choice != "":
            if choice.isdigit() and 0 <= int(choice) < len(parameter):
                return choice

            choice = i_input(f"Введите существующий номер, либо нажмите Enter для пропуска.\n"
                             f"{variations}\n")

        return choice

    def ask_experience(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'требуемый опыт работы'
        """

        experience = self._filter_dictionary["experience"]
        text = "Выберите требуемый опыт работы:"
        answer = self._check_right_answer(experience, text)

        return experience[int(answer)]["id"] if answer.isdigit() else None

    def ask_employment(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'вид занятости'
        """

        employment = self._filter_dictionary["employment"]
        text = "Выберите требуемый вид занятости:"
        answer = self._check_right_answer(employment, text)

        return employment[int(answer)]["id"] if answer.isdigit() else None

    def ask_schedule(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'график работы'
        """

        schedule = self._filter_dictionary["schedule"]
        text = "Выберите требуемый график:"
        answer = self._check_right_answer(schedule, text)

        return schedule[int(answer)]["id"] if answer.isdigit() else None

    def ask_currency(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'валюта зарплаты'
        """

        currency = [field for field in self._filter_dictionary["currency"] if field["in_use"]]
        text = "Выберите валюту зарплаты:"
        answer = self._check_right_answer(currency, text)

        return currency[int(answer)]["code"] if answer.isdigit() else None

    def ask_order_by(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'способ сортировки'
        """

        order_by = [field for field in self._filter_dictionary["vacancy_search_order"] if field["id"] != "distance"]
        text = "Выберите способ сортировки:"
        answer = self._check_right_answer(order_by, text)

        return order_by[int(answer)]["id"] if answer.isdigit() else None

    def ask_area(self) -> str | None:
        """
        Запрашивает у пользователя, ищет и возвращает id
        по указанному названию города или другого субъекта,
        если таковой есть в перечне доступных для поиска
        """

        all_areas = sorted(self._areas_names)
        name = i_input("\nВведите город или населенный пункт, либо нажмите Enter для пропуска:\n")

        while name != "":

            if name == "list":
                print()
                print(*all_areas, sep="\n")
                print()
                name = i_input("Попробуйте ещё раз:\n")

            elif name not in all_areas:
                print(f"Не могу найти такой населенный пункт.\n"
                      f"Для вызова списка городов введите 'list'.\n"
                      f"Соблюдайте регистр.")
                name = i_input("Попробуйте ещё раз:\n")

            else:
                break

        return self.get_area_id(name)

    @staticmethod
    def _check_right_number(text: str) -> int | str:
        """
        Запрашивает и проверяет ответ пользователя,
        который должен быть либо целым положительным числом,
        либо пустой строкой
        """

        answer = i_input(f"\nВведите {text} (целое положительное число),\n"
                       f"либо нажмите Enter для пропуска:\n")

        while answer != "":
            if answer.isdigit():
                answer = int(answer)
                break
            answer = i_input("Введите целое положительное число без каких-либо знаков.\n"
                           "Попробуйте еще раз:\n")

        return answer

    def ask_salary(self) -> int | None:
        """
        Запрашивает и возвращает значение суммы зарплаты для поиска,
        если оно представлено целым положительным числом
        """

        text = "сумму зарплаты для поиска"
        salary = self._check_right_number(text)

        return salary if salary else None

    def ask_period(self) -> int | None:
        """
        Запрашивает и возвращает количество дней, в пределах которых
        производится поиск, если оно представлено целым положительным числом
        """

        text = "количество дней, в пределах которых производится поиск по вакансиям"
        period = self._check_right_number(text)

        return period if period else None

    def get_all_parameters(self) -> dict:
        """Возвращает все параметры фильтра"""

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
    """Класс для настройки фильтра запроса на сайт SuperJob"""

    # ссылка на ресурс, возвращающий весь перечень регионов/городов
    _AREA_CODES = urls_sj.AREA_CODES
    # ссылка на ресурс, возвращающий словари со значениями для фильтра
    _FILTER_DICTIONARY = urls_sj.FILTER_DICTIONARY

    def __init__(self) -> None:
        """
        Инициализатор фильтра. Устанавливает все обязательные
        и дополнительные параметры фильтра
        """

        self._filter_dictionary = self.get_filter_dictionary()
        self._areas_info = self.get_areas_info()
        self._areas_names = self.get_areas_names()

        self.keyword: str = self.ask_keyword()  # ключевое слово, ищет по всей вакансии

        # обязательные параметры
        self.page: int = 0
        self.count: int = 100

        self.no_agreement: int = 1  # не показывать оклад «по договоренности» (когда установлено значение 1)
        self.currency: str = "rub"  # валюта

        self.order_field: str = "date"  # сортировка: по дате публикации/по сумме оклада
        self.order_direction: str = "desc"  # направление сортировки: прямая/обратная

        # дополнительные параметры
        self.town: int | None = None  # ID города
        self.experience: int | None = None  # опыт работы
        self.type_of_work: int | None = None  # тип занятости
        self.payment_from: int | None = None  # сумма оклада от
        self.payment_to: int | None = None  # сумма оклада до
        self.period: int | None = None  # период публикации

        super().__init__()

    def __str__(self):
        parameters = "\n".join([f"{key}: {value}" for key, value in self.get_parameters().items()])
        return f"Фильтр для поиска на SuperJob. Значения:\n" \
               f"{parameters}"

    def __repr__(self):
        parameters = ", ".join([f"'{key}'={repr(value)}" for key, value in self.get_all_parameters().items()])
        return f"{self.__class__.__name__}({parameters})"

    def get_filter_dictionary(self) -> dict:
        """
        Возвращает словарь, содержащий надлежащие значения
        для некоторых параметров фильтра
        """

        url = self._FILTER_DICTIONARY
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении словаря дополнительных значений")

    def get_areas_info(self) -> list[dict]:
        """
        Возвращает список словарей, содержащих информацию о городах,
        доступных для поиска вакансий на сайте
        """

        url = self._AREA_CODES
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении списка кодов")

    def get_areas_names(self) -> list[str]:
        """
        Возвращает список городов и других субъектов,
        доступных для поиска вакансий на сайте
        """

        areas = self._areas_info

        json_exp = jp.parse('$..title')
        matches = json_exp.find(areas)
        codes = [match.value for match in matches]

        return codes

    def get_area_id(self, name: str) -> int:
        """
        Возвращает id переданного функции субъекта,
        если он есть в списке доступных
        """

        regions = self._areas_info

        json_exp = jp.parse("$..towns[*]")
        matches = [match.value for match in json_exp.find(regions) if match.value.get('title') == name]

        if matches:
            return matches[0].get("id")

    def set_obligatory_parameters(self) -> None:
        """Устанавливает обязательные параметры функции"""

        self.no_agreement = self.ask_no_agreement()
        self.order_field = self.ask_order_field()
        self.order_direction = self.ask_order_direction()

    def set_extra_parameters(self) -> None:
        """Устанавливает дополнительные параметры функции"""

        self.town = self.ask_town()
        self.experience = self.ask_experience()
        self.type_of_work = self.ask_type_of_work()
        self.payment_from, self.payment_to = self.ask_payment_from_to()
        self.period = self.ask_period()

    @staticmethod
    def ask_keyword() -> str:
        """Запрашивает у пользователя ключевые слова для поиска и возвращает их"""

        return i_input("\nВведите слово или фразу для ключевого запроса:\n")

    def ask_no_agreement(self) -> int:
        """
        Запрашивает у пользователя и возвращает значение 0 или 1 для включения
        или игнорирования вакансий с окладом 'по договоренности'
        """

        text = "Требуется ли исключить вакансии с окладом 'по договоренности'?\n" \
               "Пожалуйста, введите соответствующее числовое значение.\n" \
               "0 - нет\n" \
               "1 - да"

        answer = self._check_binary_answer(text)

        return 1 if answer == "да" else 0

    def ask_order_field(self) -> str:
        """
        Запрашивает у пользователя и возвращает значение сортировки
        вакансий: по дате или сумме оклада
        """

        text = "Сортировать вакансии по параметру:\n" \
               "Пожалуйста, введите соответствующее числовое значение.\n" \
               "0 - дата\n" \
               "1 - сумма оклада" \

        answer = self._check_binary_answer(text)

        return "date" if answer == "0" else "payment"

    def ask_order_direction(self) -> str:
        """
        Запрашивает у пользователя и возвращает значение направление
        сортировки вакансий: в прямом или обратном порядке
        """

        text = "В каком направлении следует сортировать вакансии?\n" \
               "Пожалуйста, введите соответствующее числовое значение:\n" \
               "0 - в прямом\n" \
               "1 - в обратном"

        answer = self._check_binary_answer(text)

        return "asc" if answer == "0" else "desc"

    @staticmethod
    def _check_right_answer(parameter: dict, text: str) -> str:
        """
        Вспомогательная функция для валидации ответа пользователя,
        если значения параметра фильтра ограничены и указаны в словаре сайта
        """

        variations = "\n".join([f"{key} - {value}" for key, value in parameter.items()])

        choice = i_input(f"\nВведите подходящее числовое значение для выбора {text}, "
                       f"либо нажмите Enter для пропуска:\n{variations}\n")

        while choice not in parameter:
            if choice == "":
                break
            choice = i_input(f"Введите существующий номер, либо нажмите Enter для пропуска.\n"
                           f"{variations}\n")

        return choice

    def ask_experience(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'требуемый опыт работы'
        """

        experience = self._filter_dictionary["experience"]
        text = "опыта работы"

        answer = self._check_right_answer(experience, text)

        return answer if answer else None

    def ask_type_of_work(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'тип занятости'
        """

        type_of_work = self._filter_dictionary["type_of_work"]
        text = "типа занятости"

        answer = self._check_right_answer(type_of_work, text)

        return answer if answer else None

    def ask_period(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'период публикации' вакансии
        """

        period = self._filter_dictionary["period"]
        text = "периода публикации"

        answer = self._check_right_answer(period, text)

        return answer if answer else None

    def ask_town(self) -> int | None:
        """
        Запрашивает у пользователя, ищет и возвращает id
        по указанному названию города или другого субъекта,
        если таковой есть в перечне доступных для поиска
        """

        all_towns = sorted(self._areas_names)
        name = i_input("\nВведите город или населенный пункт, либо нажмите Enter для пропуска:\n")

        while name != "":

            if name == "list":
                print()
                print(*all_towns, sep="\n")
                print()
                name = i_input("Попробуйте ещё раз:\n")

            elif name not in all_towns:
                print(f"Не могу найти такой населенный пункт.\n"
                      f"Для вызова списка городов введите 'list'.\n"
                      f"Соблюдайте регистр.")
                name = i_input("Попробуйте ещё раз:\n")

            else:
                break

        return self.get_area_id(name)

    @staticmethod
    def _get_number(text: str) -> int | None:
        """
        Запрашивает у пользователя и валидирует значение суммы
        на соответствие условиям: сумма должна быть целым положительным числом,
        либо этот параметр будет пропущен (если выражен пустой строкой)
        """

        payment = i_input(f"\nВведите {text} суммы зарплаты для поиска (целое положительное число),\n"
                        f"либо нажмите Enter для пропуска:\n")

        while payment != "":
            if payment.isdigit():
                payment = int(payment)
                break
            payment = i_input("Сумма должна быть целым положительным числом без каких-либо знаков.\n"
                            "Попробуйте еще раз:\n")

        return payment if payment else None

    def ask_payment_from_to(self) -> tuple | list:
        """
        Запрашивает у пользователя и возвращает нижнюю
        и вернюю границы зарплаты для поиска
        """

        text = "нижнюю границу"
        payment_from = self._get_number(text)

        text = "верхнюю границу"
        payment_to = self._get_number(text)

        try:
            return sorted((payment_from, payment_to))
        except TypeError:
            return payment_from, payment_to

    def get_all_parameters(self) -> dict:
        """Возвращает все параметры фильтра"""

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
