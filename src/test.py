import math
from time import time

from constants import LOW_MIN_DISTANCE_TWO_CLONES_AS_FRACTION, \
    LOW_MIN_DISTANCE_THREE_CLONES_AS_FRACTION
from util import get_nr_of_tracks, get_total_time


def test(sp, playlist_id):
    """
    Checks if the tracks occurring more than once (clones)
    are all far enough from each other
    """

    print('\nStarted test...')
    start_time = time()

    # Stores key-value pairs in the form {(track_id, track_name): last_occurrence}
    # Using track name and ID because local tracks have no ID and some (different) tracks
    # have the same name
    tracks_last_index_dict = dict()
    clones_too_close = 0
    playlist_size = get_nr_of_tracks(sp, playlist_id)
    # Adding a margin of 15 because, when reordering tracks, after setting two clones
    # <min_distance> tracks apart, tracks between the two clones may move and make the
    # distance a little smaller
    min_distance = math.floor(
        playlist_size * min(LOW_MIN_DISTANCE_TWO_CLONES_AS_FRACTION,
                            LOW_MIN_DISTANCE_THREE_CLONES_AS_FRACTION) - 15)
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
            if (track_name, track_id) in tracks_last_index_dict:
                index_of_last_clone = tracks_last_index_dict[(track_name, track_id)]
                if current_track_index - index_of_last_clone < min_distance:
                    clones_too_close += 1
                    print(
                        f'Clones of track "{track_name}" too close! Indices: {index_of_last_clone}, {current_track_index}')
            tracks_last_index_dict[(track_name, track_id)] = current_track_index
        if not tracks['next']:
            break
        tracks = sp.next(tracks)
        page_index += 1

    total_time = get_total_time(start_time)
    if clones_too_close:
        print(
            f'Completed test: Processed {playlist_size} tracks in {total_time}. {clones_too_close} tracks were too close.')
    else:
        print(
            f'Completed test, playlist is well ordered! Processed {playlist_size} tracks in {total_time}.')
