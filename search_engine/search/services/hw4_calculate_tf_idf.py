import glob
import os
import math
from collections import defaultdict
import re

from hw2_tokenizer import get_tokens

OUTPUT_DIR = 'output'
DUMPS_DIR = 'dumps'

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


def calculate_tf(tokens):
    """Расчет TF для терминов или лемм в документе."""
    term_count = defaultdict(int)
    for term in tokens:
        term_count[term] += 1
    if len(tokens) == 0:
        return tokens
    else:
        tf = {term: count / len(tokens) for term, count in term_count.items()}
    return tf

# terms - список токенов, documents - словарь документ: список терминов
def calculate_idf(tokens, documents):
    """Расчет IDF для терминов или лемм."""
    num_docs = len(documents)
    term_doc_count = defaultdict(int)
    for doc in documents.values():
        unique_terms = set(doc)
        for term in unique_terms:
            term_doc_count[term] += 1
    idf = {
        term: math.log(num_docs / (1 + term_doc_count[term]))
        for term in tokens
    }
    return idf


def save_results(filename, data):
    """Сохранение результатов в файл."""
    with open(filename, 'w', encoding='utf-8') as file:
        for term in sorted(data):
            idf, tf_idf = data[term]
            if tf_idf > 0:
                file.write(f"{term} {idf} {tf_idf}\n")


def main(dumps_dir, output_dir):
    # 1. Для каждого файла в dumps получить типа 1: [] список терминов (для токенов и лемм)
    # 2. Посчитать tf для каждого документа
    # 3. Посчитать idf для каждого документа
    # 4. Сохранить результаты в файл

    file_numbers = []
    all_tokens = {}
    all_lemmas = {}

    for dump_file in glob.glob(os.path.join(DUMPS_DIR, 'dump_*.txt')):
        file_number = re.search(r'\d+', dump_file).group()
        file_numbers.append(file_number)

        for word, lemma in get_tokens(dump_file):
            if file_number not in all_tokens:
                all_tokens[file_number] = []
            all_tokens[file_number].append(word.strip().lower())

            if file_number not in all_lemmas:
                all_lemmas[file_number] = []
            all_lemmas[file_number].append(lemma.strip().lower())
    
    # --- tokens ---
    tokens_tf = {}
    for file_number, tokens in all_tokens.items():
        tokens_tf[file_number] = calculate_tf(tokens)

    tokens_idf = {}
    for file_number, tokens in all_tokens.items():
        tokens_idf[file_number] = calculate_idf(tokens, all_tokens)
    
    for file_number in file_numbers:
        output_file = os.path.join(output_dir, f"tokens_{file_number}.txt")
        result = {}
        for term in tokens_idf[file_number].keys():
            result[term] = (
                tokens_idf[file_number][term],
                tokens_tf[file_number][term] * tokens_idf[file_number][term]
            )
        save_results(output_file, result)

    # --- lemmas ---
    lemmas_tf = {}
    for file_number, lemmas in all_lemmas.items():
        lemmas_tf[file_number] = calculate_tf(lemmas)

    lemmas_idf = {}
    for file_number, lemmas in all_lemmas.items():
        lemmas_idf[file_number] = calculate_idf(lemmas, all_lemmas)

    for file_number in file_numbers:
        output_file = os.path.join(output_dir, f"lemmas_{file_number}.txt")
        result = {}
        for term in lemmas_idf[file_number].keys():
            result[term] = (
                lemmas_idf[file_number][term],
                lemmas_tf[file_number][term] * lemmas_idf[file_number][term]
            )
        save_results(output_file, result)
    
if __name__ == "__main__":
    main(DUMPS_DIR, OUTPUT_DIR)