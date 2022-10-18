# spotify-api-to-db
Collects data from spotify's api and stores it in a postgresql database

Utilizes spotify's scope "user-recently-played" which returns 50 most recently played tracks.

The script then checks if there have been any new songs played by comparing the played_at
times of returned tracks and the stored tracks in database.<br />
    EXAMPLE:<br />
        "2022-10-18T08:12:57.973Z" is the most recent played_at time in database<br />
        "2022-10-18T09:12:57.973Z" is the played_at time for a track returned by spotify<br />
        It was played 1 hour after the most recent track in database.<br />
        Therefore, it will be added to database and so on until we get to a track that is equal to the former played_at time (meaning it is the same track).<br />

Database consists of 4 tables named 'tracks', 'recently_played', 'albums', and 'artists'<br />

    tracks and recently_played have columns:
        id            - int4 (default)
        created_at    - timestamp (default)
        replayed      - int4         # EXCLUSIVE TO 'Tracks' TABLE
        name          - varchar(255)
        artists       - varchar(255)
        album         - varchar(255)
        played_at     - varchar(255) # EXCLUSIVE TO 'recently_played' TABLE
        popularity    - int4
        duration_ms   - int8
        explicit      - varchar(255)
        track_id      - varchar(255)
        disc_number   - int4
        external_ids  - varchar(500)
        external_urls - varchar(500)
        href          - varchar(255)
        is_local      - varchar(255)
        preview_url   - varchar(500)
        track_number  - int4
        type          - varchar(255)
        uri           - varchar(255)
        artist_ids    - varchar(500)
        album_id      - varchar(500)

    albums has columns:
        id                       - int4 (default)
        created_at               - timestamp (default)
        name                     - varchar(255)
        artist_names             - varchar(255)
        total_tracks             - int4
        release_date             - varchar(255)
        release_date_precision   - varchar(255)
        album_type               - varchar(255)
        artist_ids               - varchar(255)
        external_urls            - varchar(500)
        href                     - varchar(255)
        album_id                 - varchar(255)
        images                   - varchar(1500)
        type                     - varchar(255)
        uri                      - varchar(255)
    
    artists has columns:
        id            - int4 (default)
        created_at    - timestamp (default)
        name          - varchar(255)
        replayed      - int4
        href          - varchar(255)
        artist_id     - varchar(255)
        external_urls - varchar(255)
        type          - varchar(255)
        uri           - varchar(255)

This script has been formatted in such a way that it can be conviently deployed to AWS Lambda after importing the two external dependencies (spotipy and psycopg2)<br />
    AWS Docs: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html