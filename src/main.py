import time

import spotipy
from dotenv import load_dotenv
from gooey import Gooey, GooeyParser
from spotipy.oauth2 import SpotifyOAuth

from features import get_intersection, get_difference, shuffle, convert_to_mp3
from util import get_playlist_id, get_total_time, test


@Gooey(program_name='Spotify Utils', default_size=(500, 750), tabbed_groups=True, required_cols=1, optional_cols=1)
def main():
    start_time = time.time()

    load_dotenv()
    parser = GooeyParser()

    shuffle_arg_group = parser.add_argument_group(title='Shuffle',
                                                  description='Shuffle a playlist and reorder it, so that the tracks that are present twice (from Good playlist) or three times (from Best playlist) are not close to each other')
    shuffle_arg_group.add_argument('--main_playlist', default='My Songs', help='Main playlist name',
                                   gooey_options={'show_label': False})
    shuffle_arg_group.add_argument('--good_playlist', default='Good', help='Good playlist name',
                                   gooey_options={'show_label': False})
    shuffle_arg_group.add_argument('--best_playlist', default='Best', help='Best playlist name',
                                   gooey_options={'show_label': False})
    shuffle_arg_group.add_argument('--shuffle', widget='CheckBox', default=True, action='store_false',
                                   help='  Shuffle playlist', gooey_options={'show_label': False})
    shuffle_arg_group.add_argument('--reorder', widget='CheckBox', default=True, action='store_false',
                                   help='  Reorder playlist', gooey_options={'show_label': False})
    shuffle_arg_group.add_argument('--test', widget='CheckBox', default=True, action='store_false',
                                   help='  Check if playlist is well-ordered', gooey_options={'show_label': False})

    mp3_arg_group = parser.add_argument_group(title='Convert to MP3',
                                              description='Convert a playlist to MP3 files and save them locally')
    mp3_arg_group.add_argument('--playlist', help='Playlist name', gooey_options={'show_label': False})
    mp3_arg_group.add_argument('--save_path', help='Full path to save MP3 songs to',
                               gooey_options={'show_label': False})

    misc_arg_group = parser.add_argument_group(title='Misc')
    misc_arg_group.add_argument('--intersection', nargs=2,
                                help='Two playlist names between quotation marks, separated by space. Get the intersection of the two playlists')
    misc_arg_group.add_argument('--difference', nargs=2,
                                help='Two playlist names between quotation marks, separated by space. Get the tracks present in the first playlist but missing from the second one')

    args = parser.parse_args()

    # Peculiarity of ArgParse and the fact that the default values are True
    should_shuffle = not args.shuffle
    should_reorder = not args.reorder
    should_test = not args.test

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(scope='playlist-modify-private playlist-modify-public'),
        requests_timeout=100,
        retries=10)

    if args.playlist or args.save_path or args.intersection or args.difference:
        if args.playlist and args.save_path:
            playlist_id = get_playlist_id(sp, args.playlist)
            convert_to_mp3(sp, playlist_id, args.save_path)
        if args.intersection:
            playlist1_id = get_playlist_id(sp, args.intersection[0])
            playlist2_id = get_playlist_id(sp, args.intersection[1])
            get_intersection(sp, playlist1_id, playlist2_id)
        if args.difference:
            base_playlist_id = get_playlist_id(sp, args.difference[0])
            playlist2_id = get_playlist_id(sp, args.difference[1])
            get_difference(sp, base_playlist_id, playlist2_id)
    elif args.main_playlist and args.good_playlist and args.best_playlist:
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
