import os
import spotipy #1 pip
from spotipy.oauth2 import SpotifyOAuth #1 pip
import psycopg2 #2 pip

os.environ['SPOTIPY_CLIENT_ID']='Insert spotify client id here'
os.environ['SPOTIPY_CLIENT_SECRET']='Insert spotify client secret here'
os.environ['SPOTIPY_REDIRECT_URI']='http://localhost:8888/callback'

# Function for retrieving data from spotify's api and updating database with new information
#   Takes two unused parameters for AWS Lambda compatibility purposes
def spotify_get(foo, bar):
    scope = "user-read-recently-played"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    DB_HOST = 'Insert database host here'
    DB_NAME = 'Insert database name here'
    DB_USER = 'Insert database user here'
    DB_PASS = 'Insert database password here'

    sing_quote = "'"
    doub_quote = "''"


    # send request to spotify api for 50 most recently played tracks
    results = sp.current_user_recently_played()
    # connect to postgresql database
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()

    # checks if the recently played track has already been logged
    #   by comparing the playtimes of most recent track in database
    #   and that of the tracks returned by spotify's api
    # else adds track to all_tracks
    cur.execute("SELECT played_at \
FROM recently_played \
ORDER BY played_at DESC \
LIMIT 1;")

    playedattimes = cur.fetchall()
    try:
        previous_last_song_time = playedattimes[0][0]
    except:
        previous_last_song_time = 0
    temp_dic = {}
    temp_dic['items'] = []
    print("# of tracks: ", len(results['items']))
    for i in range(len(results['items'])):
        if(results['items'][i]['played_at'] != previous_last_song_time):
            temp_dic['items'].insert(0, results['items'][i])
            print("Added song: ", results['items'][i]['track']['name'])
        else:
            break
    print(f"Added {len(temp_dic['items'])} songs to temp_dic")
    if (len(temp_dic['items']) == 0):
        return ("No new tracks")

    # most recently played song is last item in temp_dic['items'] so it gets added to end of database table
    for i in (temp_dic['items']):

        # update recently_played, tracks, albums, and artists tables
        # must double up the single quotes to insert into db table
        track_name = i['track']['name'].replace("'", "''")
        track_artist_names = f"'{str([j['name'] for j in i['track']['artists']]).replace(sing_quote, doub_quote)}'"
        track_album_name = i['track']['album']['name'].replace("'", "''")
        played_at = i['played_at']
        track_popularity = i['track']['popularity']
        track_duration_ms = i['track']['duration_ms']
        track_explicit = i['track']['explicit']
        track_id = i['track']['id'].replace("'", "''")
        track_disc_number = i['track']['disc_number']
        track_external_ids = str(i['track']['external_ids']).replace("'", "''")
        track_external_urls = str(i['track']['external_urls']).replace("'", "''")
        track_href = i['track']['href'].replace("'", "''")
        track_is_local = i['track']['is_local']
        track_preview_url = i['track']['preview_url'].replace("'", "''")
        track_number = i['track']['track_number']
        track_type = i['track']['type']
        track_uri = i['track']['uri'].replace("'", "''")
        track_artist_ids = f"'{str([j['id'] for j in i['track']['artists']]).replace(sing_quote, doub_quote)}'"
        track_album_id = i['track']['album']['id'].replace("'", "''")
        
        cur.execute(f"INSERT INTO recently_played (name, artists, album, played_at, popularity,\
 duration_ms, explicit, track_id, disc_number, external_ids, external_urls, href, is_local,\
 preview_url, track_number, type, uri, artist_ids, album_id)\
 VALUES ('{track_name}', {track_artist_names}, '{track_album_name}', '{played_at}',\
 {track_popularity}, {track_duration_ms}, '{track_explicit}', '{track_id}',\
 '{track_disc_number}', '{track_external_ids}', '{track_external_urls}',\
 '{track_href}', '{track_is_local}', '{track_preview_url}', {track_number},\
 '{track_type}', '{track_uri}', {track_artist_ids}, '{track_album_id}');")

        cur.execute(f"INSERT INTO tracks (name, artists, album, popularity,\
 duration_ms, explicit, track_id, disc_number, external_ids, external_urls, href, is_local,\
 preview_url, track_number, type, uri, artist_ids, album_id)\
 SELECT '{track_name}', {track_artist_names}, '{track_album_name}',\
 {track_popularity}, {track_duration_ms}, '{track_explicit}', '{track_id}',\
 '{track_disc_number}', '{track_external_ids}', '{track_external_urls}',\
 '{track_href}', '{track_is_local}', '{track_preview_url}', {track_number},\
 '{track_type}', '{track_uri}', {track_artist_ids}, '{track_album_id}'\
 WHERE NOT EXISTS (SELECT track_id FROM tracks WHERE track_id = '{track_id}');")

        cur.execute(f"SELECT exists (SELECT 1 FROM tracks WHERE track_id = '{track_id}' AND replayed is null LIMIT 1);")
        id_exists = cur.fetchone()[0]
        if (id_exists == True):
            cur.execute(f"UPDATE tracks SET replayed = 1 WHERE track_id = '{track_id}'")
        else:
            cur.execute(f"UPDATE tracks SET replayed = replayed + 1 WHERE track_id = '{track_id}'")


        album_artist_names = f"'{str([j['name'] for j in i['track']['album']['artists']]).replace(sing_quote, doub_quote)}'"
        album_total_tracks = i['track']['album']['total_tracks']
        album_release_date = i['track']['album']['release_date']
        album_release_date_precision = i['track']['album']['release_date_precision']
        album_album_type = i['track']['album']['album_type']
        album_artist_ids = f"'{str([j['id'] for j in i['track']['album']['artists']]).replace(sing_quote, doub_quote)}'"
        album_external_urls = str(i['track']['album']['external_urls']).replace("'", "''")
        album_href = i['track']['album']['href'].replace("'", "''")
        album_id = i['track']['album']['id'].replace("'", "''")
        album_images = str(i['track']['album']['images']).replace("'", "''")
        album_type = i['track']['album']['type']
        album_uri = i['track']['album']['uri'].replace("'", "''")

        cur.execute(f"INSERT INTO albums (name, artist_names, total_tracks, release_date,\
 release_date_precision, album_type, artist_ids, external_urls, href,\
 album_id, images, type, uri)\
 SELECT '{track_album_name}', {album_artist_names}, {album_total_tracks},\
 '{album_release_date}', '{album_release_date_precision}', '{album_album_type}',\
 {album_artist_ids}, '{album_external_urls}', '{album_href}', '{album_id}',\
 '{album_images}', '{album_type}', '{album_uri}'\
 WHERE NOT EXISTS (SELECT album_id FROM albums WHERE album_id = '{i['track']['album']['id']}');")


        for j in (i['track']['artists']):
            artist_name = j['name'].replace("'", "''")
            artist_href = j['href'].replace("'", "''")
            artist_id = j['id'].replace("'", "''")
            artist_external_url = str(j['external_urls']).replace("'", "''")
            artist_uri = j['uri'].replace("'", "''")

            cur.execute(f"INSERT INTO artists (name, href, artist_id, external_urls, uri)\
 SELECT '{artist_name}', '{artist_href}', '{artist_id}', '{artist_external_url}', '{artist_uri}'\
 WHERE NOT EXISTS (SELECT artist_id FROM artists WHERE artist_id = '{artist_id}');")

            cur.execute(f"SELECT exists (SELECT 1 FROM artists WHERE artist_id = '{artist_id}' AND replayed is null LIMIT 1);")
            id_exists = cur.fetchone()[0]
            if (id_exists == True):
                cur.execute(f"UPDATE artists SET replayed = 1 WHERE artist_id = '{artist_id}'")
            else:
                cur.execute(f"UPDATE artists SET replayed = replayed + 1 WHERE artist_id = '{artist_id}'")


    # commit all changes to database and close connection
    conn.commit()
    cur.close
    conn.close()
    print("Successfully called spotify_get")
    return ("Done")