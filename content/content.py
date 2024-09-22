import json

import dateutil.parser
import requests
import requests_cache
from lxml import html

requests_cache.install_cache('.cache')


def get_page(url):
    response = requests.get(url)
    return response.text


def get_tree_xpath(url):
    tree = html.fromstring(get_page(url))
    return tree.xpath


def get_data(url):
    ld_json = get_tree_xpath(url)('//script[@type=\'application/ld+json\']')[0].text
    return json.loads(ld_json)


def get_date(url):
    data = get_data(url)
    return dateutil.parser.parse(data['datePublished'])


def get_episode_title(url):
    data = get_data(url)
    return data['headline']


def get_formatted_date(url):
    return get_date(url).strftime('%Y-%m-%d')


def get_playlist_title(url):
    return 'Very Good Trip \r\n' + get_formatted_date(url) + '\r\n' + episode_title


def get_article(url):
    xpath = '//article[@class=\'content-body\']'
    return get_tree_xpath(url)(xpath)[0].text_content()
