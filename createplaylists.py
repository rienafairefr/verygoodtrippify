import csv
import json
from collections import namedtuple

from configargparse import ArgumentParser
from dotenv import load_dotenv, find_dotenv
import requests
from lxml import html
from xml.etree import ElementTree as ET
load_dotenv(find_dotenv())

parser = ArgumentParser()
parser.add_argument('-c','--cid',help='Spotify API key',env_var='SPOTIFY_CLIENT_ID')
parser.add_argument('-s','--cs', help='Spotify API key',env_var='SPOTIFY_CLIENT_SECRET')

arguments = parser.parse_args()
spotify_client_id = arguments.cid
spotify_client_secret = arguments.cs

xpath1 = '//*[@id="content"]/div[3]/div[2]/div/div/div[1]/article/h3'
xpath2 = '//*[@id="content"]/div[3]/div[2]/div/div/div[1]/article/ul/li'
title_xpath ='//*[@id="content"]/div[3]/div[1]/div/div[2]/div[2]/h1'
date_xpath ='//*[@id="content"]/div[3]/div[1]/div/div[1]/p[1]'

def content(tag):
    return str(tag.text) + ''.join(str(ET.tostring(e)) for e in tag)

try:
    with open('playlist_data','r') as playlist_data_file:
        playlist_data = json.loads(playlist_data_file)
except:
    playlist_data = []

#track=namedtuple('track',field_names=['date','episode_title','author','title'])

with open('playlist_data', 'w', encoding='utf-8') as playlist_data_file,\
        open('urls', 'r') as urls_file:
    datawriter = csv.writer(playlist_data_file, delimiter=';'
                            , quoting=csv.QUOTE_MINIMAL)
    for urlline in urls_file.readlines():
        url = urlline.rstrip('\n')
        print('treating '+url)

        response = requests.get(url)
        tree = html.fromstring(response.text)

        episode_title = str(tree.xpath(title_xpath)[0].text_content()).strip()
        date = str(tree.xpath(date_xpath)[0].text_content())


        def treat_elem(element):
            elements_author = element.xpath('strong')
            elements_title = element.xpath('text()')
            raw = element.text_content().strip()
            if len(elements_author)==1 :
                author = element.xpath('strong')[0].text.strip()
            else:
                author = None
            if len(elements_title) == 1:
                title = str(element.xpath('text()')[0]).strip()
                if 'album' in title:
                    spl = title.split('album')
                    album = spl[1]
                    title = spl[0]
                else:
                    album = None
            else:
                title = None
                album = None

            datawriter.writerow([date, episode_title, raw, author, album, title])


        for h3 in tree.xpath(xpath1):
            treat_elem(h3)
        for li in tree.xpath(xpath2):
            treat_elem(li)







    exit(-1)




