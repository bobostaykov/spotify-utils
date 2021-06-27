import spotipy
from spotipy.oauth2 import SpotifyOAuth

from constants import MY_SONGS_PLAYLIST_ID, BEST_PLAYLIST_ID, GOOD_PLAYLIST_ID
from reorder import reorder
from src.test import test
from util import shuffle, get_intersection


def main():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(scope='playlist-modify-private playlist-modify-public'))

    shuffle(sp, MY_SONGS_PLAYLIST_ID)
    reorder(sp, MY_SONGS_PLAYLIST_ID)
    test(sp, MY_SONGS_PLAYLIST_ID)
    get_intersection(sp, BEST_PLAYLIST_ID, GOOD_PLAYLIST_ID)


if __name__ == '__main__':
    main()
