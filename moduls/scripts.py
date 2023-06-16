import os
from pprint import pprint

from classes.filter import FilterHH, FilterSJ
from classes.request_api import HeadHunterAPI, SuperJobAPI
from classes.saver import JSONSaver
from moduls.utils import i_input


def user_interaction():
    print("Добрый день! Я помогу вам найти вакансии.")

    vacancies = find_vacancies()

    json_saver = JSONSaver()
    json_saver.add_vacancies(vacancies)


def check_int(number):

    while True:
        try:
            return int(number)
        except ValueError:
            number = i_input("\nОтвет должен быть выражен целым числом.\n")
            continue


def find_vacancies():

    results = []

    while True:

        website = choice_website()
        number = get_number()

        if website == "0":
            vacancies = HeadHunterAPI(FilterHH()).get_vacancies(number)

        elif website == "1":
            vacancies = SuperJobAPI(FilterSJ()).get_vacancies(number)

        for vacancy in vacancies:
            if vacancy not in results:
                results.append(vacancy)

        operation = choice_operation()

        if operation == 0:
            continue
        elif operation == 1:
            results.clear()
            continue
        elif operation == 2:
            break

    return results


def choice_website():

    root_dir = os.path.dirname(os.path.dirname(__file__))
    path_websites = os.path.join(root_dir, "sources", "urls.txt")
    with open(path_websites, "r", encoding="utf-8") as file:
        websites = file.read().split("\n")

    websites_print = "\n".join([f"{i}: {site}" for i, site in enumerate(websites)])
    answer = i_input(f"\nНа каком сайте искать вакансии? "
                     f"Пожалуйста, введите номер, соответствующий ресурсу.\n"
                     f"{websites_print}\n")

    return answer


def get_number():

    answer = i_input("\nПожалуйста, введите желаемое количество вакансий. "
                     "Число должно быть больше 0 и не больше 500.\n"
                     "В противном случае будет установлено значение по умолчанию = 10)\n")

    return check_int(answer)


def choice_operation():
    operations = {
        0: "Добавить больше вакансий в список",
        1: "Очистить список и найти новые вакансии",
        2: "Показать результаты поиска"
    }

    operations_print = "\n".join([f"{key}: {value}" for key, value in operations.items()])

    operation = None

    while operation not in operations:

        operation = i_input(f"\nПожалуйста, выберите номер следующей операции.\n"
                            f"{operations_print}\n")

        operation = check_int(operation)

    return operation


