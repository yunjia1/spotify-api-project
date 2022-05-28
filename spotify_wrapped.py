import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import time
import datetime
import gspread
#from wrapped_functions import get_artist_ids, get_track_ids, genres_to_artists, insert_to_gsheet, insert_reccs_to_gsheet
from dotenv import load_dotenv
import os
import wrapped_functions

load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SCOPE = "user-top-read"

#Globals
genres = set()

# Authorize
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                              client_secret=SPOTIPY_CLIENT_SECRET,
                              redirect_uri=SPOTIPY_REDIRECT_URI,
                              scope=SCOPE))

# Run script to insert into sheet
time_ranges = ['short_term', 'medium_term', 'long_term']
for time_period in time_ranges:
    top_tracks = sp.current_user_top_tracks(limit=20,
                                            offset=0,
                                            time_range=time_period)
    top_artists = sp.current_user_top_artists(limit=20,
                                              offset=0,
                                              time_range=time_period)
    track_ids = wrapped_functions.get_track_ids(top_tracks)
    artist_ids = wrapped_functions.get_artist_ids(top_artists)
    genres = wrapped_functions.insert_to_gsheet(track_ids, artist_ids,
                                                time_period, genres)
genres = list(genres)
genres_to_artist = {genre: [] for genre in genres}
wrapped_functions.genres_to_artists(artist_ids, genres, genres_to_artist)

genre_numbers = ['genre1', 'genre2', 'genre3', 'genre4']
length = len(genres)
if length > 4:
    length = 4
for i in range(0, length):
    wrapped_functions.insert_reccs_to_gsheet(i, genre_numbers[i], genres,
                                             genres_to_artist, artist_ids)
