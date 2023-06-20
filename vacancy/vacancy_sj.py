from vacancy.vacancy_abc import Vacancy


class VacancySuperJob(Vacancy):

    def __init__(self, vacancy_dict: dict) -> None:

        self.profession = vacancy_dict.get("profession")
        self.town = vacancy_dict.get("town")
        self.payment_from = vacancy_dict.get("payment_from")
        self.payment_to = vacancy_dict.get("payment_to")
        self.currency = vacancy_dict.get("currency")
        self.link = vacancy_dict.get("link")
        self.description = vacancy_dict.get("candidat")
        self.experience = vacancy_dict.get("experience")
        self.type_of_work = vacancy_dict.get("type_of_work")

        self.full_info = vacancy_dict

    def __str__(self) -> str:
        return f"'profession': {self.profession}\n" \
               f"'url': {self.link}"

    def __repr__(self) -> str:
        full_info = "\n".join({f"{key}: {value}" for key, value in self.full_info.items()})
        return f"{self.__class__.__name__}(\n" \
               f"{full_info}\n" \
               f")"

    def __setattr__(self, key, value):
        if key == "description":
            value = value.replace("\n\n", "\n").replace("\n", "\n\t")
        super().__setattr__(key, value)

    def get_min_salary(self) -> int:

        salary_from, salary_to = self.payment_from, self.payment_to

        min_salary = 0

        if all((salary_from, salary_to)):
            min_salary = min([salary for salary in (salary_from, salary_to) if type(salary) is int])
        elif any((salary_from, salary_to)):
            min_salary = salary_from or salary_to

        return min_salary

    def get_currency(self) -> str:
        return self.currency

    def get_short_info(self) -> str:

        profession = self.profession
        town = self.town.get("title", "Не указано") if self.town else "Не указано"
        payment_from = self.payment_from
        payment_to = self.payment_to
        currency = self.currency if self.currency else ""
        link = self.link
        description = self.description if self.description else "Не указано"

        experience = self.experience.get("title", "Не указано") if self.experience else "Не указано"
        type_of_work = self.type_of_work.get("title", "Не указано") if self.type_of_work else "Не указано"

        str_salary = "Не указано"
        if all((payment_from, payment_to)):
            str_salary = f"{payment_from} - {payment_to} {currency}"
        elif any((payment_from, payment_to)):
            str_salary = f"{payment_from or payment_to} {currency}"

        return f"Название: {profession}\n" \
               f"Город: {town}\n" \
               f"Зарплата: {str_salary}\n" \
               f"Ссылка: {link}\n" \
               f"Описание: \n\t{description}\n" \
               f"Опыт: {experience}\n" \
               f"Занятость: {type_of_work}"

    def get_full_info(self) -> dict:
        return self.full_info
