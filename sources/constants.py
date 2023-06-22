# ссылка на словарь центрального банка России, для конвертации валюты в рубли
CBR_RATE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

# кортеж строк для построения пути от корневой папки проекта к дефолтному файлу
# для сохранения полной информации о найденных вакансиях
PATH_FILE_FULL_INFO_VACANCIES = ("vacancies_files", "JSON", "vacancies(full_info).json")

# кортеж строк для построения пути от корневой папки проекта к дефолтному файлу
# для сохранения краткой информации о найденных вакансиях
PATH_FILE_SHORT_INFO_VACANCIES = ("vacancies_files", "JSON", "vacancies(short_info).json")

# кортеж строк для построения пути от корневой папки проекта к папке с JSON-файлами,
# содержащими информацию о найденных вакансиях
PATH_DIR_JSON = "vacancies_files", "JSON"

# максимальное количество символов для имени пользовательского файла с вакансиями
MAX_LENGTH_NAME = 20