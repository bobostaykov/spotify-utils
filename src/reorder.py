import math
from random import randint
from time import time

from constants import LOW_MIN_DISTANCE_TWO_CLONES_AS_FRACTION, \
    HIGH_MIN_DISTANCE_TWO_CLONES_AS_FRACTION, LOW_MIN_DISTANCE_THREE_CLONES_AS_FRACTION, \
    HIGH_MIN_DISTANCE_THREE_CLONES_AS_FRACTION
from util import get_nr_of_tracks, get_tracks, get_total_time


def reorder(sp, main_playlist_id, good_playlist_id, best_playlist_id):
    """
    Runs the reordering process for double and for triple clones,
    and displays the total time needed
    """
    print('\nStarted reordering...')
    start_time = time()
    reorder_playlist_two_clones(sp, main_playlist_id, good_playlist_id)
    reorder_playlist_three_clones(sp, main_playlist_id, best_playlist_id)
    playlist_size = get_nr_of_tracks(sp, main_playlist_id)
    print(f'Total: {playlist_size} tracks in {get_total_time(start_time)}.')


def reorder_playlist_two_clones(sp, main_playlist_id, good_playlist_id):
    """
    Reorders the playlist so that the tracks that appear
    twice (clones) are not too close to each other
    """

    size = get_nr_of_tracks(sp, main_playlist_id)
    reordered_tracks = 0

    for clone in get_tracks(sp, good_playlist_id):
        # Minimal distance between two clones of the same track
        min_distance = randint(
            math.floor(size * LOW_MIN_DISTANCE_TWO_CLONES_AS_FRACTION),
            math.floor(size * HIGH_MIN_DISTANCE_TWO_CLONES_AS_FRACTION))
        clone_id = clone[0]
        clone_name = clone[1]
        playlist = sp.playlist(main_playlist_id, fields='tracks, name')
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
                if (first_clone_index != -1
                        and current_track_index - first_clone_index >= min_distance):
                    # The distance between the two clones is already >= the minimal one,
                    # stop searching for the second clone
                    distance_already_enough = True
                    break
                if page[i]['track']['id'] == clone_id:
                    if first_clone_index == -1:
                        first_clone_index = current_track_index
                    else:
                        second_clone_index = current_track_index
                        break
            else:
                # Executed only if we don't break out of the inner-most for loop
                if not playlist_tracks['next']:
                    break
                playlist_tracks = sp.next(playlist_tracks)
                page_index += 1
                continue
            # Executed only if we break out the inner-most for loop
            break

        if first_clone_index == -1:
            print(
                f'[x] Track "{clone_name}" not present in playlist "{playlist["name"]}"')
        elif second_clone_index == -1:
            if not distance_already_enough:
                print(
                    f'[x] Track "{clone_name}" does not have a clone in playlist "{playlist["name"]}"')
        else:
            # Loop to the beginning of the playlist if the index
            # to insert on is larger than the playlist size
            print(
                f'Clones of track "{clone_name}" too close (indices: {first_clone_index}, {second_clone_index}), reordering.')
            index_to_insert_on = (first_clone_index + min_distance) % size
            sp.playlist_reorder_items(main_playlist_id,
                                      range_start=second_clone_index,
                                      insert_before=index_to_insert_on)
            reordered_tracks += 1

    if reordered_tracks:
        tracks = 'track' if reordered_tracks == 1 else 'tracks'
        print(
            f'Completed reordering of double clones! Reordered {reordered_tracks} {tracks}.\n')
    else:
        print('Completed reordering of double clones! Didn\'t change playlist.\n')


def reorder_playlist_three_clones(sp, main_playlist_id, best_playlist_id):
    """
    Reorders the playlist so that the tracks that appear
    three times (clones) are not too close to each other
    """

    size = get_nr_of_tracks(sp, main_playlist_id)
    reordered_tracks = 0

    for clone in get_tracks(sp, best_playlist_id):
        # Minimal distance between any two clones of the same track
        min_distance = randint(
            math.floor(size * LOW_MIN_DISTANCE_THREE_CLONES_AS_FRACTION),
            math.floor(size * HIGH_MIN_DISTANCE_THREE_CLONES_AS_FRACTION))
        clone_id = clone[0]
        clone_name = clone[1]
        playlist = sp.playlist(main_playlist_id, fields='tracks, name')
        playlist_tracks = playlist['tracks']
        page_size = playlist_tracks['limit']
        first_clone_index = -1
        second_clone_index = -1
        third_clone_index = -1
        page_index = 0
        # Distance between any two of the three clones already enough
        distance_already_enough = False

        while True:
            page = playlist_tracks['items']
            for i in range(len(page)):
                current_track_index = page_index * page_size + i
                if (first_clone_index != -1
                        and second_clone_index != -1
                        and abs(first_clone_index - second_clone_index) >= min_distance
                        and current_track_index - second_clone_index >= min_distance):
                    # The distance between any two of the three clones is
                    # already >= the minimal one, stop searching for the third clone
                    distance_already_enough = True
                    break
                if page[i]['track']['id'] == clone_id:
                    if first_clone_index == -1:
                        first_clone_index = current_track_index
                    elif second_clone_index == -1:
                        second_clone_index = current_track_index
                    else:
                        # Found all three clones, stop searching
                        third_clone_index = current_track_index
                        break
            else:
                # Executed only if we don't break out of the inner-most for loop
                if not playlist_tracks['next']:
                    break
                playlist_tracks = sp.next(playlist_tracks)
                page_index += 1
                continue
            # Executed only if we break out the inner-most for loop
            break

        if first_clone_index == -1:
            print(
                f'[x] Track "{clone_name}" not present in playlist "{playlist["name"]}"')
        elif second_clone_index == -1:
            print(
                f'[x] Track "{clone_name}" does not have a second clone in playlist "{playlist["name"]}"')
        elif third_clone_index == -1:
            if not distance_already_enough:
                print(
                    f'[x] Track "{clone_name}" does not have a third clone in playlist "{playlist["name"]}"')
        else:
            # Have to reorder playlist.
            # Loop to the beginning of the playlist if the position
            # to insert on is larger than the playlist size.
            # Having to increments and decrements by 1 is a result of the
            # moving element leaving one empty space behind.

            print(
                f'Clones of track "{clone_name}" too close (indices: {first_clone_index}, {second_clone_index}, {third_clone_index}), reordering.')

            if second_clone_index - first_clone_index < min_distance:
                decrement = False
                index_to_insert_second_clone_on = \
                    (first_clone_index + min_distance) % size
                if index_to_insert_second_clone_on > second_clone_index:
                    index_to_insert_second_clone_on += 1
                    decrement = True
                sp.playlist_reorder_items(main_playlist_id,
                                          range_start=second_clone_index,
                                          insert_before=index_to_insert_second_clone_on)
                if first_clone_index > index_to_insert_second_clone_on:
                    first_clone_index += 1
                if third_clone_index < index_to_insert_second_clone_on:
                    third_clone_index -= 1
                second_clone_index = (index_to_insert_second_clone_on - 1 if decrement
                                      else index_to_insert_second_clone_on)
                reordered_tracks += 1

            if abs(third_clone_index - second_clone_index) < min_distance:
                decrement = False
                index_to_insert_third_clone_on = \
                    (second_clone_index + min_distance) % size
                if index_to_insert_third_clone_on > third_clone_index:
                    index_to_insert_third_clone_on += 1
                    decrement = True
                sp.playlist_reorder_items(main_playlist_id,
                                          range_start=third_clone_index,
                                          insert_before=index_to_insert_third_clone_on)
                third_clone_index = (index_to_insert_third_clone_on - 1 if decrement
                                     else index_to_insert_third_clone_on)
                if third_clone_index <= first_clone_index:
                    first_clone_index += 1
                reordered_tracks += 1

            lastly_moved_clone_index = -1

            # Either the third clone was moved to the beginning of the playlist where it
            # is now too close to the first one, they were close to each other from the
            # beginning, or they got too close as a result from moving the second one.
            # Move the clone with the larger index beyond the minimal distance from the
            # one with the smaller index.
            if abs(first_clone_index - third_clone_index) < min_distance:
                decrement = False
                index_to_insert_clone_on = (min(first_clone_index,
                                                third_clone_index) + min_distance) % size
                if index_to_insert_clone_on > max(first_clone_index, third_clone_index):
                    index_to_insert_clone_on += 1
                    decrement = True
                sp.playlist_reorder_items(main_playlist_id,
                                          range_start=max(first_clone_index,
                                                          third_clone_index),
                                          insert_before=index_to_insert_clone_on)
                lastly_moved_clone_index = (index_to_insert_clone_on - 1 if decrement
                                            else index_to_insert_clone_on)
                if min(first_clone_index, third_clone_index) > lastly_moved_clone_index:
                    reordered_tracks += 1

            # After moving the first or third clone, it could end up near the second one
            if lastly_moved_clone_index != -1 and abs(
                    lastly_moved_clone_index - second_clone_index) < min_distance:
                index_to_insert_clone_on = (min(lastly_moved_clone_index,
                                                second_clone_index) + min_distance) % size
                if index_to_insert_clone_on > max(lastly_moved_clone_index,
                                                  second_clone_index):
                    index_to_insert_clone_on += 1
                sp.playlist_reorder_items(main_playlist_id,
                                          range_start=max(lastly_moved_clone_index,
                                                          second_clone_index),
                                          insert_before=index_to_insert_clone_on)

    if reordered_tracks:
        tracks = 'track' if reordered_tracks == 1 else 'tracks'
        print(
            f'Completed reordering of triple clones! Reordered {reordered_tracks} {tracks}.')
    else:
        print('Completed reordering of triple clones! Didn\'t change playlist.')
