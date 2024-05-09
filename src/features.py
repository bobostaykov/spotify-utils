import random
from random import randint

import math

from constants import LOW_MIN_DISTANCE_TWO_CLONES_AS_FRACTION, HIGH_MIN_DISTANCE_TWO_CLONES_AS_FRACTION, \
    LOW_MIN_DISTANCE_THREE_CLONES_AS_FRACTION, HIGH_MIN_DISTANCE_THREE_CLONES_AS_FRACTION
from util import get_tracks, divide_in_chunks


def shuffle(sp, main_playlist_id, good_playlist_id, best_playlist_id, should_shuffle, should_reorder):
    """ Shuffles the tracks of the given playlist, keeping clones of a track apart """

    if should_shuffle and should_reorder:
        print('Started shuffle and reordering...')
    elif should_shuffle:
        print('Started shuffle...')
    else:
        print('Started reordering...')

    tracks = get_tracks(sp, main_playlist_id)
    main_playlist_size = len(tracks)
    non_local_tracks = [track for track in tracks if not track['is_local']]
    if should_shuffle:
        random.shuffle(non_local_tracks)
    if should_reorder:
        non_local_tracks = reorder(sp, non_local_tracks, good_playlist_id, best_playlist_id)
    non_local_tracks_ids = [track['id'] for track in non_local_tracks]
    # A maximum of 100 tracks can be deleted/added at once
    for chunk in divide_in_chunks(non_local_tracks_ids, 100):
        sp.playlist_remove_all_occurrences_of_items(main_playlist_id, chunk)
    try:
        reordered_non_local_track_ids = [track['id'] for track in non_local_tracks]
        for chunk in divide_in_chunks(reordered_non_local_track_ids, 100):
            sp.playlist_add_items(main_playlist_id, chunk)
    except:
        for chunk in divide_in_chunks(non_local_tracks_ids, 100):
            sp.playlist_add_items(main_playlist_id, chunk)
    local_tracks = [track for track in tracks if track['is_local']]
    # Minimal distance between any two clones of the same local track
    min_distance = math.floor(main_playlist_size * HIGH_MIN_DISTANCE_THREE_CLONES_AS_FRACTION)
    reordered_local_tracks = {}
    for track in local_tracks:
        if track['uri'] in reordered_local_tracks:
            new_index = (reordered_local_tracks[track['uri']] + min_distance) % main_playlist_size
        else:
            new_index = random.randint(1, main_playlist_size)
        sp.playlist_reorder_items(main_playlist_id, range_start=0, insert_before=new_index)
        reordered_local_tracks[track['uri']] = new_index

    print('Done')


def reorder(sp, tracks, good_playlist_id, best_playlist_id):
    """
    Reorders the given tracks so that the ones that appear
    two or three times (clones) are not too close to each other
    """

    tracks_count = len(tracks)
    reordered_tracks = tracks

    # Reorder tracks with 2 clones
    for good_track in get_tracks(sp, good_playlist_id):
        if good_track['is_local']:
            continue
        # Minimal distance between two clones of the same track
        min_distance = randint(
            math.floor(tracks_count * LOW_MIN_DISTANCE_TWO_CLONES_AS_FRACTION),
            math.floor(tracks_count * HIGH_MIN_DISTANCE_TWO_CLONES_AS_FRACTION))
        clone_indices = [index for index, track in enumerate(reordered_tracks) if track['id'] == good_track['id']]
        if len(clone_indices) != 2:
            good_track_name = good_track['name']
            print(f'(!) "{good_track_name}" should be present twice, but it is not.')
            continue
        if clone_indices[1] - clone_indices[0] < min_distance:
            new_index = (clone_indices[0] + min_distance) % tracks_count
            reordered_tracks.insert(new_index, reordered_tracks.pop(clone_indices[1]))

    # Reorder tracks with 3 clones
    for best_track in get_tracks(sp, best_playlist_id):
        if best_track['is_local']:
            continue
        # Minimal distance between any two clones of the same track
        min_distance = randint(
            math.floor(tracks_count * LOW_MIN_DISTANCE_THREE_CLONES_AS_FRACTION),
            math.floor(tracks_count * HIGH_MIN_DISTANCE_THREE_CLONES_AS_FRACTION))
        clone_indices = [index for index, track in enumerate(reordered_tracks) if track['id'] == best_track['id']]
        if len(clone_indices) != 3:
            best_track_name = best_track['name']
            print(f'(!) "{best_track_name}" should be present three times, but it is not.')
            continue
        if clone_indices[1] - clone_indices[0] < min_distance:
            new_index = (clone_indices[0] + min_distance) % tracks_count
            reordered_tracks.insert(new_index, reordered_tracks.pop(clone_indices[1]))
            if clone_indices[1] < clone_indices[2] < new_index:
                # Third clone has shifted, due to moving the second one
                clone_indices[2] -= 1
            if abs(clone_indices[2] - new_index) < min_distance:
                # Third clone is being moved to the beginning of the list,
                # make sure it's not too close to the first clone
                reordered_tracks.insert((new_index + min_distance) % tracks_count,
                                        reordered_tracks.pop(clone_indices[2]))
        elif clone_indices[2] - clone_indices[1] < min_distance:
            new_index = (clone_indices[1] + min_distance) % tracks_count
            if abs(clone_indices[0] - new_index) < min_distance:
                new_index = (clone_indices[0] + min_distance) % tracks_count
            reordered_tracks.insert(new_index, reordered_tracks.pop(clone_indices[2]))

    return reordered_tracks


def get_intersection(sp, playlist1_id, playlist2_id):
    """
    Returns a tuple of the form (id, name) of all
    the tracks present in both playlists
    """

    playlist1_name = sp.playlist(playlist1_id, fields='name')['name']
    playlist2_name = sp.playlist(playlist2_id, fields='name')['name']
    playlist1_tracks = get_tracks(sp, playlist1_id)
    playlist2_tracks = get_tracks(sp, playlist2_id)
    smaller_playlist = playlist1_tracks if len(playlist1_tracks) < len(playlist2_tracks) else playlist2_tracks
    larger_playlist = playlist1_tracks if len(playlist1_tracks) >= len(playlist2_tracks) else playlist2_tracks

    intersection = [track for track in smaller_playlist if track in larger_playlist]

    if intersection:
        print(f'Intersection of playlists "{playlist1_name}" and "{playlist2_name}":')
        [print(f'   {track["name"]}') for track in intersection]
    else:
        print(f'Playlists "{playlist1_name}" and "{playlist2_name}" have no tracks in common')

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

    difference = [track for track in base_playlist_tracks if track not in playlist2_tracks]

    if difference:
        print(f'Tracks from "{base_playlist_name}" that are missing from "{playlist2_name}":')
        [print(f'   {track["name"]}') for track in difference]
    else:
        print(f'"{playlist2_name}" contains all tracks from "{base_playlist_name}"')

    return difference
