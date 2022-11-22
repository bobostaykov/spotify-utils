import time
from argparse import ArgumentParser
from dotenv import load_dotenv

import spotipy
from gooey import Gooey
from spotipy.oauth2 import SpotifyOAuth

from reorder import reorder
from test import test
from util import shuffle, get_intersection, get_playlist_id, get_difference, get_total_time


@Gooey(program_name='Spotify Utilities', default_size=(800, 700))
def main():
    load_dotenv()
    parser = ArgumentParser(prog='Spotify Utils')

    parser.add_argument('--main_playlist',
                        default='My Songs',
                        required=True,
                        help='Main playlist name. The playlist on which to execute actions')

    parser.add_argument('--good_playlist',
                        default='Good',
                        required=True,
                        help='Good playlist name. The playlist which contains the good (double) tracks')

    parser.add_argument('--best_playlist',
                        default='Best',
                        required=True,
                        help='Best playlist name. The playlist which contains the best (triple) tracks')
    parser.add_argument('--no-shuffle', action='store_true',
                        help='Do not shuffle playlist')
    parser.add_argument('--no-reorder', action='store_true',
                        help='Do not reorder playlist')
    parser.add_argument('--no-test', action='store_true',
                        help='Do not run test on playlist')
    parser.add_argument('--intersection', nargs=2,
                        help='Two playlist names between quotation marks, separated by space. Get the intersection of the two playlists. If this function is used, the others are skipped.')
    parser.add_argument('--difference', nargs=2,
                        help='Two playlist names between quotation marks, separated by space. Get the tracks present in the first playlist but missing from the second one. If this function is used, the others are skipped (except "intersecion").')

    args = parser.parse_args()

    start_time = time.time()

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
        if not args.no_shuffle:
            shuffle(sp, main_playlist_id)
        if not args.no_reorder:
            good_playlist_id = get_playlist_id(sp, args.good_playlist)
            best_playlist_id = get_playlist_id(sp, args.best_playlist)
            reorder(sp, main_playlist_id, good_playlist_id, best_playlist_id)
        if not args.no_test:
            test(sp, main_playlist_id)

    print(f'\nTotal time: {get_total_time(start_time)}')


if __name__ == '__main__':
    main()
