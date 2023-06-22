from abc import ABC, abstractmethod


class Vacancy(ABC):

    def get_parameters(self) -> dict:
        return self.__dict__

    def __eq__(self, other):

        if isinstance(other, Vacancy):
            return self.get_min_salary() == other.get_min_salary()

    def __ne__(self, other):

        if isinstance(other, Vacancy):
            return self.get_min_salary() != other.get_min_salary()

    def __lt__(self, other):

        if isinstance(other, Vacancy):
            return self.get_min_salary() < other.get_min_salary()

    def __le__(self, other):

        if isinstance(other, Vacancy):
            return self.get_min_salary() <= other.get_min_salary()

    def __gt__(self, other):

        if isinstance(other, Vacancy):
            return self.get_min_salary() > other.get_min_salary()

    def __ge__(self, other):

        if isinstance(other, Vacancy):
            return self.get_min_salary() >= other.get_min_salary()

    @abstractmethod
    def get_min_salary(self) -> int:
        pass

    @abstractmethod
    def get_short_info(self) -> str:
        pass
