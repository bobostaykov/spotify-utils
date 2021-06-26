import random


def get_track_ids_names(sp, playlist_id):
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
    playlist_size = get_nr_of_tracks(sp, playlist_id)
    current_index = 0
    for i in range(playlist_size):
        random_index = random.randrange(playlist_size)
        sp.playlist_reorder_items(playlist_id,
                                  range_start=current_index,
                                  insert_before=random_index + 1)
        if random_index <= current_index:
            current_index += 1
        # else: the track was moved down the playlist and
        # the track to move next slided in its place
