# -*- coding: utf-8 -*-
"""
Created on Thu Mar 06 01:12:10 2014

@author: Michael
"""

import os
import logging
import cPickle as pkl
from collections import namedtuple

import requests

from retry import retry


API_KEY = '14333ebf446ea0df4ab5cffc8e2cb0316080cd85'
PLAY_TOKEN = '663955208'


Song = namedtuple('Song', ['title', 'artist', 'album', 'length'])


def get(url, api_key=API_KEY, **kwargs):
    params = kwargs.get('params', {})
    params['api_key'] = api_key
    params['api_version'] = 3
    return requests.get(url, params=params)


def create_new_token():
    return get('http://8tracks.com/sets/new.json').json()['play_token']

class Playlist(object):
    def __init__(self, title, pid, play_token=PLAY_TOKEN):
        self.title = title
        self.file_name = title.lower().replace(' ', '-') + '.pkl'
        self.id = pid
        self.play_token = play_token
        
        if os.path.isfile(self.file_name):
            self.load_from_pickle()
        else:
            self.songs = []
            
    @retry(10)
    def get(self, url, api_key=API_KEY, **kwargs):
        params = kwargs.get('params', {})
        params['mix_id'] = self.id
        return get(url, params=params)

    def download_data(self):
        self.songs = [song for song in self.track_json_gen()]
        with open(self.file_name, 'wb') as out:
            #pkl.dump(self.songs, out)
            pkl.dump(self.get_songs_played(), out)
    
    def start_mix(self):
        url = 'http://8tracks.com/sets/%s/play.json' % self.play_token
        return self.get(url)
    
    def get_next_track(self):
        url = 'http://8tracks.com/sets/%s/next.json' % self.play_token
        return self.get(url)
        
    def track_json_gen(self):
        resp = self.start_mix()
        set_json = resp.json()['set']
        track_json = set_json['track']
        logging.info('Song 1 fetched.')
        yield track_json
        
        last_track = set_json['at_last_track']
        i = 2
        
        while not last_track:
            resp = self.get_next_track()
            set_json = resp.json()['set']
            track_json = set_json['track']
            last_track = set_json['at_last_track']

            logging.info('Song %d fetched.' % i)
            i += 1
            yield track_json

    def get_songs_played(self):
        url = 'http://8tracks.com/sets/%s/tracks_played.json' % self.play_token
        return self.get(url).json()

logging.basicConfig(
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    level=logging.INFO)
velvet = Playlist('Velvet Vocals', '1082597')
velvet.download_data()