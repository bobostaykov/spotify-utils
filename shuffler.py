import math

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from constants import TEST_PLAYLIST_ID, TEST_2_PLAYLIST_ID

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(scope='playlist-modify-private playlist-modify-public'))


def get_track_ids_names(playlist_id):
    return [(item['track']['id'], item['track']['name']) for item in
            sp.playlist(playlist_id, fields='tracks')['tracks']['items']]


def get_nr_of_tracks(playlist_id):
    return sp.playlist(playlist_id, fields='tracks')['tracks']['total']


def reorder_playlist_two_clones(playlist_id):
    """
    Reorders the playlist so that the tracks that appear
    twice are not too close to each other
    """
    size = get_nr_of_tracks(playlist_id)
    # Minimal distance between two instances (clones) of the same track
    min_distance = math.floor(size / 3)
    reordered_tracks = 0

    for clone in get_track_ids_names(TEST_2_PLAYLIST_ID):
        print(f'Processing "{clone[1]}"')

        playlist = sp.playlist(playlist_id, fields='tracks, name')
        playlist_tracks = playlist['tracks']
        page_size = playlist_tracks['limit']
        first_clone_index = -1
        second_clone_index = -1
        page_index = 0
        distance_already_enough = False

        while True:
            page = playlist_tracks['items']
            for i in range(len(page)):
                current_track_index = page_index * page_size + i
                if first_clone_index != -1 and current_track_index - first_clone_index >= min_distance:
                    # The distance between the two clones is already >= the minimal one,
                    # stop searching for the second clone
                    distance_already_enough = True
                    break
                if page[i]['track']['id'] == clone[0]:
                    if first_clone_index == -1:
                        first_clone_index = current_track_index
                    else:
                        second_clone_index = current_track_index
                        break
            else:
                # Executed only if we don't break out of the inner-most for loop
                if not playlist_tracks['next']:
                    break
                sp.next(playlist_tracks)
                page_index += 1
                continue
            # Executed only if we break out the inner-most for loop
            break

        if first_clone_index == -1:
            print(f'   Track not present in playlist "{playlist["name"]}"')
        elif second_clone_index == -1:
            if not distance_already_enough:
                print(f'   Track does not have a clone in playlist "{playlist["name"]}"')
        else:
            # Loop to the beginning of the playlist if the index
            # to insert on is larger than the playlist size
            index_to_insert_on = (first_clone_index + min_distance) % size
            sp.playlist_reorder_items(playlist_id,
                                      range_start=second_clone_index,
                                      insert_before=index_to_insert_on + 1)
            reordered_tracks += 1

    if reordered_tracks:
        tracks = 'track' if reordered_tracks == 1 else 'tracks'
        print(f'\nDone! Reordered {reordered_tracks} {tracks}.')
    else:
        print('\nDone! Didn\'t change playlist.')


reorder_playlist_two_clones(TEST_PLAYLIST_ID)
