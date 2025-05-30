import os
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ..constants import OUTPUT_DIR, URLS_FILENAME


def load_tfidf_data(output_dir) -> tuple[dict, set]:
    """Загружает данные TF-IDF из папки output."""
    tfidf_data = {}
    vocabulary = set()

    for filename in os.listdir(Path(__file__).parent /output_dir):
        if filename.endswith(".txt"):
            page_num = int(filename.split("_")[1].split(".")[0])
            tfidf_vector = {}

            with open(os.path.join(Path(__file__).parent /output_dir, filename), "r", encoding="utf-8") as file:
                for line in file:
                    term, _, tf_idf = line.strip().split()
                    tfidf_vector[term] = float(tf_idf)
                    vocabulary.add(term)
            tfidf_data[page_num] = tfidf_vector

    return tfidf_data, vocabulary


def load_pages_url(urls_filename) -> dict[int, str]:
    """Загружает ссылки на страницы."""
    urls_dir = {}
    with open(Path(__file__).parent / urls_filename, "r", encoding="utf-8") as file:
        for page_number, line in enumerate(file):
            _, url = line.strip().split()
            urls_dir[page_number] = url
    return urls_dir


def preprocess_query(query, vocabulary) -> dict[str, int]:
    """Токенизирует запрос и создает вектор TF-IDF для запроса."""
    query_terms = query.lower().split()
    query_vector = {term: 1 for term in query_terms if term in vocabulary}
    return query_vector


def compute_cosine_similarity(query_vector, document_vectors, vocabulary):
    """Вычисляет косинусное сходство между запросом и документами."""
    query_array = np.array([query_vector.get(term, 0) for term in vocabulary])

    similarities = []
    for page_num, doc_vector in document_vectors.items():
        doc_array = np.array([doc_vector.get(term, 0) for term in vocabulary])
        similarity = cosine_similarity([query_array], [doc_array])[0][0]
        similarities.append((page_num, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities


def search(query, output_dir, urls_name):
    """Осуществляет поиск по запросу."""
    tfidf_data, vocabulary = load_tfidf_data(output_dir)
    query_vector = preprocess_query(query, vocabulary)
    similarities = compute_cosine_similarity(query_vector, tfidf_data, vocabulary)
    print("Результаты поиска:")
    return [[page_num, urls_name.get(page_num), similarity] for page_num, similarity in similarities if similarity > 0]


def get_result_info(pages_info):
    for page_num, url, similarity in pages_info:
        print(f'Страница {page_num}: {url}, сходство: {similarity}')


if __name__ == "__main__":
    query = input("Введите запрос: ")
    urls_name = load_pages_url(URLS_FILENAME)
    result = search(query, OUTPUT_DIR, urls_name)
    get_result_info(result)
