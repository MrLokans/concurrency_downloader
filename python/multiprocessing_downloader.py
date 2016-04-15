import re
import os
import logging

from collections import namedtuple

import lxml.html
import requests


import settings as pref


logging.basicConfig(level=logging.DEBUG)

Book = namedtuple('Book', ('title', 'description',
                           'authors', 'url',
                           'year', 'publisher',
                           'pages', 'ISBN'))


def extract_id_from_text(text):
    book_id = re.findall(r'\d+', text)

    if not book_id:
        raise ValueError('Text does not contain any ID.')
    return int(book_id[-1])


def get_latest_book_id():
    book_id = 0
    page_html = requests.get(pref.BASE_URL,
                             headers={'User-Agent': pref.CUSTOM_USERAGENT}).text
    tree = lxml.html.fromstring(page_html)
    book_elem = get_first_selector_value(tree, 'td.top td a')
    book_id = extract_id_from_text(book_elem.get('href'))
    logging.debug('Latest book id is {}'.format(book_id))
    return book_id


def get_book_id_url(book_id):
    return "/".join([pref.BASE_URL, 'book', str(book_id)]) + '/'


def get_book_url_generator(first_id=1, last_id=100):
    return (get_book_id_url(x) for x in range(first_id, last_id+1))


def prepare_dir(download_dir=pref.DOWNLOAD_DIR):
    if not os.path.exists(download_dir):
        logging.info('Creating dir {}'.format(download_dir))
        os.mkdir(download_dir)


def parse_book_from_url(url):
    r = requests.get(url, headers={'User-Agent': pref.CUSTOM_USERAGENT})
    return _parse_book_from_text(r.text)


def get_first_selector_value(tree, selector, sel_type='css'):
    if sel_type == 'xpath':
        # root = tree.getroot()
        logging.debug('Looking by XPATH selector "{}"'.format(selector))
        selected = tree.xpath(selector)
        logging.debug('Elements found: '.format(selected))
        return selected[0]
    else:
        logging.debug('Looking for css selector "{}"'.format(selector))
        elements = tree.cssselect(selector)
        logging.debug('Elements found: '.format(elements))
        return elements[0]


def _parse_book_from_text(text):
    tree = lxml.html.fromstring(text)

    book_title = get_first_selector_value(tree, pref.TITLE_SELECTOR).text
    book_description = get_first_selector_value(tree, pref.DESCRIPTION_SELECTOR).text
    book_url = get_first_selector_value(tree, pref.URL_SELECTOR).get('href')
    book_year = get_first_selector_value(tree, pref.YEAR_SELECTOR).text
    book_pages = get_first_selector_value(tree, pref.PAGES_SELECTOR).text
    book_authors = get_first_selector_value(tree, pref.AUTHORS_SELECTOR).text

    return Book(title=book_title,
                description="",
                authors=book_authors,
                url=book_url,
                year=book_year,
                publisher="",
                pages=book_pages,
                ISBN="")


def main():
    print(get_latest_book_id())
    parse_book_from_url(get_book_id_url(20))
    prepare_dir()


if __name__ == '__main__':
    main()
