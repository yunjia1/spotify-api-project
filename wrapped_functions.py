import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import time
import datetime
import gspread
from dotenv import load_dotenv
import os

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SCOPE = "user-top-read"

# Authorize
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                              client_secret=SPOTIPY_CLIENT_SECRET,
                              redirect_uri=SPOTIPY_REDIRECT_URI,
                              scope=SCOPE))


#####################################TOP SONG FUNCTIONS#####################################
def get_track_ids(time_frame):
    track_ids = []
    for song in time_frame['items']:
        track_ids.append(song['id'])
    return track_ids


def get_track_features(id):
    meta = sp.track(id)
    # meta
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    spotify_url = meta['external_urls']['spotify']
    album_cover = meta['album']['images'][0]['url']
    track_info = [name, album, artist, spotify_url, album_cover]
    return track_info


#####################################TOP ARTIST FUNCTIONS#####################################


def get_artist_ids(time_frame):
    track_ids = []
    for artist in time_frame['items']:
        track_ids.append(artist['id'])
    return track_ids


#dict of lists
def get_artist_features(id, genres):
    meta = sp.artist(id)
    # meta
    name = meta['name']
    genre = meta['genres'][0]
    for genre in meta['genres']:
        if genre in sp.recommendation_genre_seeds()['genres']:
            genres.add(genre)
    spotify_url = meta['external_urls']['spotify']
    artist_cover = meta['images'][0]['url']
    artist_info = [name, genre, spotify_url, artist_cover]
    return artist_info, genres


def insert_to_gsheet(track_ids, artist_ids, time_period, genres):
    # loop over track ids
    tracks = []
    for i in range(len(track_ids)):
        time.sleep(.5)
        track = get_track_features(track_ids[i])
        tracks.append(track)

    # loop over track ids
    artists = []
    for i in range(len(artist_ids)):
        time.sleep(.5)
        artist, genres = get_artist_features(artist_ids[i], genres)
        artists.append(artist)
    gc = gspread.service_account(
        filename='spotify-project-351223-6241061dba93.json')
    sh = gc.open("Spotify Wrapped Songs")

    # create dataset
    df = pd.DataFrame(
        tracks,
        columns=['name', 'album', 'artist', 'spotify_url', 'album_cover'])
    # insert into google sheet
    worksheet = sh.worksheet(f'{time_period + "_songs"}')
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print('Done')

    # create dataset
    df_artist = pd.DataFrame(
        artists, columns=['name', 'genre', 'spotify_url', 'artist_cover'])
    # insert into google sheet
    worksheet = sh.worksheet(f'{time_period + "_artists"}')
    worksheet.update([df_artist.columns.values.tolist()] +
                     df_artist.values.tolist())
    print('Done')
    return genres 
    #####################reccomendation functions######################


    #create dict of lists
def genres_to_artists(artist_ids, genres, genres_to_artist):
    for id in artist_ids:
        meta = sp.artist(id)
        for genre in meta['genres']:
            if genre in genres:
                genres_to_artist[genre].append(id)


#can only pass in a max of 5 seeds
#create suggested playlist based on genre
def insert_reccs_to_gsheet(index, genre_number, genres, genres_to_artist, artist_ids):
    genre = genres[index]
    artist_len = len(genres_to_artist[genre])
    if (artist_len > 2):
        artist_len = 2
    lim = 10
    recommendations = sp.recommendations(
        seed_artists=artist_ids[0:artist_len], limit=lim)
    tracks = []
    for i in range(0, lim):
        iD = recommendations['tracks'][i]['id']
        track = get_track_features(iD)
        tracks.append(track)
    df = pd.DataFrame(
        tracks,
        columns=['name', 'album', 'artist', 'spotify_url', 'album_cover'])
    # insert into google sheet
    gc = gspread.service_account(
        filename='spotify-project-351223-6241061dba93.json')
    sh = gc.open("Spotify Wrapped Songs")
    worksheet = sh.worksheet(f'{genre_number}')
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print('Done')