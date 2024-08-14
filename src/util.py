import math
import sys
from time import time

from constants import USER_ID, TEST_MIN_DISTANCE


def get_tracks(sp, playlist_id):
    """
    Returns a dict with id, URI, name and is_local for all the
    tracks in the playlist with the given ID
    """

    result = []
    page_size = 100
    offset = 0
    while True:
        track_batch = sp.playlist_items(playlist_id, limit=page_size, offset=offset)
        result.extend([{
            'id': item['track']['id'],
            'uri': item['track']['uri'],
            'name': item['track']['name'],
            'artist': item['track']['artists'][0]['name'],
            'is_local': item['track']['is_local'],
        } for item in track_batch['items']])
        if not track_batch['next']:
            break
        offset += page_size
    return result


def get_nr_of_tracks(sp, playlist_id):
    """ Returns the number of tracks in the playlist with the given ID """

    return sp.playlist_items(playlist_id)['total']


def get_playlist_id(sp, playlist_name):
    """ Given the playlist's name, returns its ID """

    playlists = sp.user_playlists(USER_ID)['items']
    for playlist in playlists:
        if playlist['name'].lower() == playlist_name.lower():
            return playlist['id']
    sys.exit(f'No playlist with name "{playlist_name}" found.')


def get_total_time(start_time):
    """ Returns the time elapsed since the start_time in a human-readable way """

    end_time = time()
    total_time = end_time - start_time
    unit = 'seconds'
    if total_time >= 3600:
        total_time /= 3600
        unit = 'hours'
    elif total_time >= 60:
        total_time /= 60
        unit = 'minutes'
    total_time = round(total_time, 2)
    return f'{total_time} {unit}'


def divide_in_chunks(list_to_divide, chunk_size):
    """ Returns a list of lists - the given list divided into chunks of the given size """

    return [list_to_divide[i:i + chunk_size] for i in range(0, len(list_to_divide), chunk_size)]


def test(sp, main_playlist_id, good_playlist_id, best_playlist_id):
    """ Checks playlists are OK """

    print('\nStarted test...')
    check_well_ordered(sp, main_playlist_id)
    check_clones_ok(sp, main_playlist_id, good_playlist_id, best_playlist_id)
    print('\nDone')


def check_well_ordered(sp, playlist_id):
    """
    Checks whether the playlist is well-ordered, i.e. the tracks occurring
    more than once (clones) are all far enough from each other
    """

    tracks = get_tracks(sp, playlist_id)
    playlist_size = len(tracks)
    min_distance = math.floor(playlist_size * TEST_MIN_DISTANCE)
    clones_too_close = 0

    # For each track in playlist check if it is too close to any of its clones. Only looks forward.
    for track_index, track in enumerate(tracks):
        for current_track_index in range(track_index + 1, len(tracks)):
            if current_track_index - track_index >= min_distance:
                # Min distance already reached, clones can not be too close
                break
            if tracks[current_track_index] == track:
                track_name = track['name']
                print(f'(!) Clones of track "{track_name}" too close! Indices: {track_index}, {current_track_index}')
                clones_too_close += 1

    if clones_too_close == 0:
        print(f'\nMain playlist is well ordered!\n')


def check_clones_ok(sp, main_playlist_id, good_playlist_id, best_playlist_id):
    """ Checks whether all double clones in the playlist are present
    in the good playlist and the same for the triple ones """

    all_tracks = get_tracks(sp, main_playlist_id)
    good_tracks = get_tracks(sp, good_playlist_id)
    best_tracks = get_tracks(sp, best_playlist_id)
    checked_tracks = []

    for track in all_tracks:
        if track in checked_tracks:
            continue
        # Checking by URI because local tracks don't have ID
        track_indices = [index for index, t in enumerate(all_tracks) if t['uri'] == track['uri']]
        if len(track_indices) == 2:
            checked_tracks.append(track)
            if track not in good_tracks:
                track_name = track['name']
                print(
                    f'(!) "{track_name}" is present twice in the main playlist, but not present in the good playlist.')
        elif len(track_indices) == 3:
            checked_tracks.append(track)
            if track not in best_tracks:
                track_name = track['name']
                print(
                    f'(!) "{track_name}" is present three times in the main playlist, but not present in the best playlist.')


def get_youtube_search_url(artist_name: str, track_name: str) -> str:
    """ Returns the URL to a YouTube search for
    the given song by the given artist """

    query = f'{artist_name} {track_name}'.replace(' ', '+')
    return f'https://www.youtube.com/results?search_query={query}'


def get_last_occurrence_index(text, char):
    """ Returns the index of the last occurrence of the given char in the given text """

    return len(text) - 1 - text[::-1].index(char)


def get_track_name_core(track_name):
    """ Returns the most significant part of a track name.
    I.e. strips away things like featured artists """

    stripped = track_name.split('(')[0]
    stripped = stripped.split('-')[0]
    stripped = stripped.split('feat')[0]
    stripped = stripped.split('ft')[0]
    return stripped.strip()


class CustomLogger:
    """ Used to suppress YoutubeDL output """

    def error(self):
        pass

    def warning(self):
        pass

    def debug(self):
        pass
