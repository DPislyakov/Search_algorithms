"""
Реализация алгоритма составления рейтинга документа
"""

import os
import collections
import requests
from bs4 import BeautifulSoup

directory_name = "ForRank"
static_ranks = list()
factor = 0.2

StaticRank = collections.namedtuple('StaticRank', 'name rank')


def get_urls():
    file_name = os.listdir(f"./{directory_name}")[1]
    with open(f"./{directory_name}/{file_name}") as file:
        data = file.read()
        data = data.replace("\n", " ").split()
    return data


def get_static_ranks():
    file_name = os.listdir(f"./{directory_name}")[0]
    with open(f"./{directory_name}/{file_name}") as file:
        data = file.read()
        data = data.replace("\n", " ").split()
    for info in data:
        static_ranks.append(StaticRank(name=info.split(",")[0], rank=info.split(",")[1]))


def get_href_links(url_links):
    all_url_links = dict()
    sessions = requests.Session()
    for url in url_links:
        links: list[str] = []
        response = sessions.get(url=url)
        soup = BeautifulSoup(response.text, "lxml")
        for link in soup.findAll('a'):
            href_link = link.get('href')
            if 'http' not in href_link:
                href_link = f"{url}{href_link}"
            links.append(href_link)
        all_url_links[url] = links
    return all_url_links


def check_static_rank(url_list):
    all_ranks = dict()
    for url in url_list:
        for doc, rank in static_ranks:
            if doc == url:
                all_ranks[url] = rank
                break
            else:
                all_ranks[url] = 1
    return all_ranks


def map_url(url_list, url_out, all_ranks):
    mapped_ranks = dict()
    for url in url_list:
        links = url_out[url]
        rank = all_ranks[url]
        for doc_id, rank in map_fn(k=url, v=(rank, links), url_list=url_list):
            if doc_id not in mapped_ranks.keys():
                mapped_ranks[doc_id] = []
            mapped_ranks[doc_id].append(rank)
    return mapped_ranks


def map_fn(k, v, url_list):
    rank, out_links = v
    yield k, 0
    if len(out_links) > 0:
        for out_link in out_links:
            yield out_link, float(rank) / len(out_links)
    else:
        for url in url_list:
            yield url, float(rank) / len(url_list)


def get_computed_ranks(mapped_ranks, url_list):
    computed_ranks = {}

    for doc_id, ranks in mapped_ranks.items():
        rank = calculate_rate(ranks, url_list)
        computed_ranks[doc_id] = rank
    return computed_ranks


def calculate_rate(rank_list, url_list):
    return (1 - factor) * sum(rank_list) + factor / len(url_list)


def print_ranks(rank_dict):
    for doc_id, rank in rank_dict.items():
        print(f'{doc_id}: Rank = {rank}')


def print_top_n_ranks(rank_dict, n):
    sort_orders = sorted(rank_dict.items(), key=lambda x: x[1], reverse=True)
    new_orders = sort_orders[1:n+1]
    print(f"Top {n} ranks:")
    for rank in new_orders:
        print(f'{rank[0]}: Rank = {rank[1]}')


def print_low_n_ranks(rank_dict, n):
    sort_orders = sorted(rank_dict.items(), key=lambda x: x[1])
    new_orders = sort_orders[2:n+2]
    print(f"Low {n} ranks:")
    for rank in new_orders:
        print(f'{rank[0]}: Rank = {rank[1]}')


def main():
    url_links = get_urls()
    get_static_ranks()
    url_out = get_href_links(url_links=url_links)
    all_ranks = check_static_rank(url_list=url_links)
    ranks = map_url(url_list=url_links, url_out=url_out, all_ranks=all_ranks)
    computed_ranks = get_computed_ranks(mapped_ranks=ranks, url_list=url_links)
    print_top_n_ranks(computed_ranks, 4)
    print_low_n_ranks(computed_ranks, 4)


if __name__ == '__main__':
    main()