from collections import namedtuple

import requests
import requests_cache
import spotipy
from lxml import html

sp = spotipy.Spotify(requests_session=False)

xpath1 = '//*[@id="content"]/div[3]/div[2]/div/div/div[1]/article/h3'
xpath2 = '//*[@id="content"]/div[3]/div[2]/div/div/div[1]/article/ul/li'
title_xpath = '//*[@id="content"]/div[3]/div[1]/div/div[2]/div[2]/h1'
date_xpath = '//*[@id="content"]/div[3]/div[1]/div/div[1]/p[1]'


def getpageepisode(urlepisode):
    response = requests.get(urlepisode)
    return response.text


def normalise(input):
    if input is None: return None
    input = input.strip()

    input = input.replace('«','"')
    input = input.replace('»','"')
    input = input.replace('’','\'')

    return input.strip()

requests_cache.install_cache('.cache')


TrackInfo = namedtuple('TrackInfo',field_names=['date','raw','episode_title','author','album','title'])


def treat_url(url):
    tree = html.fromstring(getpageepisode(url))

    episode_title = str(tree.xpath(title_xpath)[0].text_content()).strip()
    date = str(tree.xpath(date_xpath)[0].text_content())

    list_tracks = []

    def treat_to_spotify(track_info):
        album = track_info.album
        author = track_info.author
        title = track_info.title
        # first, naive track searches
        qs = (
            'album:%s artist:%s track:%s' % (album, author, title),
            'artist:%s track:%s' % (author, title),
            '%s %s %s' % (album, author, title),
            '%s %s' % (title, author),
            '%s %s' % (title, author.replace('and', '&')),
            '%s %s' % (title, author.replace('&', 'and')),
            ('%s %s' % (title, author)).encode('ascii', errors='ignore')
        )

        for q in qs:
            search_tracks = sp.search(q=q)['tracks']
            if search_tracks['total'] == 1:
                # yay
                spotify_track = search_tracks['items'][0]
                return spotify_track['uri']

        return ''

    def treat_elem(element):
        elements_author = element.xpath('strong')
        elements_title = element.xpath('text()')
        raw = element.text_content().strip()
        if raw == '':
            return
        if len(elements_author) == 1:
            author = strip2(element.xpath('strong')[0].text)
        else:
            author = None
        if len(elements_title) == 1:
            title = normalize(str(element.xpath('text()')[0]))
            if 'extrait de l\'album' in title:
                spl = title.split('extrait de l\'album')
                album = spl[1]
                title = spl[0]
            elif 'album' in title:
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

        author = author.strip()
        album = strip2(album.strip())
        title = strip2(title.strip())

        track_info = TrackInfo(date=date, episode_title=episode_title, raw=raw, author=author, album=album, title=title)
        list_tracks.append(track_info)

    for h3 in tree.xpath(xpath1):
        treat_elem(h3)
    for li in tree.xpath(xpath2):
        treat_elem(li)

    for track_info in list_tracks:
        treat_to_spotify(track_info)

    pass
