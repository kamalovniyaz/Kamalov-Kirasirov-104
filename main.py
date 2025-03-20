import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Список посещенных URL, чтобы избежать дублирования
visited_urls = set()


def fetch_page(url: str) -> str | None:
    """Получение текста страницы."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to retrieve {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def save_to_file(content: str, filename: str) -> None:
    """Сохранение контента в файл."""
    try:
        fixed_content = content.encode('latin1').decode('utf-8', errors='replace')
    except UnicodeEncodeError:
        fixed_content = content
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(fixed_content)


def create_index_file(index_data: list[tuple], filename: str = 'index.txt') -> None:
    """Сохранение данных о всех номерах файла и ссылках в файл."""
    with open(filename, 'w', encoding='utf-8') as file:
        for idx, url in index_data:
            file.write(f"{idx} {url}\n")


def crawl(base_url: str, max_pages: int = 120) -> None:
    """Краулер для сбора страниц и рекурсивного обхода всех найденных ссылок."""
    urls_to_visit = [base_url]  # Очередь ссылок для обхода
    index_data = []

    os.makedirs('dumps', exist_ok=True)  # Создаем папку dumps, если её нет

    while urls_to_visit and len(visited_urls) < max_pages:
        url = urls_to_visit.pop(0)  # Берем первую ссылку из очереди
        if url in visited_urls:
            continue

        content = fetch_page(url)
        if not content:
            continue

        page_number = len(visited_urls) + 1
        print(f"Crawling: {url} (Page {page_number})")

        filename = f'dump_{page_number}.txt'
        filepath = os.path.join('dumps', filename)
        save_to_file(content, filepath)
        index_data.append((filename, url))
        visited_urls.add(url)

        soup = BeautifulSoup(content, 'html.parser')
        # Ищем все ссылки на текущей странице
        sidebar = soup.find('div', class_='sidebar-scrollbox')
        for link in sidebar.find_all('a', href=True):
            relative_path = link['href']
            full_url = urljoin(base_url, f'/book/{relative_path}')  # Преобразуем в абсолютный URL

            # Проверяем, что ссылка ведет на тот же домен и еще не была посещена
            if full_url.startswith(base_url) and full_url not in visited_urls and full_url not in urls_to_visit:
                urls_to_visit.append(full_url)  # Добавляем следующую ссылку для обхода в список

    create_index_file(index_data)


if __name__ == "__main__":
    base_url = 'https://doc.rust-lang.ru/book'  # основная страница
    crawl(base_url, max_pages=120)
