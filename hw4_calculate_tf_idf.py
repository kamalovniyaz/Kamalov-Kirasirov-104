import os
import math
from collections import defaultdict


def read_files(directory):
    """Чтение файлов из директории."""
    data = {}
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                continue
            data[filename] = content.split()
    return data


def calculate_tf(tokens, total_terms):
    """Расчет TF для терминов или лемм в документе."""
    term_count = defaultdict(int)
    for term in tokens:
        term_count[term] += 1
    if total_terms == 0:
        tf = {term: 0 for term in term_count}
    else:
        tf = {term: count / total_terms for term, count in term_count.items()}
    return tf


def calculate_idf(documents, terms):
    """Расчет IDF для терминов или лемм."""
    num_docs = len(documents)
    term_doc_count = defaultdict(int)
    for doc in documents.values():
        unique_terms = set(doc)
        for term in unique_terms:
            term_doc_count[term] += 1
    idf = {
        term: math.log(max(1, num_docs / (1 + term_doc_count[term])))
        for term in terms
    }
    return idf


def save_results(filename, data):
    """Сохранение результатов в файл."""
    with open(filename, 'w', encoding='utf-8') as file:
        for term, (idf, tf_idf) in data.items():
            if tf_idf > 0:
                file.write(f"{term} {idf} {tf_idf}\n")


def main(dumps_dir, tokens_dir, lemmas_dir, output_dir):
    dumps_data = read_files(dumps_dir)

    tokens_data = read_files(tokens_dir)
    lemmas_data = read_files(lemmas_dir)

    dumps_keys = {key.replace("dump_", ""): key for key in dumps_data.keys()}
    tokens_keys = {key.replace("tokens_", ""): key for key in tokens_data.keys()}
    lemmas_keys = {key.replace("lemmas_", ""): key for key in lemmas_data.keys()}

    common_numbers = set(dumps_keys.keys()) & set(tokens_keys.keys()) & set(lemmas_keys.keys())
    if not common_numbers:
        raise ValueError("Нет совпадающих файлов в папках dumps, tokens и lemmas.")

    filtered_dumps_data = {dumps_keys[num]: dumps_data[dumps_keys[num]] for num in common_numbers}
    filtered_tokens_data = {tokens_keys[num]: tokens_data[tokens_keys[num]] for num in common_numbers}
    filtered_lemmas_data = {lemmas_keys[num]: lemmas_data[lemmas_keys[num]] for num in common_numbers}

    all_terms = set(term for doc in filtered_tokens_data.values() for term in doc)
    all_lemmas = set(lemma for doc in filtered_lemmas_data.values() for lemma in doc)

    idf_terms = calculate_idf(filtered_tokens_data, all_terms)
    idf_lemmas = calculate_idf(filtered_lemmas_data, all_lemmas)

    # Обработка каждого документа
    for doc_num in common_numbers:
        doc_name = f"dump_{doc_num}"
        tokens_name = f"tokens_{doc_num}"
        lemmas_name = f"lemmas_{doc_num}"

        # Общее количество слов в документе
        total_terms = len(filtered_dumps_data[doc_name])

        # Термины
        tokens = filtered_tokens_data[tokens_name]
        tf_terms = calculate_tf(tokens, total_terms)
        tf_idf_terms = {term: tf * idf_terms.get(term, 0) for term, tf in tf_terms.items()}

        # Леммы
        lemmas = filtered_lemmas_data[lemmas_name]
        tf_lemmas = calculate_tf(lemmas, total_terms)
        tf_idf_lemmas = {lemma: tf * idf_lemmas.get(lemma, 0) for lemma, tf in tf_lemmas.items()}

        # Сохранение результатов
        save_results(os.path.join(output_dir, f"terms_{doc_num}"),
                     {term: (idf_terms.get(term, 0), tf_idf_terms.get(term, 0))
                      for term in all_terms if term in tf_terms})

        save_results(os.path.join(output_dir, f"lemmas_{doc_num}"),
                     {lemma: (idf_lemmas.get(lemma, 0), tf_idf_lemmas.get(lemma, 0))
                      for lemma in all_lemmas if lemma in tf_lemmas})


if __name__ == "__main__":
    dumps_directory = "dumps"
    tokens_directory = "tokens"
    lemmas_directory = "lemmas"
    output_directory = "output"

    main(dumps_directory, tokens_directory, lemmas_directory, output_directory)