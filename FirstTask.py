"""
Поиск наиболее популярных словосочетаний во всех документах указанной папки
"""

from typing import Tuple, List, Dict
import re
import os
import pymorphy2
import string

directory_name = 'ForMap'


def main():
    data_dict = get_data_dict()
    full_map_res: List[Tuple[str, int]] = []
    for doc_id in data_dict.keys():
        doc_id, map_res = map_fn(doc_id, data_dict[doc_id])
        full_map_res += map_res

    shuffle_res = shuffle_fn(full_map_res)
    reduce_res = reduce_fn(shuffle_res)

    for word, value in reduce_res.items():
        print(f'{word}: {value}')


def get_data_dict():
    file_names = os.listdir(f"./{directory_name}")
    data_dict = dict()
    for file_ in file_names:
        with open(f"./{directory_name}/{file_}") as file:
            data = file.read()
            data = data.replace("\n", " ")
            data_dict[f"{directory_name}/{file_}"] = data
    return data_dict


def pos(word, morth=pymorphy2.MorphAnalyzer()):
    return morth.parse(word)[0].tag.POS


def map_fn(doc_id: str, data: str) -> Tuple[str, List[Tuple[str, int]]]:
    out_dict: List[Tuple[str, int]] = []
    data = data.translate(str.maketrans('', '', string.punctuation))
    new_text = re.split('\s+', data.lower())
    for ind in range(len(new_text) - 2):
        new_str = new_text[ind] + ' ' + new_text[ind + 1]
        if check_morp(new_str):
            new_str += ' ' + new_text[ind + 2]
        out_dict.append((new_str, 1))
    return doc_id, out_dict


def check_morp(new_str):
    functors_pos = {'INTJ', 'PRCL', 'CONJ', 'PREP'}
    check = False
    for word in new_str.split():
        if pos(word) in functors_pos:
            check = True
    return check


def shuffle_fn(items: List[Tuple[str, int]]) -> Dict[str, List[int]]:
    out_dict: Dict[str, List[int]] = {}
    for key, value in items:
        if key not in out_dict:
            out_dict[key] = [value, ]
        else:
            out_dict[key].append(value)
    return out_dict


def reduce_fn(items: Dict[str, List[int]]) -> Dict[str, int]:
    out_dict = {}
    for key, values in items.items():
        if key not in out_dict:
            out_dict[key] = sum(values)
        else:
            out_dict[key] += 1
    return out_dict


if __name__ == '__main__':
    main()
