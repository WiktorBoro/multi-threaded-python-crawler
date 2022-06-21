# Multi threaded python crawler

## Scrap One Page
`ScrapOnePage(url='https://www.crummy.com/software/BeautifulSoup/bs4/doc/', everything=True).return_result_dict()`

In `ScrapOnePage()` we indicate the url address and optionally the following parameters:

`everything=False/True`

`outbound_links=False/True,`

`internal_links=False/True,`

`h1=False/True,`

`h2=False/True,`

`h3=False/True,`

`canonical=False/True,`

`title=False/True,`

`meta_description=False/True,`

`img=False/True,`



All parameters are optional and define what we want to scrape.

If the website has a special encoding, for example Polish special characters, we can use:

`decode=''`

As a result we get dict in dict:

`{url-we-scrap: {result}}`

For graphics internal/outbound links we get dict where keys it's internal/outbound links and the values are a list, where the first value is always number of number of occurrences for the link, and the rest of the values are anchor:

For graphics, we get dict where the keys are the addresses of the graphics and the values are the number of their appearances


## Crawl entire page

`CrawlEntirePage(url='https://www.crummy.com/software/BeautifulSoup/bs4/doc/', everything=True).start_crawl()`

In `CrawlEntirePage()` we indicate start url and the same parameters as with `ScrapOnePage()`.

In `start_crawl()` we optional indicate the:

`number_of_threaded=1`

`sleep_time=0`

`file_loc=''`

`condition_allow=''` - regex

`condition_disallow=''` - regex

The result will be saved as csv
