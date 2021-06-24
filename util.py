def get_track_ids_names(sp, playlist_id):
    """
    Returns a tuple of the form (id, name) of all
    the tracks in the playlist with the given ID
    """
    return [(item['track']['id'], item['track']['name']) for item in
            sp.playlist(playlist_id, fields='tracks')['tracks']['items']]


def get_nr_of_tracks(sp, playlist_id):
    """
    Returns the number of tracks in the playlist with the given ID
    """
    return sp.playlist(playlist_id, fields='tracks')['tracks']['total']