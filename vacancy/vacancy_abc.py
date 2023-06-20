from abc import ABC, abstractmethod


class Vacancy(ABC):

    def get_parameters(self) -> dict:
        return self.__dict__

    def _check_currency(self, other):
        rub = ("rub", "RUR")

        if isinstance(other, Vacancy):
            if self.get_currency() == other.get_currency():
                return True
            elif self.get_currency() in rub and other.get_currency() in rub:
                return True

            return False

    def __eq__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() == other.get_min_salary()

    def __ne__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() != other.get_min_salary()

    def __lt__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() < other.get_min_salary()

    def __le__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() <= other.get_min_salary()

    def __gt__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() > other.get_min_salary()

    def __ge__(self, other):

        if isinstance(other, Vacancy) and self._check_currency(other):
            return self.get_min_salary() >= other.get_min_salary()

    @abstractmethod
    def get_min_salary(self) -> int:
        pass

    @abstractmethod
    def get_currency(self) -> str:
        pass

    @abstractmethod
    def get_short_info(self) -> str:
        pass

    @abstractmethod
    def get_full_info(self) -> dict:
        pass





