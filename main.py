import spotipy
from spotipy.oauth2 import SpotifyOAuth

from constants import MY_SONGS_PLAYLIST_ID
from reorder import reorder_playlist_two_clones, reorder_playlist_three_clones
from util import shuffle


def main():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(scope='playlist-modify-private playlist-modify-public'))

    shuffle(sp, MY_SONGS_PLAYLIST_ID)
    print('Starting reordering process:')
    reorder_playlist_two_clones(sp, MY_SONGS_PLAYLIST_ID)
    reorder_playlist_three_clones(sp, MY_SONGS_PLAYLIST_ID)


if __name__ == '__main__':
    main()
