import re
import os
import logging

from collections import namedtuple
from multiprocessing import Pool

import lxml.html
import requests


import settings as pref


logging.basicConfig(level=logging.INFO)

Book = namedtuple('Book', ('title', 'description',
                           'authors', 'url',
                           'year', 'publisher',
                           'pages', 'ISBN',
                           'format', 'origin_url'))


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
    if not r.status_code == 200:
        logging.info("Incorrect status code: {}".format(r.status_code))
        return None
    return _parse_book_from_text(r.text, url)


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


def _parse_book_from_text(text, origin_url):
    tree = lxml.html.fromstring(text)

    book_title = get_first_selector_value(tree, pref.TITLE_SELECTOR).text
    book_description = get_first_selector_value(tree, pref.DESCRIPTION_SELECTOR).text
    book_url = get_first_selector_value(tree, pref.URL_SELECTOR).get('href')
    book_year = get_first_selector_value(tree, pref.YEAR_SELECTOR).text
    book_pages = get_first_selector_value(tree, pref.PAGES_SELECTOR).text
    book_authors = get_first_selector_value(tree, pref.AUTHORS_SELECTOR).text
    book_format = get_first_selector_value(tree, pref.FORMAT_SELECTOR).text

    return Book(title=book_title,
                description="",
                authors=book_authors,
                url=book_url,
                year=book_year,
                publisher="",
                pages=book_pages,
                ISBN="",
                format=book_format,
                origin_url=origin_url)


def download_book(book_obj):
    if book_obj is None:
        pass
    logging.info("Downloading {}".format(book_obj.title))
    print(book_obj)


def download_book_by_url(book_url):
    book = parse_book_from_url(book_url)
    if book is None:
        logging.info("Url {} contains no book data!".format(book_url))
    logging.info("Book obtained {}".format(book))
    output_filename = os.path.join(pref.DOWNLOAD_DIR,
                                   ".".join([book.title, book.format]))
    download_file(book.url, output_filename, book_url)


def download_file(url, output_file, original_url):
    headers = {
        "Referer": original_url
    }
    r = requests.get(url, headers=headers, stream=True)
    with open(output_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return output_file


def main():
    print(get_latest_book_id())
    # books = (parse_book_from_url(u) for u in get_book_url_generator(1, 10))
    # books = list(books)
    book_urls = list(get_book_url_generator(1, 50))
    pool = Pool(6)
    pool.map(download_book_by_url, book_urls)
    # prepare_dir()


if __name__ == '__main__':
    main()
