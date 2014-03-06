import os
import cPickle as pkl
from collections import namedtuple

import requests
from bs4 import BeautifulSoup


Song = namedtuple('Song', ['title', 'artist', 'album', 'length'])


class Playlist(object):
    def __init__(self, title, url):
        self.title = title
        self.file_name = title.lower().replace(' ', '-') + '.pkl'
        self.url = url

        if os.path.isfile(self.file_name):
            self.load_from_pickle()
        else:
            self.songs = []

    def load_from_pickle(self):
        with open(self.file_name, 'rb') as in_file:
            self.songs = pkl.load(in_file)

    def download_data(self):
        url = self.url
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text)


        for song_elem in (soup.find(class_='songs')
                              .find_all(class_='media-body')):
            title = song_elem.h4.text
            ps = song_elem.find_all('p')
            artist, album = ps[0].text.split(u' \xb7 ')
            length = ps[1].text
            song = Song(title, artist, album, length)
            self.songs.append(song)

        with open(self.file_name, 'wb') as out:
            pkl.dump(self.songs, out)


ambient_bass = Playlist(
        'ambient bass',
        'http://www.playlister.io/items/playlist/1472493/ambient-bass/#')
beats = Playlist(
        'Blissed-Out Beats',
        'http://www.playlister.io/items/playlist/1682151/')
liquid = Playlist(
        'Liquid Dubstep',
        'http://www.playlister.io/items/playlist/1404323/')

liquid.download_data()