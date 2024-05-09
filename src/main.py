import time

import spotipy
from dotenv import load_dotenv
from gooey import Gooey, GooeyParser
from spotipy.oauth2 import SpotifyOAuth

from features import get_intersection, get_difference, shuffle
from util import get_playlist_id, get_total_time, test


@Gooey(program_name='Spotify Utilities', default_size=(800, 700))
def main():
    start_time = time.time()

    load_dotenv()
    parser = GooeyParser(prog='Spotify Utils')
    arg_group = parser.add_argument_group()

    arg_group.add_argument('--main_playlist', default='My Songs', required=True,
                           help='Main playlist name. The playlist on which to execute actions')
    arg_group.add_argument('--good_playlist', default='Good', required=True,
                           help='Good playlist name. The playlist which contains the good (double) tracks')
    arg_group.add_argument('--best_playlist', default='Best', required=True,
                           help='Best playlist name. The playlist which contains the best (triple) tracks')
    arg_group.add_argument('--shuffle', widget='CheckBox', default=True, action='store_false',
                           help='  Shuffle playlist')
    arg_group.add_argument('--reorder', widget='CheckBox', default=True, action='store_false',
                           help='  Reorder playlist')
    arg_group.add_argument('--test', widget='CheckBox', default=True, action='store_false',
                           help='  Test that playlist is well-ordered')
    arg_group.add_argument('--intersection', nargs=2,
                           help='Two playlist names between quotation marks, separated by space. Get the intersection of the two playlists. If this function is used, the others are skipped.')
    arg_group.add_argument('--difference', nargs=2,
                           help='Two playlist names between quotation marks, separated by space. Get the tracks present in the first playlist but missing from the second one. If this function is used, the others are skipped (except "intersecion").')

    args = parser.parse_args()

    # Peculiarity of ArgParse and the fact that the default values are True
    should_shuffle = not args.shuffle
    should_reorder = not args.reorder
    should_test = not args.test

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(scope='playlist-modify-private playlist-modify-public'),
        requests_timeout=100,
        retries=10)

    if args.intersection:
        playlist1_id = get_playlist_id(sp, args.intersection[0])
        playlist2_id = get_playlist_id(sp, args.intersection[1])
        get_intersection(sp, playlist1_id, playlist2_id)
    elif args.difference:
        base_playlist_id = get_playlist_id(sp, args.difference[0])
        playlist2_id = get_playlist_id(sp, args.difference[1])
        get_difference(sp, base_playlist_id, playlist2_id)
    else:
        main_playlist_id = get_playlist_id(sp, args.main_playlist)
        good_playlist_id = get_playlist_id(sp, args.good_playlist)
        best_playlist_id = get_playlist_id(sp, args.best_playlist)
        if should_shuffle or should_reorder:
            shuffle(sp, main_playlist_id, good_playlist_id, best_playlist_id, should_shuffle, should_reorder)
        if should_test:
            test(sp, main_playlist_id, good_playlist_id, best_playlist_id)

    print(f'\nTotal time: {get_total_time(start_time)}\n\n')


if __name__ == '__main__':
    main()
