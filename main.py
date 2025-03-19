import os
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

visited_urls = set()  # Все посещенные страницы для убирания дублей


def fetch_page(url: str) -> str | None:
    """Получение текста страницы."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        return None


def save_to_file(content: str, filename: str) -> None:
    """Сохранение контента в файл."""
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)


def create_index_file(index_data: list[tuple], filename: str = 'index.txt') -> None:
    """Сохранение данных о всех номерах файла и ссылках в файл."""
    with open(filename, 'w', encoding='utf-8') as file:
        for idx, url in index_data:
            file.write(f"{idx} {url}\n")


def crawl(start_url: str, max_pages: int = 120) -> None:
    """Краулер для сбора страниц и рекурсивного обхода всех найденных ссылок."""
    urls_to_visit = [start_url]  # Очередь ссылок для обхода
    index_data = []

    # Регулярное выражение для фильтрации ссылок
    product_pattern = re.compile(r'https:\/\/chaconne\.ru\/product\/\d+\/')

    while urls_to_visit and len(visited_urls) < max_pages:
        url = urls_to_visit.pop(0)  # Берем первую ссылку из очереди
        if url in visited_urls:
            continue

        content = fetch_page(url)
        if not content:
            continue

        page_number = len(visited_urls) + 1
        print(page_number)
        filename = f'dump_{page_number}.txt'
        filepath = os.path.join('dumps', filename)
        save_to_file(content, filepath)
        index_data.append((filename, url))
        visited_urls.add(url)

        soup = BeautifulSoup(content, 'html.parser')
        # Ищем все ссылки на текущей странице
        for link in soup.find_all('a', href=True):
            new_url = link['href']
            full_url = urljoin(start_url, new_url)  #
            # Проверяем, что ссылка ведет на тот же домен и еще не была посещена
            if full_url.startswith(start_url) and full_url not in visited_urls and full_url not in urls_to_visit:
                # Фильтруем ссылки по шаблону /product/{id}/
                if product_pattern.match(full_url):
                    urls_to_visit.append(full_url) # Добавляем следующую ссылку для обхода в список

    create_index_file(index_data)


if __name__ == "__main__":
    start_url = 'https://chaconne.ru'  # основная страница
    crawl(start_url, max_pages=120)
