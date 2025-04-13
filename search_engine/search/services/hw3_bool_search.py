import glob
import os
import re
import signal
import sys

from search_engine.search.constants import LEMMAS_DIR


def signal_handler(sig, frame):
    print('\n')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def build_inverted_index():
    inverted_index = {}

    for file_path in glob.glob(os.path.join(LEMMAS_DIR, 'lemmas_*.txt')):
        filename = os.path.basename(file_path)
        page_number = int(filename.split('_')[1].split('.')[0])

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                lemma_part, _ = line.split(':', 1)
                lemma = lemma_part.strip()
                if lemma not in inverted_index:
                    inverted_index[lemma] = set()
                inverted_index[lemma].add(page_number)

    return inverted_index

def save_inverted_index(index, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for lemma in sorted(index.keys()):
            pages = sorted(index[lemma])
            f.write(f"{lemma}: {', '.join(map(str, pages))}\n")


class SearchEngine:
    def __init__(self, inverted_index):
        self.inverted_index = inverted_index
        self.all_pages = self._get_all_pages()
        
    def _get_all_pages(self):
        all_pages = set()
        for pages in self.inverted_index.values():
            all_pages.update(pages)
        return sorted(all_pages)
    
    def process_query(self, query):
        postfix = self._parse_to_postfix(query)
        result = self._evaluate_postfix(postfix)
        return sorted(result)
    
    def _parse_to_postfix(self, query):
        precedence = {
            'NOT': 3,
            'AND': 2,
            'OR': 1,
            '(': 0
        }
        output = []
        operator_stack = []
        tokens = self._tokenize(query)
        
        for token in tokens:
            if token in ('AND', 'OR', 'NOT'):
                while (operator_stack and 
                       precedence[operator_stack[-1]] >= precedence[token]):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                operator_stack.pop()  # Удаляем '('
            else:
                output.append(token.lower())
                
        while operator_stack:
            output.append(operator_stack.pop())
            
        return output
    
    def _tokenize(self, query):
        regex = r'\b(?:AND|OR|NOT)\b|\(|\)|\b[\w\d]+\b'
        return re.findall(regex, query)
    
    def _evaluate_postfix(self, postfix):
        stack = []
        for token in postfix:
            if token == 'NOT':
                operand = stack.pop()
                result = self._not(operand)
                stack.append(result)
            elif token in ('AND', 'OR'):
                operand2 = stack.pop()
                operand1 = stack.pop()
                if token == 'AND':
                    result = self._and(operand1, operand2)
                else:
                    result = self._or(operand1, operand2)
                stack.append(result)
            else:
                stack.append(self._get_pages(token))
                
        return stack[0] if stack else set()
    
    def _get_pages(self, term):
        return set(self.inverted_index.get(term.lower(), []))
    
    def _and(self, a, b):
        return a.intersection(b)
    
    def _or(self, a, b):
        return a.union(b)
    
    def _not(self, a):
        return set(self.all_pages).difference(a)


if __name__ == "__main__":
    inverted_index = build_inverted_index()
    save_inverted_index(inverted_index, 'inverted_index.txt')
    engine = SearchEngine(inverted_index)
    while True:
        query = input("Введите запрос (или 'q' для выхода): ")
        if query.lower() in ['exit', 'quit', 'q']:
            break
        results = engine.process_query(query)
        print(f"Результаты поиска (номера страниц): {results}")