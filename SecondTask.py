"""
Алгоритм постраничного поиска в запросе
"""

import collections
from collections import namedtuple
import os
import re

my_query = "Начать работу с JavaScript"
directory_name = "ForSearcher"
top_n = 2

document = namedtuple('document', 'name weight length')
posting_list_item = namedtuple('posting_list_item', 'document word weight')
word = namedtuple('word', 'word weight')

documents: list[document] = []
posting_list: list[posting_list_item] = []
words: list[word] = []

result_dict = dict()


def get_dict_from_article():
    file_names = os.listdir(f"./{directory_name}")
    data_dict = dict()
    for file_ in file_names:
        with open(f"./{directory_name}/{file_}") as file:
            data = file.read()
            data = data.replace("\n", " ")
            data_dict[f"{file_}"] = data
    return data_dict


def get_words_from_query(query):
    words_query = query.lower().split()
    return words_query


def fill_values(contents):
    for article, text in contents.items():
        words_dict = {}
        for phrase in re.split(r"[^\w']+", text.lower()):
            if phrase not in words_dict:
                words_dict[phrase] = 1
            else:
                words_dict[phrase] += 1
        for phrase, weight in words_dict.items():
            posting_list.append(posting_list_item(document=article, word=phrase, weight=weight))


def get_result_table(contents, query_words):
    for article, text in contents.items():
        words_in_text = text.lower().split()
        for index in range(len(words_in_text)):
            if words_in_text[index] in query_words:
                if article not in result_dict:
                    result_dict[article] = 1
                else:
                    result_dict[article] += 1


def search_my_query(str_query: str) -> dict[str, float]:
    scored = {}
    query = str_query
    for word in query:
        weight = 1
        for word_item in words:
            if word_item.word == word:
                weight = word_item.weight
                break
        for pl_item in posting_list:
            if pl_item.word == word:
                if pl_item.document in scored:
                    scored[pl_item.document] += pl_item.weight * weight
                else:
                    scored[pl_item.document] = pl_item.weight * weight
    for doc_id in scored.keys():
        weight = 1
        length = 1
        for doc in documents:
            if doc.name == doc_id:
                weight = doc.weight
                length = doc.length
                break
        scored[doc_id] = scored[doc_id] * weight / length
    return scored


def get_top_n(scored, n):
    second_dict = collections.defaultdict(list)
    for k, v in scored.items():
        second_dict[v].append(k)
    new_scored = sorted(second_dict.items())
    return new_scored[-n:]


def show_result(result):
    for item in result:
        document_id = item[1][0].split('.')[0]
        weight = item[0]
        print(f'Document = {document_id}; Weight = {weight}')


def main():
    contents = get_dict_from_article()
    query_words = get_words_from_query(query=my_query)
    get_result_table(contents=contents, query_words=query_words)
    fill_values(contents)
    words.append(word(word="python", weight=2))
    documents.append(document(name="PythonFirst", weight=2, length=1))
    result = search_my_query(str_query=query_words)
    result = get_top_n(result, top_n)
    show_result(result)


if __name__ == '__main__':
    main()
