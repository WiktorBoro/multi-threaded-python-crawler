from requests import get, exceptions
from bs4 import BeautifulSoup
from re import match


class CrawlOnePage:
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

        response = self.get_response(url)
        self.url = response.url
        self.domain = match(r'https?:\/\/([^\/]+)\/.*', self.url).groups()[0]
        self.result_dict = {self.url: {}}

        self.get_status_code(response)
        soup = BeautifulSoup(response.text, features="html.parser")
        self.get_status_code(response)
        if response.status_code != 200:
            # in dictionary status code is update so we can just end scrap this url
            raise self.return_result_dict()
        if any([title, everything]):
            self.get_title(soup)
        if any([meta_description, everything]):
            self.get_meta_desc(soup)
        if any([h1, everything]):
            self.get_h1(soup)
        if any([h2, everything]):
            self.get_h2(soup)
        if any([h3, everything]):
            self.get_h3(soup)
        if any([canonical, everything]):
            self.get_canonical(soup)
        if any([img, everything]):
            self.get_img_url(soup)
        if any([internal_links, outbound_links, everything]):
            self.get_links(soup, internal_links, outbound_links, everything)

    def get_response(self, url):
        try:
            response = get(url)
        except exceptions.RequestException as e:
            self.result_dict[self.url].update({'Error message': 'Could not connect, unknown error'})
            raise self.return_result_dict()
        return response

    def get_status_code(self, response):
        self.result_dict[self.url].update({'status code':
                                               [status.status_code for status in response.history]
                                                    if response.history else [response.status_code]})

    def get_h1(self, soup):
        self.result_dict[self.url].update({'h1': [i.get_text() for i in soup.find_all('h1')]})

    def get_h2(self, soup):
        self.result_dict[self.url].update({'h2': [i.get_text() for i in soup.find_all('h2')]})

    def get_h3(self, soup):
        self.result_dict[self.url].update({'h3': [i.get_text() for i in soup.find_all('h3')]})

    def get_title(self, soup):
        self.result_dict[self.url].update({'title': [i.get_text() for i in soup.find_all('title')]})

    def get_meta_desc(self, soup):
        self.result_dict[self.url].update({'meta description':
                                               [i['content'] for i in soup.find_all('meta', attrs={'name': 'description'})]})

    def get_canonical(self, soup):
        self.result_dict[self.url].update({'canonical': {i['href']: 'self-canonical' if i['href'] == self.url
                                                         else 'canonical side is indicated'
                                                         for i in soup.find_all('link', attrs={'rel': 'canonical'})}})

    def get_img_url(self, soup):
        img_dict = {}
        # learned by accident from ahref, I added a security
        for i in soup.find_all('img'):
            try:
                isrc = i['src']
            except KeyError:
                continue
            if match(r'^\/', isrc):
                isrc = 'https://'+self.domain+isrc

            if isrc in img_dict:
                img_dict[isrc] += 1
            elif isrc not in img_dict:
                img_dict[isrc] = 1

        self.result_dict[self.url].update({'img': img_dict})

    def get_links(self, soup, internal_links, outbound_links, everything):
        links_dict = {}
        for i in soup.find_all('a'):
            # sometime a don't have href, just no link there
            try:
                ihref = i['href']
            except KeyError:
                continue
            if match(r'^\/', ihref):
                ihref = 'https://'+self.domain+ihref
            if ihref in links_dict:
                links_dict[ihref][0] += 1
                links_dict[ihref].append(i.get_text())

            elif ihref not in links_dict:
                links_dict[ihref] = [1, i.get_text()]

        if any([internal_links, everything]):
            self.result_dict[self.url].update({'internal links':
                                                   {k: v for k, v in links_dict.items()
                                                    if match(f'(https?:\/\/{self.domain}.*)|^#$|^$', k)}})
        if any([outbound_links, everything]):
            self.result_dict[self.url].update({'outgoing links':
                                                   {k: v for k, v in links_dict.items()
                                                    if match(f'(https?:\/\/(?!{self.domain}).*)', k)}})

    def return_result_dict(self):
        return self.result_dict
