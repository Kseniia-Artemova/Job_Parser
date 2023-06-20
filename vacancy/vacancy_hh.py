from vacancy.vacancy_abc import Vacancy


class VacancyHeadHunter(Vacancy):

    def __init__(self, vacancy_dict: dict) -> None:
        self.name = vacancy_dict.get("name")
        self.area = vacancy_dict.get("area")
        self.salary = vacancy_dict.get("salary")
        self.alternate_url = vacancy_dict.get("alternate_url")
        self.requirement = vacancy_dict.get("snippet")
        self.responsibility = vacancy_dict.get("snippet")
        self.professional_roles = vacancy_dict.get("professional_roles")
        self.experience = vacancy_dict.get("experience")
        self.employment = vacancy_dict.get("employment")

        self.full_info = vacancy_dict

    def __str__(self) -> str:
        return f"'name': {self.name}\n" \
               f"'url': {self.alternate_url}"

    def __repr__(self) -> str:
        full_info = "\n".join({f"{key}: {value}" for key, value in self.full_info.items()})
        return f"{self.__class__.__name__}(\n" \
               f"{full_info}\n" \
               f")"

    def __setattr__(self, key, value) -> None:
        if key == "requirement" or key == "responsibility":
            value = value.get(key) if value else None
            artefacts = ("<highlighttext>", "</highlighttext>")
            for string in artefacts:
                if value and string in value:
                    value = value.replace(string, "")
        super().__setattr__(key, value)

    def get_min_salary(self) -> int:

        if self.salary:
            salary_from, salary_to = self.salary.get("from"), self.salary.get("to")

            min_salary = 0

            if any((salary_from, salary_to)):
                min_salary = min([salary for salary in (salary_from, salary_to) if type(salary) is int])

            return min_salary

    def get_currency(self) -> str:

        if self.salary:
            return self.salary.get("currency")

    def get_short_info(self) -> str:

        name = self.name
        area = self.area.get('name', "Не указано") if self.area else "Не указано"
        salary_from = self.salary.get('from') if self.salary else None
        salary_to = self.salary.get('to') if self.salary else None
        currency = self.salary.get('currency') if self.salary else ""
        alternate_url = self.alternate_url
        requirement = self.requirement if self.requirement else "Не указано"
        responsibility = self.responsibility if self.responsibility else "Не указано"

        experience = self.experience.get('name', "Не указано") if self.experience else "Не указано"
        employment = self.employment.get('name', "Не указано") if self.employment else "Не указано"

        str_salary = "Не указано"
        if all((salary_from, salary_to)):
            str_salary = f"{salary_from} - {salary_to} {currency}"
        elif any((salary_from, salary_to)):
            str_salary = f"{salary_from or salary_to} {currency}"

        str_professional_roles = "Не указано"
        if self.professional_roles:
            professional_roles = [role.get("name", "Не указано") for role in self.professional_roles]
            str_professional_roles = ", ".join(professional_roles)

        return f"Название: {name}\n" \
               f"Город: {area}\n" \
               f"Зарплата: {str_salary}\n" \
               f"Ссылка: {alternate_url}\n" \
               f"Требования: {requirement}\n" \
               f"Обязанности: {responsibility}\n" \
               f"Профессиональные роли: {str_professional_roles}\n" \
               f"Опыт: {experience}\n" \
               f"Занятость: {employment}"

    def get_full_info(self) -> dict:
        return self.full_info