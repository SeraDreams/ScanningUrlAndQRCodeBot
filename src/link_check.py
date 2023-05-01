import requests
import socket
import ssl
from urllib.parse import urlparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import whois
import datetime


def string_similarity(str1, str2):
    """Функция для вычисления расстояния Левенштейна между двумя строками"""
    distances = [[0 for j in range(len(str2) + 1)] for i in range(len(str1) + 1)]

    for i in range(len(str1) + 1):
        distances[i][0] = i
    for j in range(len(str2) + 1):
        distances[0][j] = j

    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            if str1[i - 1] == str2[j - 1]:
                distances[i][j] = distances[i - 1][j - 1]
            else:
                distances[i][j] = min(distances[i - 1][j], distances[i][j - 1], distances[i - 1][j - 1]) + 1

    return distances[-1][-1]


def is_redirect(link):
    """Функция для проверки на наличие редиректа"""
    response = requests.head(link, allow_redirects=False)
    return response.status_code in (301, 302)


def has_suspicious_js(link):
    """Функция для проверки на наличие подозрительного JS кода"""
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.get(link, verify=False)
    js_code = response.text
    if response.status_code == 200:
        if "eval(" in js_code or 'document.location.replace(' in js_code:
            return True
    return False


def is_solution(link):
    """Функция для проверки на наличие скачиваемых файлов"""
    response = requests.get(link, verify=False)
    content_type = response.headers['content-type']
    return 'application/octet-stream' in content_type or '.exe' in link or '.dll' in link


def is_https(link):
    """Функция для проверки наличия HTTPS в ссылке"""
    return link.startswith('https://')


def has_ssl_cert(link):
    """Функция для проверки наличия SSL-сертификата"""
    response = requests.head(link)
    url = response.url
    if isinstance(url, bytes):
        url = url.decode('utf-8')
    domain = urlparse(url).netloc.split(':')[0]
    context = ssl.create_default_context()
    with socket.create_connection((domain, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssl_sock:
            cert = ssl_sock.getpeercert()
            return bool(cert)


def is_suspicious(link):
    """Функция для проверки ссылки на подозрительные домены"""
    domens = ['google', 'facebook', 'amazon', 'twitter', 'linkedin', 'youtube']
    parsed_link = urlparse(link)
    domain = parsed_link.netloc.split('.')[1]
    for i in domens:
        if 0 < string_similarity(domain, i) < 3:
            return True
    return False


def is_long_level(link):
    """Функция для проверки на длину уровня ссылки"""
    return len(link.split('.')) > 4


def is_unreadable(link):
    """Функция для проверки на неразборчивость ссылки"""
    return any(char in link for char in ['xn--', 'xn----', 'xn------'])


def register_domain(link):
    """Функция для проверки кол-ва дней с даты регистрации домена"""
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
            return "Неизвестно"
        else:
            # получаем текущую дату
            current_date = datetime.datetime.now()
            # вычисляем количество дней между текущей датой и датой регистрации
            delta = current_date - registration_date
            # выводим количество дней
            return delta.days


def check_link(link):
    """Функция для проверки ссылки на различные признаки подозрительности"""
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.get(link, verify=False)
    stats = {
        'redirect': is_redirect(link),
        'https': is_https(link),
        'ssl': has_ssl_cert(link),
        'suspicious': is_suspicious(link),
        'suspicious_js': has_suspicious_js(link),
        'Long level': is_long_level(link),
        'Unreadability': is_unreadable(link),
        'register_domain': register_domain(link)
    }
    return stats