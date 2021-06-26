import math
from time import time

from constants import MIN_DISTANCE_TWO_CLONES_AS_FRACTION, \
    MIN_DISTANCE_THREE_CLONES_AS_FRACTION
from util import get_nr_of_tracks, get_total_time


def are_clones_close(sp, playlist_id):
    """
    Checks if the tracks occurring more than once (clones)
    are all far enough from each other
    """

    print('\nStarted test...')
    start_time = time()

    # Stores key-value pairs in the form <track_id, last_occurrence>
    tracks_last_index_dict = dict()
    playlist_size = get_nr_of_tracks(playlist_id)
    min_distance = math.floor(playlist_size * min(MIN_DISTANCE_TWO_CLONES_AS_FRACTION,
                                                  MIN_DISTANCE_THREE_CLONES_AS_FRACTION))
    tracks = sp.playlist(playlist_id, fields='tracks')['tracks']
    page_size = tracks['limit']
    page_index = 0

    # Iterate over all tracks in playlist and for each one
    # check if it is close to any of its clones
    while True:
        page = tracks['items']
        for i in range(len(page)):
            current_track_index = page_index * page_size + i
            track_id = page[i]['track']['id']
            track_name = page[i]['track']['name']
            if track_id in tracks_last_index_dict:
                index_of_last_clone = tracks_last_index_dict[track_id]
                if current_track_index - index_of_last_clone < min_distance:
                    print(
                        f'Clones of track "{track_name}" too close! Indices: {index_of_last_clone}, {current_track_index}')
            tracks_last_index_dict[track_id] = current_track_index
        if not tracks['next']:
            break
        tracks = sp.next(tracks)
        page_index += 1

    print(f'Completed test: {playlist_size} tracks in {get_total_time(start_time)}.')
