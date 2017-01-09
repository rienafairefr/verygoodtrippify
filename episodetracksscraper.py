import csv
import json
from collections import namedtuple
from urllib.parse import urljoin, urlencode, quote

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


def strip2(input):
    if input is None: return None
    input = input.strip()
    # has enclosing double quotes
    input = input.rstrip('«')
    input = input.lstrip('»')

    # has enclosing dashes
    input = input.rstrip('-')
    input = input.lstrip('-')

    return input.strip()

import requests_cache

requests_cache.install_cache('.cache')

import spotipy
sp = spotipy.Spotify(requests_session=False)


def getpageepisode(urlepisode):
    response = requests.get(urlepisode)
    return response.text

with open('playlist_data.csv', 'w', encoding='utf-8', newline='') as playlist_data_file,\
        open('urls', 'r') as urls_file:
    datawriter = csv.writer(playlist_data_file, delimiter=';'
                            , quoting=csv.QUOTE_MINIMAL)
    datawriter.writerow(['date','episode_title','raw','author','album','title','spotify_uri'])
    for urlline in urls_file.readlines():
        url = urlline.rstrip('\n')
        print('treating '+url)

        tree = html.fromstring(getpageepisode(url))

        episode_title = str(tree.xpath(title_xpath)[0].text_content()).strip()
        date = str(tree.xpath(date_xpath)[0].text_content())

        list_tracks = []
        list_spotify_tracks = []
        def treat_elem(element):
            elements_author = element.xpath('strong')
            elements_title = element.xpath('text()')
            raw = element.text_content().strip()
            if raw == '':
                return
            if len(elements_author)==1 :
                author = strip2(element.xpath('strong')[0].text)
            else:
                author = None
            if len(elements_title) == 1:
                title = str(element.xpath('text()')[0]).strip()
                if 'album' in title:
                    spl = title.split('album')
                    album = spl[1]
                    title = spl[0]
                elif 'compilation' in title:
                    spl = title.split('compilation')
                    album = spl[1]
                    title = spl[0]
                elif 'EP' in title:
                    spl = title.split('EP')
                    album = spl[1]
                    title = spl[0]
                else:
                    album = None
            else:
                title = None
                album = None

            if 'single' in raw.lower() and album is None:
                album = '(single)'

            author = strip2(author)
            album = strip2(album)
            title = strip2(title)

            # first, naive track search
            q = 'album:%s artist:%s track:%s'%(album,author,title)
            search_tracks = sp.search(q=q)['tracks']
            if search_tracks['total']==1:
                #yay
                spotify_track = search_tracks['items'][0]
                list_spotify_tracks.append(spotify_track)
                spotify_track_id = spotify_track['uri']
            else:
                spotify_track_id = None

            track = [date, episode_title, raw, author, album, title, spotify_track_id]
            list_tracks.append(track)
            datawriter.writerow(track)


        for h3 in tree.xpath(xpath1):
            treat_elem(h3)
        for li in tree.xpath(xpath2):
            treat_elem(li)

        pass