import random
import sys
from time import time

from sortedcontainers import SortedList

from constants import USER_ID


def get_tracks(sp, playlist_id):
    """
    Returns a tuple of the form (id, name) of all
    the tracks in the playlist with the given ID
    """
    result = []
    tracks = sp.playlist(playlist_id, fields='tracks')['tracks']
    while True:
        result.extend([(item['track']['id'], item['track']['name']) for item in
                       tracks['items']])
        if not tracks['next']:
            break
        tracks = sp.next(tracks)
    return result


def get_nr_of_tracks(sp, playlist_id):
    """
    Returns the number of tracks in the playlist with the given ID
    """
    return sp.playlist(playlist_id, fields='tracks')['tracks']['total']


def shuffle(sp, playlist_id):
    """
    Shuffles the tracks of the playlist with the given ID
    """
    print('Started shuffle...')
    start_time = time()
    playlist_size = get_nr_of_tracks(sp, playlist_id)
    current_index = 0
    # Keep track of tracks already reordered
    indices_already_processed = SortedList()
    while current_index < playlist_size:
        random_index = random.randrange(playlist_size)
        sp.playlist_reorder_items(playlist_id,
                                  range_start=current_index,
                                  insert_before=random_index + 1)
        # The already processed indices change due to track reordering
        if random_index > current_index:
            indices_already_processed = SortedList(
                [index - 1 if current_index < index <= random_index else index
                 for index in indices_already_processed])
        elif random_index < current_index:
            indices_already_processed = SortedList(
                [index + 1 if random_index <= index < current_index else index
                 for index in indices_already_processed])
        indices_already_processed.add(random_index)
        while current_index in indices_already_processed:
            current_index += 1
    print(f'Shuffled playlist: {playlist_size} tracks in {get_total_time(start_time)}')


def get_total_time(start_time):
    """
    Returns the time elapsed since the start_time in a human readable way
    """
    end_time = time()
    total_time = end_time - start_time
    secs_mins_hours = 'seconds'
    if total_time >= 3600:
        total_time /= 3600
        secs_mins_hours = 'hours'
    elif total_time >= 60:
        total_time /= 60
        secs_mins_hours = 'minutes'
    total_time = round(total_time, 2)
    return f'{total_time} {secs_mins_hours}'


def get_playlist_id(sp, playlist_name):
    """
    Given the playlist's name, returns its ID
    """
    playlists = sp.user_playlists(USER_ID)['items']
    for playlist in playlists:
        if playlist['name'].lower() == playlist_name.lower():
            return playlist['id']
    sys.exit(f'No playlist with name "{playlist_name}" found')


def get_intersection(sp, playlist1_id, playlist2_id):
    """
    Returns a tuple of the form (id, name) of all
    the tracks present in both playlists
    """

    playlist1_name = sp.playlist(playlist1_id, fields='name')['name']
    playlist2_name = sp.playlist(playlist2_id, fields='name')['name']
    playlist1_tracks = get_tracks(sp, playlist1_id)
    playlist2_tracks = get_tracks(sp, playlist2_id)
    smaller_playlist = playlist1_tracks if len(playlist1_tracks) < len(
        playlist2_tracks) else playlist2_tracks
    larger_playlist = playlist1_tracks if len(playlist1_tracks) >= len(
        playlist2_tracks) else playlist2_tracks

    intersection = [track for track in smaller_playlist if track in larger_playlist]

    if intersection:
        print(f'Intersection of playlists "{playlist1_name}" and "{playlist2_name}":')
        [print(f'   {track[1]}') for track in intersection]
    else:
        print(
            f'Playlists "{playlist1_name}" and "{playlist2_name}" have no tracks in common')

    return intersection


def get_difference(sp, base_playlist_id, playlist2_id):
    """
    Returns a tuple of the form (id, name) of all the tracks present
    in the first playlist but missing from the second one
    """

    base_playlist_name = sp.playlist(base_playlist_id, fields='name')['name']
    playlist2_name = sp.playlist(playlist2_id, fields='name')['name']
    base_playlist_tracks = get_tracks(sp, base_playlist_id)
    playlist2_tracks = get_tracks(sp, playlist2_id)

    difference = [track for track in base_playlist_tracks if
                  track not in playlist2_tracks]

    if difference:
        print(
            f'Tracks from "{base_playlist_name}" that are missing from "{playlist2_name}":')
        [print(f'   {track[1]}') for track in difference]
    else:
        print(f'"{playlist2_name}" contains all tracks from "{base_playlist_name}"')

    return difference
