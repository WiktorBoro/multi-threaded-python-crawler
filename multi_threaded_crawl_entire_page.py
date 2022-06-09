from crawl_one_page import CrawlOnePage
from threading import Thread
from re import findall
from time import sleep


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

    def start_crawl(self):
        CrawlOnePage(url='url',
                     everything=self.everything,
                     outbound_links=self.outbound_links,
                     internal_links=self.internal_links,
                     h1=self.h1,
                     h2=self.h2,
                     h3=self.h3,
                     canonical=self.canonical,
                     title=self.title,
                     meta_description=self.meta_description,
                     img=self.img).save_result_to_csv()


