from urllib.parse import urljoin

import requests
from lxml import html

urlmain = 'https://www.franceinter.fr/emissions/very-good-trip'

xpath = '//a[@class=\'rich-section-list-item-content-title\']/@href[\'href\']'

with open('urls','w') as urls_file:
    for i in range(1, 50):
        fetched_url = urlmain
        response = requests.get(fetched_url, params=dict(p=i))
        if not response.ok:
            print('response not ok from %s' % fetched_url)
            break

        tree = html.fromstring(response.text)

        for href in tree.xpath(xpath):
            page_url = urljoin(urlmain, href)
            print(page_url)
            urls_file.write(page_url+'\n')
