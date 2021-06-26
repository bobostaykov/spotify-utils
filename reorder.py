import math

from constants import GOOD_PLAYLIST_ID, BEST_PLAYLIST_ID
from util import get_nr_of_tracks, get_track_ids_names


def reorder_playlist_two_clones(sp, playlist_id):
    """
    Reorders the playlist so that the tracks that appear
    twice (clones) are not too close to each other
    """
    size = get_nr_of_tracks(sp, playlist_id)
    # Minimal distance between two clones of the same track
    min_distance = math.floor(size / 3)
    reordered_tracks = 0

    for clone in get_track_ids_names(sp, GOOD_PLAYLIST_ID):
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
                if (first_clone_index != -1
                        and current_track_index - first_clone_index >= min_distance):
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
                                      insert_before=index_to_insert_on)
            reordered_tracks += 1

    if reordered_tracks:
        tracks = 'track' if reordered_tracks == 1 else 'tracks'
        print(f'\nDone! Reordered {reordered_tracks} {tracks}.')
    else:
        print('\nDone! Didn\'t change playlist.')


def reorder_playlist_three_clones(sp, playlist_id):
    """
    Reorders the playlist so that the tracks that appear
    three times (clones) are not too close to each other
    """
    size = get_nr_of_tracks(sp, playlist_id)
    # Minimal distance between any two clones of the same track
    min_distance = math.floor(size / 4)
    reordered_tracks = 0

    for clone in get_track_ids_names(sp, BEST_PLAYLIST_ID):
        print(f'Processing "{clone[1]}"')

        playlist = sp.playlist(playlist_id, fields='tracks, name')
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
                if page[i]['track']['id'] == clone[0]:
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
                sp.next(playlist_tracks)
                page_index += 1
                continue
            # Executed only if we break out the inner-most for loop
            break

        if first_clone_index == -1:
            print(f'   Track not present in playlist "{playlist["name"]}"')
        elif second_clone_index == -1:
            print(
                f'   Track does not have a second clone in playlist "{playlist["name"]}"')
        elif third_clone_index == -1:
            if not distance_already_enough:
                print(
                    f'   Track does not have a third clone in playlist "{playlist["name"]}"')
        else:
            # Have to reorder playlist.
            # Loop to the beginning of the playlist if the position
            # to insert on is larger than the playlist size.
            # Having to increments and decrements by 1 is a result of the
            # moving element leaving one empty space behind.

            if second_clone_index - first_clone_index < min_distance:
                decrement = False
                index_to_insert_second_clone_on = \
                    (first_clone_index + min_distance) % size
                if index_to_insert_second_clone_on > second_clone_index:
                    index_to_insert_second_clone_on += 1
                    decrement = True
                sp.playlist_reorder_items(playlist_id,
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
                sp.playlist_reorder_items(playlist_id,
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
                sp.playlist_reorder_items(playlist_id,
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
                sp.playlist_reorder_items(playlist_id,
                                          range_start=max(lastly_moved_clone_index,
                                                          second_clone_index),
                                          insert_before=index_to_insert_clone_on)

    if reordered_tracks:
        tracks = 'track' if reordered_tracks == 1 else 'tracks'
        print(f'\nDone! Reordered {reordered_tracks} {tracks}.')
    else:
        print('\nDone! Didn\'t change playlist.')
