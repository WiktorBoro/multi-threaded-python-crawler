from requests import get, exceptions
from bs4 import BeautifulSoup
from re import match
from pandas import DataFrame
from os.path import exists


class PageToCrawl:
    def __init__(self):
        self.page_to_crawl = set()

    def set_result(self, page_list):
        self.page_to_crawl.add(x for x in page_list)

    def get_result(self):
        return self.page_to_crawl


class CrawlOnePage():
    def __init__(self,
                 url,
                 everything=False,
                 outbound_links=False,
                 internal_links=False,
                 h1=False,
                 h2=False,
                 h3=False,
                 canonical=False,
                 title=False,
                 meta_description=False,
                 img=False):

        self._result_dict = {self._url: {}}

        response = self._get_response(url)
        self._url = response.url
        self._domain = match(r'https?:\/\/([^\/]+)\/.*', self._url).groups()[0]

        self._get_status_code(response)
        soup = BeautifulSoup(response.text, features="html.parser")
        self._get_status_code(response)
        if response.status_code != 200:
            # in dictionary status code is update so we can just end scrap this url
            raise self.return_result_dict()
        if any([title, everything]):
            self._get_title(soup)
        if any([meta_description, everything]):
            self._get_meta_desc(soup)
        if any([h1, everything]):
            self._get_h1(soup)
        if any([h2, everything]):
            self._get_h2(soup)
        if any([h3, everything]):
            self._get_h3(soup)
        if any([canonical, everything]):
            self._get_canonical(soup)
        if any([img, everything]):
            self._get_img_url(soup)
        if any([internal_links, outbound_links, everything]):
            self._get_links(soup, internal_links, outbound_links, everything)

    def _get_response(self, url):
        try:
            response = get(url)
        except exceptions.RequestException as e:
            self._result_dict[self._url].update({'Error message': 'Could not connect, unknown error'})
            raise self.return_result_dict()
        return response

    def _get_status_code(self, response):
        self._result_dict[self._url].update({'status code':
                                               [status.status_code for status in response.history]
                                                    if response.history else [response.status_code]})

    def _get_h1(self, soup):
        self._result_dict[self._url].update({'h1': [i.get_text() for i in soup.find_all('h1')]})

    def _get_h2(self, soup):
        self._result_dict[self._url].update({'h2': [i.get_text() for i in soup.find_all('h2')]})

    def _get_h3(self, soup):
        self._result_dict[self._url].update({'h3': [i.get_text() for i in soup.find_all('h3')]})

    def _get_title(self, soup):
        self._result_dict[self._url].update({'title': [i.get_text() for i in soup.find_all('title')]})

    def _get_meta_desc(self, soup):
        self._result_dict[self._url].update({'meta description':
                                               [i['content'] for i in soup.find_all('meta', attrs={'name': 'description'})]})

    def _get_canonical(self, soup):
        self._result_dict[self._url].update({'canonical': {i['href']: 'self-canonical' if i['href'] == self._url
                                                         else 'canonical side is indicated'
                                                           for i in soup.find_all('link', attrs={'rel': 'canonical'})}})

    def _get_img_url(self, soup):
        img_dict = {}
        # learned by accident from ahref, I added a security
        for i in soup.find_all('img'):
            try:
                isrc = i['src']
            except KeyError:
                continue
            if match(r'^\/', isrc):
                isrc = 'https://' + self._domain + isrc

            if isrc in img_dict:
                img_dict[isrc] += 1
            elif isrc not in img_dict:
                img_dict[isrc] = 1

        self._result_dict[self._url].update({'img': img_dict})

    def _get_links(self, soup, internal_links, outbound_links, everything):
        links_dict = {}
        for i in soup.find_all('a'):
            # sometime a don't have href, just no link there
            try:
                ihref = i['href']
            except KeyError:
                continue
            if match(r'^\/', ihref):
                ihref = 'https://' + self._domain + ihref
            if ihref in links_dict:
                links_dict[ihref][0] += 1
                links_dict[ihref].append(i.get_text())

            elif ihref not in links_dict:
                links_dict[ihref] = [1, i.get_text()]

        if any([internal_links, everything]):
            self._result_dict[self._url].update({'internal links':
                                                   {k: v for k, v in links_dict.items()
                                                    if match(f'(https?:\/\/{self._domain}.*)|^#$|^$', k)}})
        if any([outbound_links, everything]):
            self._result_dict[self._url].update({'outgoing links':
                                                   {k: v for k, v in links_dict.items()
                                                    if match(f'(https?:\/\/(?!{self._domain}).*)', k)}})

    def return_result_dict(self):
        return self._result_dict

    def save_result_to_csv(self, file_loc):
        if not exists(file_loc):
            df = DataFrame.from_dict(self._result_dict)
            df.to_csv(file_loc, index=False, header=True)
        else:
            df = DataFrame.from_dict(self._result_dict)
            df.to_csv(file_loc, mode='a', header=False)


class CrawlEntirePage:
    def __init__(self,
                 domain,
                 number_of_threaded=1,
                 sleep_time=0,
                 everything=False,
                 outbound_links=False,
                 internal_links=False,
                 h1=False,
                 h2=False,
                 h3=False,
                 canonical=False,
                 title=False,
                 meta_description=False,
                 img=False):
        self.everything = everything,
        self.outbound_links = outbound_links,
        self.internal_links = internal_links,
        self.h1 = h1,
        self.h2 = h2,
        self.h3 = h3,
        self.canonical = canonical,
        self.title = title,
        self.meta_description = meta_description,
        self.img = img
        page_to_crawl = PageToCrawl()

    def start_crawl(self):
        pass
        # CrawlOnePage(url='url',
        #              everything=self.everything,
        #              outbound_links=self.outbound_links,
        #              internal_links=self.internal_links,
        #              h1=self.h1,
        #              h2=self.h2,
        #              h3=self.h3,
        #              canonical=self.canonical,
        #              title=self.title,
        #              meta_description=self.meta_description,
        #              img=self.img).save_result_to_csv()
