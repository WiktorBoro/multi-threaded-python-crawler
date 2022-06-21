from requests import get, exceptions
from bs4 import BeautifulSoup
from re import match
from pandas import DataFrame
from datetime import datetime
import threading
from time import sleep
from re import findall


class _CrawlInit:
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
                 img=False,
                 decode=''):
        self._url = url
        self._everything = everything
        self._outbound_links = outbound_links
        self._internal_links = internal_links
        self._h1 = h1
        self._h2 = h2
        self._h3 = h3
        self._canonical = canonical
        self._title = title
        self._meta_description = meta_description
        self._img = img
        self._domain = match(r'(https?:\/\/)?(www\.)?([^\/]+)(\/.*)?', self._url).groups()[2]
        self._decode = decode


class _PageToCrawl:
    def __init__(self, started_page: str):

        self._page_to_crawl = [started_page]

    def get_page_to_crawl(self) -> list:
        return self._page_to_crawl

    def set_page_to_crawl(self, internal_links_from_crawl):
        self._page_to_crawl += list(filter(lambda x: x not in self._page_to_crawl, internal_links_from_crawl))


class CrawlEntirePage(_CrawlInit):

    def start_crawl(self,
                    number_of_threaded=1,
                    sleep_time=0,
                    file_loc='',
                    condition_allow='',
                    condition_disallow=''):

        self._internal_links = True

        pages_to_crawl = _PageToCrawl(self._url)

        full_file_path = file_loc + self._domain + " " + str(datetime.now().strftime("%d-%m-%Y %H-%M")) + '.csv'

        CrawlOnePage(url=self._url,
                     everything=self._everything,
                     outbound_links=self._outbound_links,
                     internal_links=self._internal_links,
                     h1=self._h1,
                     h2=self._h2,
                     h3=self._h3,
                     canonical=self._canonical,
                     title=self._title,
                     meta_description=self._meta_description,
                     img=self._img).save_result_to_csv(full_file_path, pages_to_crawl)

        crawled_page_num = 1
        while True:
            # +1 because we always start with one main thread, and we want run only "extra" thread
            for i in range(number_of_threaded-threading.active_count()+1):

                page_to_crawl = pages_to_crawl.get_page_to_crawl()[crawled_page_num]

                try:
                    if condition_allow:
                        if findall(condition_allow, page_to_crawl):
                            pass
                        else:
                            crawled_page_num += 1
                            continue
                    if condition_disallow:
                        if findall(condition_disallow, page_to_crawl):
                            crawled_page_num += 1
                            continue

                    threading.Thread(target=self._run_thread, args=(page_to_crawl,
                                                                    full_file_path,
                                                                    pages_to_crawl)).start()
                    # -1 because we want print only "extra" thread without main thread
                    print(f"Active thread {threading.active_count() - 1}")
                    print(f"Current page {crawled_page_num}/{len(pages_to_crawl.get_page_to_crawl())}")
                    crawled_page_num += 1
                    sleep(sleep_time)
                except IndexError:
                    # if we get IndexError we wait 2 seconds to make sure that other threads do not bring new links
                    sleep(2)
                    crawled_page_num += 1
                    # if the current number is still outside the list we need to break loop
                    if crawled_page_num >= len(pages_to_crawl.get_page_to_crawl()):
                        break
            # if the current number is outside the list we need to break loop
            if crawled_page_num >= len(pages_to_crawl.get_page_to_crawl()):
                print(f"Current page {crawled_page_num}/{len(pages_to_crawl.get_page_to_crawl())}")
                print("DONE!")
                break

    def _run_thread(self, url_to_crawl, full_file_path, pages_to_crawl):
        CrawlOnePage(url=url_to_crawl,
                     everything=self._everything,
                     outbound_links=self._outbound_links,
                     internal_links=self._internal_links,
                     h1=self._h1,
                     h2=self._h2,
                     h3=self._h3,
                     canonical=self._canonical,
                     title=self._title,
                     meta_description=self._meta_description,
                     img=self._img).save_result_to_csv(full_file_path, pages_to_crawl)


class CrawlOnePage(_CrawlInit):
    def crawl_one_page(self, result_dict):
        response = self._get_response(self._url, result_dict)

        if self._url != response.url:
            result_dict[self._url].update({'Redirect to': response.url})

        self._get_status_code(response, result_dict)

        if response.status_code != 200:
            # in dictionary status code is update so we can just end scrap this url
            return result_dict

        if self._decode:
            soup = BeautifulSoup(response.content.decode(self._decode), features="html.parser")
        else:
            soup = BeautifulSoup(response.text, features="html.parser")

        if any([self._title, self._everything]):
            self._get_title(soup=soup, result_dict=result_dict)
        if any([self._meta_description, self._everything]):
            self._get_meta_desc(soup=soup, result_dict=result_dict)
        if any([self._h1, self._everything]):
            self._get_h1(soup=soup, result_dict=result_dict)
        if any([self._h2, self._everything]):
            self._get_h2(soup=soup, result_dict=result_dict)
        if any([self._h3, self._everything]):
            self._get_h3(soup=soup, result_dict=result_dict)
        if any([self._canonical, self._everything]):
            self._get_canonical(soup=soup, result_dict=result_dict)
        if any([self._img, self._everything]):
            self._get_img_url(soup=soup, result_dict=result_dict)
        if any([self._internal_links, self._outbound_links, self._everything]):
            self._get_links(soup=soup, result_dict=result_dict)

    def _get_response(self, url: str, result_dict: dict):
        try:
            response = get(url, timeout=10)
        except exceptions.RequestException:
            result_dict[self._url].update({'Error message': 'Could not connect, unknown error'})
            raise self.return_result_dict()
        return response

    def _get_status_code(self, response, result_dict):
        result_dict[self._url].update({'status code':
                                               [status.status_code for status in response.history]
                                                    if response.history else [response.status_code]})

    def _get_h1(self, soup, result_dict):
        result_dict[self._url].update({'h1': [i.get_text() for i in soup.find_all('h1')]})

    def _get_h2(self, soup, result_dict):
        result_dict[self._url].update({'h2': [i.get_text() for i in soup.find_all('h2')]})

    def _get_h3(self, soup, result_dict):
        result_dict[self._url].update({'h3': [i.get_text() for i in soup.find_all('h3')]})

    def _get_title(self, soup, result_dict):
        result_dict[self._url].update({'title': [i.get_text() for i in soup.find_all('title')]})

    def _get_meta_desc(self, soup, result_dict):
        result_dict[self._url].update({'meta description':
                                               [i['content'] for i in soup.find_all('meta', attrs={'name': 'description'})]})

    def _get_canonical(self, soup, result_dict):
        result_dict[self._url].update({'canonical': {i['href']: 'self-canonical' if i['href'] == self._url
                                                         else 'canonical side is indicated'
                                                     for i in soup.find_all('link', attrs={'rel': 'canonical'})}})

    def _get_img_url(self, soup, result_dict):
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

        result_dict[self._url].update({'img': img_dict})

    def _get_links(self, soup, result_dict):
        links_dict = {}
        for i in soup.find_all('a'):
            # sometime a don't have href, just no link there
            try:
                ihref = i['href']
            except KeyError:
                continue

            if match(r'(^#$)|(^$)', ihref):
                continue

            if match(r'^\/', ihref):
                ihref = 'https://' + self._domain + ihref

            if ihref in links_dict:
                links_dict[ihref][0] += 1
                links_dict[ihref].append(i.get_text())

            elif ihref not in links_dict:
                links_dict[ihref] = [1, i.get_text()]

        if any([self._internal_links, self._everything]):
            result_dict[self._url].update({'internal links':
                                                   {k: v for k, v in links_dict.items()
                                                    if match(f'https?:\/\/(www\.)?{self._domain}.*', k)}})
        if any([self._outbound_links, self._everything]):
            result_dict[self._url].update({'outgoing links':
                                                   {k: v for k, v in links_dict.items()
                                                    if match(f'(https?:\/\/(www\.)?(?!{self._domain}).*)', k)}})

    def return_result_dict(self):
        result_dict = {self._url: {}}
        self.crawl_one_page(result_dict)
        return result_dict

    def save_result_to_csv(self, full_file_path, page_to_crawl):
        result_dict = {self._url: {}}
        self.crawl_one_page(result_dict)

        if 'internal links' in result_dict[self._url].keys():
            page_to_crawl.set_page_to_crawl(set(result_dict[self._url]['internal links']))
        df = DataFrame(result_dict)
        df.to_csv(full_file_path, mode='a')
