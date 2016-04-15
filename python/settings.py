BASE_URL = 'http://it-ebooks.info'
DOWNLOAD_DIR = 'downloaded_books'

CUSTOM_USERAGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'

TITLE_SELECTOR = 'h1[itemprop="name"]'
DESCRIPTION_SELECTOR = 'span[itemprop="description"]'
AUTHORS_SELECTOR = 'b[itemprop="author"]'
ISBN_SELECTOR = 'b[itemprop="isbn"]'
YEAR_SELECTOR = 'b[itemprop="datePublished"]'
PAGES_SELECTOR = 'b[itemprop="numberOfPages"]'
URL_SELECTOR = 'td a[href*="http://filepi.com"]'
FORMAT_SELECTOR = 'b[itemprop="bookFormat"]'
