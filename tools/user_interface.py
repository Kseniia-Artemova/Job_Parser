import os
from pprint import pprint

from filter.filter_hh import FilterHH
from filter.filter_sj import FilterSJ
from request_api.request_api import HeadHunterAPI, SuperJobAPI
from saver.saver import JSONSaver
from tools.utils import i_input, get_binary_answer


def user_interaction():
    print("Добрый день! Я помогу вам найти вакансии.")

    vacancies = find_vacancies()

    json_saver = JSONSaver()
    json_saver.write_vacancies(vacancies)

    vacancy_objects = json_saver.load_all_vacancies()

    show_vacancies(vacancy_objects)


def find_vacancies():

    results = []

    while True:

        request_filter = None
        request_api = None

        website = choice_website()

        if website == "0":
            request_filter = FilterHH()
            request_filter.parameters["text"] = request_filter.ask_text()
            request_api = HeadHunterAPI

        elif website == "1":
            request_filter = FilterSJ()
            request_filter.parameters["keyword"] = request_filter.ask_keyword()
            request_api = SuperJobAPI

        request = request_api(*set_filter(request_filter))

        vacancies = request.get_vacancies()

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

    while check_int(answer) not in range(len(websites)):
        answer = i_input("\nПожалуйста, введите номер, соответствующий ресурсу.\n")

    return answer


def check_int(number):

    while True:
        try:
            return int(number)
        except ValueError:
            number = i_input("\nОтвет должен быть выражен целым числом.\n")
            continue


def set_filter(request_filter):

    text = "Настроить фильтр или использовать параметры по умолчанию?\n" \
           "0 - использовать параметры по умолчанию\n" \
           "1 - настроить фильтр самостоятельно"

    answer = get_binary_answer(text)

    if answer == "1":
        request_filter.set_request_parameters()

    number = get_number()

    return request_filter, number


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


def show_vacancies(list_objects):

    for object in list_objects:
        print()
        print(object.get_short_info())
