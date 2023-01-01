#
# 1337ris -- constants.py
# Henry Weiss
#
# Defines all symbolic constants that can be referenced globally. A lot
# of constants are tied to certain classes, and don't need to be accessed
# globally, but the ones that need to be are defined here.
#

from headers import *

# General constants
IMG_PATH = "data/images/"
SND_PATH = "data/sounds/"
MUSIC_PATH = "data/music/"

DIMENSIONS = (640, 480)
BLOCK_SIZE = (24, 24)
SCREEN_WIDTH, SCREEN_HEIGHT = DIMENSIONS  # Convenience constants
SOUND_FREQ = 44100
DEFAULT_FONT = 'data/freesansbold.ttf'  # Doesn't copy on Windows when used with py2exe, so we'll include it ourselves

GRID_SIZE = (10, 22)  # 22 high to allow rotation off-screen at the top
GRID_WIDTH, GRID_HEIGHT = GRID_SIZE  # Convenience constants
GRID_Y_OFFSET = 2  # Only 20 rows are visible

# Tile types (interchangeably referred to as blocks)
TILES = ['B', 'D', 'I', 'J', 'L', 'O', 'S', 'T', 'Z']
NORMAL_TILES = TILES[2:]

# Game states
(
    STATE_LOADING,
    STATE_MAIN_MENU,
    STATE_HIGH_SCORES,
    STATE_TRADITIONAL,
    STATE_CROSS_CUT,
    STATE_CONVERGENCE,
    STATE_PSYCHEDELIC
) = range(-1, 6)  # Loading is not part of the game state dict

# For high scores
MAX_ENTRIES = 20

GAME_MODES = ['Traditional', 'Cross-Cut', 'Convergence', 'Psychedelic']
HIGH_SCORE_FILES = ["data/high scores.dat", "data/crosscut scores.dat", "data/convergence scores.dat", "data/psychedelic scores.dat"]
DELIMITER = '\0'
TOTAL_ITEMS = 4

# The tuple that is used to store high score entries in a file. Saved in order of tiebreakers.
(
    ENTRY_SCORE,
    ENTRY_LEVEL,
    ENTRY_TIME,
    ENTRY_NAME,
) = range(TOTAL_ITEMS)

BLANK_ENTRY = (0, 0, 0, "<empty>")

# This is the format of the userdata passed into the high scores.
(
    USERDATA_MODE,
    USERDATA_SCORE,
    USERDATA_LEVEL,
    USERDATA_TIME
) = range(TOTAL_ITEMS)

# Preference file settings
PREFS_FILE = "data/prefs.cfg"

# Preference keys
MUSIC_VOLUME = "music_volume_float"
SOUND_VOLUME = "sound_volume_float"
RUN_FULLSCREEN = "fullscreen_bool"
DRAW_FRAMERATE = "draw_fps_bool"
STREAM_MUSIC = "stream_music_bool"
DRAW_BG = "draw_backgrounds_bool"
SHOW_PREVIEW = "show_preview_bool"
DRAW_GHOST = "draw_ghost_bool"

SETTINGS = [MUSIC_VOLUME, SOUND_VOLUME, DRAW_FRAMERATE, STREAM_MUSIC,
            DRAW_BG, SHOW_PREVIEW, DRAW_GHOST]

# Key config
MOVE_LEFT_KEY = "move_left_keycode_int"
MOVE_RIGHT_KEY = "move_right_keycode_int"
ROTATE_RIGHT_KEY = "rotate_keycode_int"
ROTATE_LEFT_KEY = "rotate_backwards_keycode_int"
SPEEDUP_KEY = "speedup_keycode_int"
DROP_KEY = "drop_keycode_int"
DETONATE_KEY = "detonate_keycode_int"
PAUSE_KEY = "pause_keycode_int"
QUIT_KEY = "quit_keycode_int"

CONTROLS = [MOVE_LEFT_KEY, MOVE_RIGHT_KEY, ROTATE_RIGHT_KEY, ROTATE_LEFT_KEY,
            SPEEDUP_KEY, DROP_KEY, DETONATE_KEY, PAUSE_KEY, QUIT_KEY]

# Default values
DEFAULTS = {MUSIC_VOLUME: 0.75, SOUND_VOLUME: 0.75, RUN_FULLSCREEN: False, DRAW_FRAMERATE: False, STREAM_MUSIC: True, DRAW_GHOST: True,
            DRAW_BG: True, SHOW_PREVIEW: True, MOVE_LEFT_KEY: K_LEFT, MOVE_RIGHT_KEY: K_RIGHT, ROTATE_RIGHT_KEY: K_UP, ROTATE_LEFT_KEY: K_TAB,
            SPEEDUP_KEY: K_DOWN, DROP_KEY: K_SPACE, DETONATE_KEY: K_LSHIFT, PAUSE_KEY: K_ESCAPE, QUIT_KEY: K_q}

# For screen transitions
TOTAL_TRANSITIONS = 8

(
    TRANSITION_RANDOM,
    TRANSITION_OPEN,
    TRANSITION_CLOSE,
    TRANSITION_CATCHUP,
    TRANSITION_CROSSFADE,
    TRANSITION_BLOCKS,
    TRANSITION_SPLIT_HORIZ,
    TRANSITION_SPLIT_VERT,
    TRANSITION_QUARTERS
) = range(-1, TOTAL_TRANSITIONS)
