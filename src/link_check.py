import requests
from urllib.parse import urlparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import whois
import datetime


def string_similarity(str1, str2):
    """Функция для вычисления расстояния Левенштейна между двумя строками"""
    # Инициализируем матрицу расстояний Левенштейна
    distances = [[0 for j in range(len(str2) + 1)] for i in range(len(str1) + 1)]

    # Заполняем первый столбец и первую строку матрицы
    for i in range(len(str1) + 1):
        distances[i][0] = i
    for j in range(len(str2) + 1):
        distances[0][j] = j

    # Вычисляем расстояние Левенштейна для каждой пары символов в строках
    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            if str1[i - 1] == str2[j - 1]:
                distances[i][j] = distances[i - 1][j - 1]
            else:
                distances[i][j] = min(distances[i - 1][j], distances[i][j - 1], distances[i - 1][j - 1]) + 1

    # Возвращаем расстояние Левенштейна между двумя строками
    return distances[-1][-1]


"""Функция для проверки на наличие редиректа"""
def redirect(link):
    # Отправляем HEAD-запрос на указанный URL, запрещая перенаправления
    response = requests.head(link, allow_redirects=False)
    # Возвращаем True, если код статуса равен 301 или 302
    return response.status_code in (301, 302)


"""Функция для проверки на наличие подозрительного JS кода"""
def suspicious_js(link):
    # Отключаем предупреждения о небезопасных запросах
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    # Отправляем GET-запрос на указанный URL, отключая проверку SSL-сертификата
    response = requests.get(link, verify=False)
    js_code = response.text
    # Если код статуса равен 200, проверяем наличие строк 'eval(' или 'document.location.replace(' в коде JavaScript
    if response.status_code == 200:
        if "eval(" in js_code or 'document.location.replace(' in js_code:
            return True
    return False


"""Функция для проверки на наличие скачиваемых файлов"""
def solution(link):
    # Отправляем GET-запрос на указанный URL, отключая проверку SSL-сертификата
    response = requests.get(link, verify=False)
    content_type = response.headers['content-type']
    # Возвращаем True, если тип содержимого соответствует application/octet-stream или URL содержит расширение .exe или .dll
    return 'application/octet-stream' in content_type or '.exe' in link or '.dll' in link


"""Функция для проверки наличия HTTPS в ссылке"""
def https(link):
    # Возвращаем True, если ссылка начинается с https://
    return link.startswith('https://')


"""Функция для проверки наличия SSL-сертификата"""
def ssl_cert(link):
    # Отправляем HEAD-запрос на указанный URL
    response = requests.head(link)
    # Получаем URL после всех редиректов
    final_url = response.url
    # Извлекаем доменное имя из URL
    domain = urlparse(final_url).netloc
    # Используем библиотеку whois для получения информации о домене
    w = whois.whois(domain)
    # Получаем дату истечения срока действия SSL-сертификата
    if isinstance(w.expiration_date, list):
        expiration_date = w.expiration_date[0]
    else:
        expiration_date = w.expiration_date
    # Возвращаем True, если дата истечения сертификата больше текущей даты
    if expiration_date is not None:
        return expiration_date > datetime.datetime.now()
    else:
        return False


"""Функция для проверки наличия подозрительных слов в ссылке"""
def suspicious(link):
    suspicious_words = ['login', 'signin', 'banking', 'account', 'password', 'secure', 'confirm', 'update', 'verify']
    # Извлекаем доменное имя из URL
    domain = urlparse(link).netloc
    # Проверяем, содержит ли доменное имя подозрительные слова
    for word in suspicious_words:
        if word in domain.lower():
            return True
    return False


"""Функция для проверки длины уровня домена"""
def long_level(link):
    # Извлекаем доменное имя из URL
    domain = urlparse(link).netloc
    # Получаем список уровней домена
    domain_levels = domain.split('.')
    # Возвращаем True, если длина последнего уровня домена больше 15 символов
    if len(domain_levels[-1]) > 15:
        return True
    return False


"""Функция для проверки наличия нечитаемых символов в ссылке"""
def unreadable(link):
    # Извлекаем доменное имя из URL
    domain = urlparse(link).netloc
    # Проверяем, содержит ли доменное имя нечитаемые символы
    for char in domain:
        if not char.isalnum() and char not in ['-', '.']:
            return True
    return False


"""Функция для проверки даты регистрации домена"""
def register_domain(link):
    domain = link
    w = whois.whois(domain)
    # получаем дату регистрации
    registration_date = w.creation_date
    # если дата регистрации не является списком, преобразуем ее в список
    if not isinstance(registration_date, list):
        registration_date = [registration_date]
        # выбираем первую дату из списка
        registration_date = registration_date[0]
        # если дата регистрации неизвестна, выводим сообщение об ошибке
        if registration_date is None:
            return False
        else:
            # получаем текущую дату
            current_date = datetime.datetime.now()
            # вычисляем количество дней между текущей датой и датой регистрации
            delta = current_date - registration_date
            # выводим количество дней
            return delta.days
    else:
        # выбираем первую дату из списка
        registration_date = registration_date[0]
        if registration_date is None:
            return False
        else:
            # получаем текущую дату
            current_date = datetime.datetime.now()
            # вычисляем количество дней между текущей датой и датой регистрации
            delta = current_date - registration_date
            # выводим количество дней
            return delta.days


"""Функция для проверки ссылки на различные признаки подозрительности"""
def check_link(link):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.get(link, verify=False)
    stats = {
        'redirect': redirect(link),
        'https': https(link),
        'ssl': ssl_cert(link),
        'suspicious': suspicious(link),
        'suspicious_js': suspicious_js(link),
        'Long level': long_level(link),
        'Unreadability': unreadable(link),
        'register_domain': register_domain(link)
    }
    return stats
