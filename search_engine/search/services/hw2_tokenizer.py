import os
import glob
from bs4 import BeautifulSoup
import re
from natasha import (
    Segmenter,  # 
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    Doc
)

DUMPS_DIR = 'dumps'
TOKENS_DIR = 'tokens'
LEMMAS_DIR = 'lemmas'

# Инициализация компонентов Natasha
segmenter = Segmenter()  # Токенизатор
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)

IGNORED_POS = {
    "CCONJ",  # Союзы (например, "и", "или")
    "SCONJ",  # Союзы (например, "то", "что")
    "ADP",  # Предлоги (например, "в", "на")
    "PART",  # Частицы (например, "же", "ли")
    "ADP",  # Предлоги (например, "в", "на")
}
INORED_WORDS = {"бы", "на", "как", "если"} # Игнорировать отдельно (Natasha не распознает их как игнорируемые части речи)

# Возвращает из html файла токены и леммы
def get_tokens(file_path) -> list[tuple[str, str]]:
    # Получаем текст из HTML-файла 
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Удаляем все теги <code> и их содержимое
    for code_tag in soup.find_all('code'):
        code_tag.extract()
    text = soup.get_text(separator=' ', strip=True)

    # Оставляем только слова, удаляя все остальное (числа, знаки препинания и т.д.)
    words = re.findall(r'[а-яА-ЯёЁ]+', text)

    doc = Doc(" ".join(words))
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)

    # Лемматизация
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
    
    return [
        (token.text, token.lemma) for token in doc.tokens if 
                token.pos not in IGNORED_POS and
                token.lemma.lower() not in INORED_WORDS and
                len(token.lemma) > 1
    ]


def process_html_files():
    input_folder = os.path.join(DUMPS_DIR, 'dump_*.txt')

    # Создаем папки для токенов и лемм, если их нет
    os.makedirs(TOKENS_DIR, exist_ok=True)
    os.makedirs(LEMMAS_DIR, exist_ok=True)
    
    files = glob.glob(input_folder)
    for file_path in files:
        file_name = os.path.basename(file_path)
        file_number = re.search(r'\d+', file_name).group()
        
        have = set()
        words = []
        lemmas = {}

        for word, lemma in get_tokens(file_path):
            if word.lower() not in have:
                have.add(word.lower())

                words.append(word)
                if lemma.lower() not in lemmas:
                    lemmas[lemma.lower()] = [word]
                else:
                    lemmas[lemma.lower()].append(word)
        
        tokens_file_path = os.path.join(TOKENS_DIR, f'tokens_{file_number}.txt')
        with open(tokens_file_path, 'w', encoding='utf-8') as f:
            for word in sorted(words):
                f.write(f"{word}\n")
        
        lemmas_file_path = os.path.join(LEMMAS_DIR, f'lemmas_{file_number}.txt')
        with open(lemmas_file_path, 'w', encoding='utf-8') as f:
            for lemma in sorted(lemmas):
                f.write(f"{lemma}: {' '.join(lemmas[lemma])}\n")

if __name__ == "__main__":
    process_html_files()