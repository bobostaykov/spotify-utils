# spotify-utils

A Python GUI program with Spotify utilities. Currently, the following features are available:

- Shuffle a playlist (with duplicates of a track separated, if there are any)
- Convert playlist to MP3 files (_for this you need [FFmpeg](https://ffmpeg.org/download.html) installed_)
- Get the intersection or difference of two playlists

Following values must be set as environment variables or in a `.env` file (get them from
the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)):

- SPOTIFY_CLIENT_ID
- SPOTIFY_CLIENT_SECRET
- SPOTIFY_REDIRECT_URI

_Note: If the GUI does not work for you on Mac, you can try running the script with `pythonw` in a Conda environment._
