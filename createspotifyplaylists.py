import csv
import json
import string
from collections import namedtuple
from itertools import groupby
from urllib.parse import urljoin, urlencode, quote

from configargparse import ArgumentParser
from dotenv import load_dotenv, find_dotenv
import requests
from lxml import html
from xml.etree import ElementTree as ET
import pandas




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

playlist_data_filepath = 'playlist_data1.csv.txt'
playlist_data_spotify_filepath = 'playlist_data_spotify.csv'


playlist_data_spotify=[]

with open(playlist_data_spotify_filepath, mode='w', encoding='utf-8', newline='') as playlist_data_spotify_file,\
        open(playlist_data_filepath, encoding='cp850', mode='r') as playlist_data_file:
    datareader = csv.reader(playlist_data_file, delimiter='\t')
    playlist_data_file.readline()

    def getkey(line):
        return line[0]+' '+line[1]

    grouped_lines = groupby(datareader, getkey)
    for k1, playlist_data_lines_group in grouped_lines:

        from prettytable import PrettyTable

        x = PrettyTable(field_names=['author','title','album','spotify uri'])
        spotify_tracks = []
        for playlist_data_line in playlist_data_lines_group:
            date, episode_title, author, album, title = map(lambda x:x.strip(),playlist_data_line)
            if album == '(single)':
                album = ''

            def treat():
                # first, naive track searches
                qs = (
                    'album:%s artist:%s track:%s' % (album, author, title),
                    'artist:%s track:%s' % (author, title),
                    '%s %s %s' % (album, author, title),
                    '%s %s' % (title, author),
                    '%s %s' % (title, author.replace('and','&')),
                    '%s %s' % (title, author.replace('&', 'and')),
                   ('%s %s' % (title, author)).encode('ascii',errors='ignore')
                )

                for q in qs:
                    search_tracks = sp.search(q=q)['tracks']
                    if search_tracks['total']==1:
                        #yay
                        spotify_track = search_tracks['items'][0]
                        return spotify_track['uri']

                return ''


            spotify_track_id = treat()

            spotify_track = [author, title, album, spotify_track_id]
            x.add_row(spotify_track)
            playlist_data_spotify.append(spotify_track)
            spotify_tracks.append(spotify_track)
        print(x)
        pass

df = pandas.DataFrame(data=playlist_data_spotify, columns=['date','episode','spotify_track_id'])

with open("playlist_data_spotify.html", "w") as playlist_data_spotify_html:
    playlist_data_spotify_html.write(df.to_html())

with open("playlist_data_spotify.csv", "w") as playlist_data_spotify_csv:
    playlist_data_spotify_html.write(df.to_csv())
