# spotify-shuffler

A script that shuffles a Spotify playlist and then reorders it, so that tracks that occur more than once are not close to each other.

In order for it to work, following values must be set as environment variables (get them from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications/72494217f3bc4159967e32905d3f9306)):
- SPOTIPY_CLIENT_ID
- SPOTIPY_CLIENT_SECRET
- SPOTIPY_REDIRECT_URI
