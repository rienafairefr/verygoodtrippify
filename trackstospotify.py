import json
import random

import dateutil.parser
from configargparse import ArgumentParser
from collections import namedtuple

import requests
import requests_cache
import spotipy
from dotenv import find_dotenv
from dotenv import load_dotenv
from lxml import html, etree
from spotipy import util
from pyld import jsonld

xpath1 = '//article[@class=\'content-body\']/h3'
xpath2 = '//article[@class=\'content-body\']/ul/li'
xpath3 = '//*[@id="content"]/div[4]/div[2]/div/div/div[1]/article/p[3]'
title_xpath = '//*[@class=\'cover-portrait-actions-title\']'
date_xpath = '//*[@class=\'cover-emission-period\']'


colon_not_in_quote = '(:)(?=(?:[^\"]|\"[^\"]*\")*$)'


load_dotenv(find_dotenv())

parser = ArgumentParser()
parser.add_argument('-c','--cid',help='Spotify API client id', env_var='SPOTIFY_CLIENT_ID')
parser.add_argument('-s','--cs', help='Spotify API client secret key', env_var='SPOTIFY_CLIENT_SECRET')
parser.add_argument('-r','--cr', help='Spotify API redirect', env_var='SPOTIFY_REDIRECT_URI')
parser.add_argument('-u','--user', help='User',env_var='SPOTIFY_USERNAME')

arguments = parser.parse_args()
spotify_client_id = arguments.cid
spotify_client_secret = arguments.cs
spotify_user = arguments.user
spotify_redirect_uri = arguments.cr
spotify_username = arguments.user

scope = 'playlist-modify-public'

token = util.prompt_for_user_token(username=spotify_username,client_id=spotify_client_id,client_secret=spotify_client_secret,
                           redirect_uri=spotify_redirect_uri,scope=scope)
if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", spotify_username)
    exit(-1)

spotify_user_id = sp.me()['id']


def normalise(input):
    if input is None: return None
    input = input.strip()

    input = input.replace('«','"')
    input = input.replace('»','"')
    input = input.replace('’','\'')

    return input.strip()


def strip3(input):
    if input is None: return None
    input = input.strip()

    input = input.replace('"','')
    input = input.replace('"','')

    return input.strip()

requests_cache.install_cache('.cache')


TrackInfo = namedtuple('TrackInfo',field_names=['date','raw','episode_title','author','album','title'])
TrackwithSpotifyInfo = namedtuple('TrackwithSpotifyInfo',field_names=['track_info','spotify_uri'])


def treat_url(url):
    tree = html.fromstring(getpageepisode(url))

    ld_json = tree.xpath('//script[@type=\'application/ld+json\']')[0].text

    data = json.loads(ld_json)

    episode_title = data['headline']
    date = dateutil.parser.parse(data['datePublished'])
    formatted_date = date.strftime('%Y-%m-%d')

    list_tracks = []
    #
    # def treat_to_spotify(track_info):
    #     requests_cache.install_cache('.spotifycache')
    #     album = track_info.album
    #     author = track_info.author
    #     title = track_info.title
    #     # first, naive track searches
    #     qs = (
    #         'album:%s artist:%s track:%s' % (album, author, title),
    #         'artist:%s track:%s' % (author, title),
    #         '%s %s %s' % (album, author, title),
    #         '%s %s' % (title, author),
    #         '%s %s' % (title, author.replace('and', '&')),
    #         '%s %s' % (title, author.replace('&', 'and')),
    #         ('%s %s' % (title, author)).encode('ascii', errors='ignore')
    #     )
    #
    #     for q in qs:
    #         search_tracks = sp.search(q=q)['tracks']
    #         if search_tracks['total'] == 1:
    #             # yay
    #             spotify_track = search_tracks['items'][0]
    #             return spotify_track['uri']
    #
    #     return ''
    #
    def treat_elem(element):
    #     elements_author = element.xpath('strong')
    #     elements_title = element.xpath('text()')
        raw = element.text_content().strip()
    #     if raw == '':
    #         return
    #     if len(elements_author) == 1:
    #         author = element.xpath('strong')[0].text.strip()
    #     else:
    #         author = None
    #     if len(elements_title) == 1:
    #         title = normalise(str(element.xpath('text()')[0]))
    #         title = title.lstrip(' ')
    #         title = title.lstrip(':')
    #         if 'extrait de l\'album' in title:
    #             spl = title.split('extrait de l\'album')
    #             album = spl[1]
    #             title = spl[0]
    #         elif 'album' in title:
    #             spl = title.split('album')
    #             album = spl[1]
    #             title = spl[0]
    #         elif 'compilation' in title:
    #             spl = title.split('compilation')
    #             album = spl[1]
    #             title = spl[0]
    #         elif 'EP' in title:
    #             spl = title.split('EP')
    #             album = spl[1]
    #             title = spl[0]
    #         else:
    #             album = None
    #     else:
    #         title = None
    #         album = None
    #
    #     if 'single' in raw.lower() and album is None:
    #         album = '(single)'
    #
    #     author = strip3(author)
    #     album = strip3(album)
    #     title = strip3(title)
    #
        list_tracks.append(raw)

    article = tree.xpath('//article')[0]

    for elem in tree.xpath(xpath3):
        treat_elem(elem)

    #
    # list_spotify_track_infos = []
    # for track_info in list_tracks:
    #     list_spotify_track_infos.append(TrackwithSpotifyInfo(track_info=track_info,spotify_uri=treat_to_spotify(track_info)))


    playlist_title = 'Very Good Trip \r\n' + formatted_date +'\r\n'+episode_title

    playlists = sp.user_playlists(spotify_user_id)
    for playlist_data in playlists['items']:
        if playlist_data['name'] == playlist_title:
            break
    else:
        playlist_data = sp.user_playlist_create(spotify_user_id,playlist_title)

    #uris = [spotify_track_info.spotify_uri for spotify_track_info in list_spotify_track_infos if spotify_track_info.spotify_uri!='']

    #addition = sp.user_playlist_replace_tracks(spotify_user_id,playlist_data['id'], uris)
    pass

if __name__== "__main__":
    url = random.choice(list(open('urls')))
    treat_url(url.strip())