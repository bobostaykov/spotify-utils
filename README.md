# spotify-utils

A script with Spotify utilities. Currently, the following features are available:

- Shuffle a playlist (with duplicates of a track separated, if there are any)
- Convert playlist to MP3 files (for this you need [FFmpeg](https://ffmpeg.org/download.html) installed)
- Get the intersection or difference of two playlists

Following values must be set as environment variables or in a `.env` file (get them from
the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)):

- SPOTIFY_CLIENT_ID
- SPOTIFY_CLIENT_SECRET
- SPOTIFY_REDIRECT_URI

_Note: For the GUI to work on Mac, the script may have to be run with `pythonw` in a Conda environment._