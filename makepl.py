# source for code example (without user auth): https://github.com/spotipy-dev/spotipy
# to run: py data_upload.py from same directory


import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity 
import numpy as np
import re

###### SETTINGS

# Spotify API credentials (hide?)
CLIENT_ID = "2d78b09918524458b4fcc776b822673c"
CLIENT_SECRET = "10859191e6a34ac8afe7b7639a644d69"

# Initialize Spotipy client
sp = spotipy.Spotify(auth_manager=spotipy.SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

csv = pd.read_csv("tracklist.csv")

# Extracts the track URI from a Spotify share URL
def get_track_uri(url):
    match = re.search(r'track\/(\w+)', url)
    if match:
        track_id = match.group(1)
        track_uri = f"spotify:track:{track_id}"
        return track_uri
    else:
        raise ValueError("Invalid Spotify share URL")


# get track audio features for a given track
def get_track_audio_features(track_uri, sp):
    track_id = track_uri.split(':')[-1]
    track_features = sp.audio_features(tracks=[track_id])[0]
    track_row = (track_features['uri'], track_features['danceability'], track_features['energy'], track_features['key'], track_features['loudness'], track_features['mode'], track_features['speechiness'], track_features['acousticness'], track_features['instrumentalness'], track_features['liveness'], track_features['valence'], track_features['tempo'], track_features['duration_ms'], track_features['time_signature'])
    return track_row

# get track properties for a given track, for display
def get_track_properties(track_uri):
    track_properties = {} # {'name': x, 'artist': x}
    track_metadata = sp.track(track_uri)
    track_properties['name'] = track_metadata['name'] 
    track_properties['artist'] = track_metadata['artists'][0]['name']
    return track_properties

# takes in two vectors and calculates similarity

def calculate_cosine_similarity(input_vector, candidate_features):
    # print("before input vector")
    # print("shape in_pre: ",input_features.shape )
    # print("type in_pre: ",type(input_features))
    # input_vector = input_features
    # print("shape in_after: ",input_vector.shape )
    # print("data type in_after: ",type(input_vector))
    # print("before input vector")
    candidate_vector = candidate_features.squeeze()
    # print("shape candidate: ",candidate_vector.shape )
    # print("data type candidate: ",type(candidate_vector))
    out = cosine_similarity([input_vector, candidate_vector])[0][1]
    # print("shape out: ", out.shape )
    # print("value out: ", out)
    return out


# Gets similar tracks from BigQuery table using content-based filtering
def get_similar_track_uris(track_uri):
    
    candidates_df = csv

    # Generate input_track_fatures and save on df
    track_features = sp.audio_features(track_uri)[0]
    track_row = (track_features['uri'], track_features['danceability'], track_features['energy'], track_features['key'], track_features['loudness'], track_features['mode'], track_features['speechiness'], track_features['acousticness'], track_features['instrumentalness'], track_features['liveness'], track_features['valence'], track_features['tempo'], track_features['duration_ms'], track_features['time_signature'])
 
    input_track_df = pd.DataFrame([track_row], columns=['uri', 'danceability', 'energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo','duration_ms','time_signature'])

    # combine track features
    # print(input_track_df.head())
    # print(candidates_df.head())
    df = pd.concat([input_track_df, candidates_df])
    # print(df.head())

    # Calculates similarity

    features =['danceability', 'energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo','duration_ms','time_signature']

    input_track_features = df.loc[df['uri'] == track_uri, features]
    if input_track_features.empty:
        raise ValueError("Error in creating input feaure DF")
    else:
        input_track_features = input_track_features.iloc[0]


    df_filtered = df.loc[df['uri'] != track_uri, features].dropna()
    df['similarity'] = df_filtered.apply(lambda x: calculate_cosine_similarity(input_track_features, x), axis=1) #axis=1 for row

    similar_tracks = df.loc[df['uri'] != track_uri].sort_values(by='similarity', ascending=False).head(20)

    # Creates list of uris
    track_uris = similar_tracks['uri'].tolist()

    return track_uris



# display info
def display_similar_songs (track_uris):
    # extract metadata
    metadata = {}
    for uri in track_uris:
        metadata[uri] = get_track_properties(uri) #returns {'name': x, 'artist': x}

    # display output
    track_num = 1
    songs_out = []
    for uri, meta in metadata.items():
        current_uri = uri
        current_meta = meta
        songs_out.append(f"{current_meta['name']} by {current_meta['artist']}\n")
        track_num += 1
    return songs_out

# display info
def display_input_song (uri):
    # extract metadata
    meta = get_track_properties(uri) #returns {'name': x, 'artist': x}
    song_info = f"You entered this song: {meta['name']} by {meta['artist']} ({uri})"
    return song_info

'''
# Extract url and print input song
track_url = .strip() # remove leading and trailing spaces
track_uri = get_track_uri(track_url)

display_input_song (track_uri)


#Extract similar songs and display them
similar_track_uris = get_similar_track_uris(track_uri)
print("Here is your workout playlist!")
display_similar_songs (similar_track_uris)
print()
print("GOODBYE!")
print()
'''