from urllib.parse import urlsplit, urljoin

import requests
from lxml import html


urlmain = 'https://www.franceinter.fr/emissions/very-good-trip'

xpath = '//*[@id="content"]/div[3]/div[2]/div/div/div[1]/div[2]/section/article/div/div[2]/div[2]/header/div/a'

with open('urls','w') as urls_file:
    for i in range(1, 20):
        fetched_url = urlmain
        response = requests.get(fetched_url, params=dict(p=i))
        if not response.ok:
            break

        tree = html.fromstring(response.text)

        for a in tree.xpath(xpath):
            page_url = urljoin(fetched_url,a.attrib['href'])
            urls_file.write(page_url+'\n')
