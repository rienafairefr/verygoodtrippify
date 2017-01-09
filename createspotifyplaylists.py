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



import requests_cache

requests_cache.install_cache('.cachespotify')

import spotipy
sp = spotipy.Spotify(requests_session=False)


with open('playlist_data_spotify.csv', mode='w', encoding='utf-8', newline='') as playlist_data_spotify_file,\
        open('playlist_data.csv', encoding='utf-8', mode='r') as playlist_data_file:
    datareader = csv.reader(playlist_data_file, delimiter=';')
    datawriter = csv.writer(playlist_data_spotify_file, delimiter=';')
    playlist_data_file.readline()
    datawriter.writerow(['date','episode','spotify_track_id'])
    for playlist_data_line in playlist_data_file.readlines():
        date, episode_title, raw, author, album, title = playlist_data_line.split(';')



        # first, naive track search
        q = 'album:%s artist:%s track:%s'%(album,author,title)
        search_tracks = sp.search(q=q)['tracks']
        if search_tracks['total']==1:
            #yay
            spotify_track = search_tracks['items'][0]
            spotify_track_id = spotify_track['uri']
        else:
            spotify_track_id = None

        spotify_track = [date, episode_title, spotify_track_id]
        datawriter.writerow(spotify_track)

