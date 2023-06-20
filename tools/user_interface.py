import os

from filter.filter_hh import FilterHH
from filter.filter_sj import FilterSJ
from request_api.request_api_hh import HeadHunterAPI
from request_api.request_api_sj import SuperJobAPI
from saver.saver import JSONSaver
from tools.utils import i_input, get_binary_answer


def user_interaction():
    print("Добрый день! Я помогу вам найти вакансии.")

    vacancies = find_vacancies()

    json_saver = JSONSaver()
    json_saver.write_vacancies(vacancies)

    list_vacancies = create_list_vacancies(json_saver)

    show_vacancies(list_vacancies)


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

        operations = {
            0: "Добавить больше вакансий в список",
            1: "Очистить список и найти новые вакансии",
            2: "Показать результаты поиска"
        }

        operation = choice_operation(operations)

        if operation == 0:
            continue
        elif operation == 1:
            results.clear()
            continue
        elif operation == 2:
            break

    return results


def choice_website():

    websites = get_websites()

    websites_print = "\n".join([f"{i}: {site}" for i, site in enumerate(websites)])
    answer = i_input(f"\nНа каком сайте искать вакансии? "
                     f"Пожалуйста, введите номер, соответствующий ресурсу.\n"
                     f"{websites_print}\n")

    while check_int(answer) not in range(len(websites)):
        answer = i_input("\nПожалуйста, введите номер, соответствующий ресурсу.\n")

    return answer


def get_websites():

    root_dir = os.path.dirname(os.path.dirname(__file__))
    path_websites = os.path.join(root_dir, "sources", "urls.txt")
    with open(path_websites, "r", encoding="utf-8") as file:
        websites = file.read().split("\n")

    return websites


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


def choice_operation(operations):

    operations_print = "\n".join([f"{key}: {value}" for key, value in operations.items()])

    operation = None

    while operation not in operations:
        operation = i_input(f"\nПожалуйста, выберите номер следующей операции.\n"
                            f"{operations_print}\n")
        operation = check_int(operation)

    return operation


def create_list_vacancies(saver):

    text = "В каком виде вывести информацию?\n" \
           "0 - Вывести все вакансии\n" \
           "1 - Настроить фильтр для вывода вакансий"

    answer = get_binary_answer(text)

    if answer == "0":
        return saver.load_all_vacancies()

    elif answer == "1":

        websites = get_websites()

        operations = {
            0: f"Настроить фильтр и вывести вакансии с сайта {websites[0]}",
            1: f"Настроить фильтр и вывести вакансии с сайта {websites[1]}",
            2: "Настроить оба фильтра и вывести вакансии с обоих сайтов"
        }

        operation = choice_operation(operations)

        if operation == 0:
            filter_obj = FilterHH()
            return saver.load_definite_vacancies(filter_obj_hh=filter_obj)
        elif operation == 1:
            filter_obj = FilterSJ()
            return saver.load_definite_vacancies(filter_obj_sj=filter_obj)
        elif operation == 2:
            filter_obj_hh, filter_obj_sj = (FilterHH(), FilterSJ())
            return saver.load_definite_vacancies(filter_obj_hh=filter_obj_hh, filter_obj_sj=filter_obj_sj)


def show_vacancies(list_objects):

    max_quantity = len(list_objects)

    text = "Отсортировать вакансии по зарплате?\n" \
           "0 - Нет\n" \
           "1 - Да"

    sorting = int(get_binary_answer(text))

    text = "В каком порядке выполнить сортировку?\n" \
           "0 - В порядке возрастания\n" \
           "1 - В порядке убывания"

    reverse = True if int(get_binary_answer(text)) else False

    if sorting:
        list_objects = sorted(list_objects, reverse=reverse)

    quantity = i_input(f"\nСколько вакансий вывести? "
                       f"Возможный максимум - {max_quantity}\n"
                       f"Чтобы вывести все, нажмите Enter\n")

    while quantity != "":
        if quantity.isdigit() and int(quantity) < max_quantity:
            break
        quantity = i_input("Значение должно быть целым положительным числом меньше максимума.")

    if quantity:
        list_objects = list_objects[:int(quantity)]

    for object in list_objects:
        print()
        print(object.get_short_info())
