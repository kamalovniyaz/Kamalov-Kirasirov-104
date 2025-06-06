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

from search_engine.search.constants import TOKENS_DIR, DUMPS_DIR, LEMMAS_DIR

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


def process_html_files():
    input_folder = os.path.join(DUMPS_DIR, 'dump_*.txt')

    # Создаем папки для токенов и лемм, если их нет
    os.makedirs(TOKENS_DIR, exist_ok=True)
    os.makedirs(LEMMAS_DIR, exist_ok=True)
    
    files = glob.glob(input_folder)
    for file_path in files:
        file_name = os.path.basename(file_path)
        file_number = re.search(r'\d+', file_name).group()
        
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
        
        tokens = [
            token for token in doc.tokens if 
                    token.pos not in IGNORED_POS and
                    token.lemma.lower() not in INORED_WORDS and
                    len(token.lemma) > 1
        ]


        have = set()
        words = []
        lemmas = {}

        for token in tokens:
            if token.text.lower() not in have:
                have.add(token.text.lower())

                words.append(token.text)
                if token.lemma.lower() not in lemmas:
                    lemmas[token.lemma.lower()] = [token.text]
                else:
                    lemmas[token.lemma.lower()].append(token.text)
        
        tokens_file_path = os.path.join(TOKENS_DIR, f'tokens_{file_number}.txt')
        with open(tokens_file_path, 'w', encoding='utf-8') as f:
            for word in words:
                f.write(f"{word}\n")
        
        lemmas_file_path = os.path.join(LEMMAS_DIR, f'lemmas_{file_number}.txt')
        with open(lemmas_file_path, 'w', encoding='utf-8') as f:
            for lemma, words in lemmas.items():
                f.write(f"{lemma}: {' '.join(words)}\n")

if __name__ == "__main__":
    process_html_files()