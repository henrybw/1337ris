#
# 1337ris -- traditionalmode.py
# Henry Weiss
#
# State class that handles the traditional game mode. Serves as the base
# class for all the other game modes, which is why it has a whole slew
# of seemingly "unnecessary" functions -- a lot of these will get over-
# rided by subclasses to tweak behavior. The same goes for a lot of the
# instance variables -- many are just assigned to a constant, and never
# change in *this* mode, but other subclasses might want to change them.
#
# Of course, this isn't a complete abstraction and isn't extremely custom-
# izable, but that's not really the point of this class either. It is
# supposed to be (I hope) a more balanced type of class that is extensible,
# but not too overgeneralized. Of course, it's generalized enough that
# the zillions of functions and members are pretty damn daunting, but at
# least it's better than copypasta code.
#

from .headers import *

#
# Constants
#

# How many pixels to the right the grid is
PIXEL_X_OFFSET = 80

# Scoring (increases with each level). Based on Tetris DX's scoring system.
SCORE_SINGLE = 40
SCORE_DOUBLE = 100
SCORE_TRIPLE = 300
SCORE_TETRIS = 1200
SCORE_BOMB = 10  # Per tetromino
SCORE_SPED_UP = 1  # Per lines moved when sped up
SCORE_DROP = 2  # Per lines moved when dropped

# Default rotation direction (counter-clockwise)
DEFAULT_ROTATION = 90

# For the explosions
EXPLOSION_FRAMES = 10

# Bomb/dynamite probability (bomb: 0-LOWER_BOUND, dynamite: LOWER_BOUND-UPPER_BOUND)
LOWER_BOUND = 15
UPPER_BOUND = 19

# Amount of tiles bombed/detonated that is equivalent to one line, scoring-wise
TILES_BOMBED_FOR_LINE = 20
TILES_DETONATED_FOR_LINE = 40  # Dynamite

# Collision detection flags, for block_will_collide()
DETECT_HORIZ = 1 << 0
DETECT_VERT = 1 << 1

# Block clear events (different actions that clear blocks)
(
    EVENT_NONE,
    EVENT_LINE_CLEAR,
    EVENT_BOMB,
    EVENT_DYNAMITE
) = range(4)

# Timing (ms)
INITIAL_DELAY = 850  # Also used for sliding
TILE_DELAY_INCREMENT = 40
BLOCKS_CLEARED_DELAY = 750
GAME_KEY_DELAY = 150
GAME_KEY_REPEAT = 30
DROP_DELAY = 350
SPEED_DELAY = 300

# Resources
TOTAL_BGS = 10
TOTAL_SONGS = 5

# Song IDs
(
    MORE_SOMETHING,
    MIST_IN_THE_NIGHT,
    EXPANSION,
    TECHNO_THINGY,
    SCRAZZERS_THEME
) = range(TOTAL_SONGS)

# Song names/order
SONG_NAMES = ["more something.ogg", "mist in the night.ogg", "expansion.ogg", "techno thingy.ogg", "scrazzers theme.ogg"]
SONG_ORDER = [MORE_SOMETHING, MIST_IN_THE_NIGHT, MIST_IN_THE_NIGHT, MIST_IN_THE_NIGHT, EXPANSION,
              EXPANSION, TECHNO_THINGY, SCRAZZERS_THEME, SCRAZZERS_THEME, SCRAZZERS_THEME]

# Font colors
GAME_FONT_COLOR = (255, 255, 255)
GAME_FONT_SHADOW_COLOR = (0, 0, 0)
GAME_OVER_COLOR = (205, 0, 0)
GAME_OVER_SHADOW_COLOR = (0, 0, 0)
PAUSE_FONT_COLOR = (255, 255, 255)

# Other stuff
LOCK_DELAY_MAX_ALPHA = 254  # Highest opacity during the "about to lock" warning

class TraditionalMode(GameState):
    total_resources = 9 + TOTAL_BGS + TOTAL_SONGS + EXPLOSION_FRAMES + len(TILES) * 2  # Accounts for both blocks and previews

    # Resources
    songs = [None] * TOTAL_SONGS
    bgs = [None] * TOTAL_BGS
    scorebar = None
    paused_overlay = None
    tiles = {}
    ghost_tiles = {}
    tile_previews = {}
    paused_snd = None
    move_snd = None
    rotate_snd = None
    lock_snd = None
    line_clear_snd = None
    tetris_snd = None
    bomb_snd = None
    levelup_snd = None
    game_font = None
    pause_font = None

    # Game variables
    tile_grid = []
    current = Tetromino()
    next = []
    level = 1
    paused = False
    game_over = False

    # Player info
    score = 0
    lines = 0
    total_time = 0

    # Keeps track of lines to clear and how they were cleared (mostly for kewl graphic effectz)
    clear_event = EVENT_NONE

    # For sliding at the last minute before a tetromino settles
    sliding = False

    # Timing stuff
    tile_delay = 0
    tile_delay_increment = 0
    min_tile_delay = 0
    slide_delay = 0
    sped_up_delay = 0  # For when the user holds down to speed up drops
    time_since_last_move = 0  # Keeps track of when to move the current tetromino down
    drop_delay = 0  # Prevents people from dropping inadvertantly due to fast key repeat
    speed_delay = 0  # Similar purpose as drop_delay

    #
    # Initialization routines
    #

    # Specifies the grid size. Useful for subclasses.
    def __init__(self, main, size=GRID_SIZE):
        self.size = GRID_SIZE
        self.width, self.height = self.size
        self.grid_y_offset = GRID_Y_OFFSET

        # Redefine this variable
        self.full_lines = [False] * self.height

        # And initialize the rest
        GameState.__init__(self, main)

    # Load game resources
    def load_resources(self):
        # Load static assets
        self.scorebar = self.load_resource(IMG_PATH + "scorebar.png", RES_TYPE_IMAGE)
        self.paused_overlay = self.load_resource(IMG_PATH + "pause overlay.png", RES_TYPE_IMAGE)
        self.paused_snd = self.load_resource(SND_PATH + "pause.ogg", RES_TYPE_SOUND)
        self.rotate_snd = self.load_resource(SND_PATH + "rotate.ogg", RES_TYPE_SOUND)
        self.move_snd = self.load_resource(SND_PATH + "move.ogg", RES_TYPE_SOUND)
        self.bomb_snd = self.load_resource(SND_PATH + "bomb.ogg", RES_TYPE_SOUND)
        self.lock_snd = self.load_resource(SND_PATH + "lock.ogg", RES_TYPE_SOUND)
        self.line_clear_snd = self.load_resource(SND_PATH + "line clear.ogg", RES_TYPE_SOUND)
        self.tetris_snd = self.load_resource(SND_PATH + "1337ris.ogg", RES_TYPE_SOUND)
        self.levelup_snd = self.load_resource(SND_PATH + "level complete.ogg", RES_TYPE_SOUND)

        # Load music
        for i in range(TOTAL_SONGS):
            if self.main.prefs_controller.get(STREAM_MUSIC):
                self.main.update_load_progress()  # Don't break the loading system -- it's expecting us to load a resource
            else:
                self.songs[i] = self.load_resource(MUSIC_PATH + SONG_NAMES[i], RES_TYPE_MUSIC)

        # Load tiles
        for key in TILES:
            self.tiles[key] = self.load_resource(IMG_PATH + "blocks/" + key.lower() + ".png", RES_TYPE_IMAGE)
            self.tile_previews[key] = self.load_resource(IMG_PATH + "blocks/" + key.lower() + " preview.png", RES_TYPE_IMAGE)

            # Create ghost tiles by halving each tile's alpha. Done per-pixel
            # if the image already has an alpha channel defined.
            if self.tiles[key].get_alpha() is None:
                self.ghost_tiles[key] = self.tiles[key].copy()
                self.ghost_tiles[key].set_alpha(127)
            else:
                ghost_img = self.tiles[key].copy()

                for x in range(ghost_img.get_width()):
                    for y in range(ghost_img.get_height()):
                        new_color = (ghost_img.get_at((x, y))[0], ghost_img.get_at((x, y))[1], ghost_img.get_at((x, y))[2], ghost_img.get_at((x, y))[3] / 2)
                        ghost_img.set_at((x, y), new_color)

                self.ghost_tiles[key] = ghost_img

        # Load explosion animation
        for i in range(EXPLOSION_FRAMES):
            self.tiles[str(i + 1)] = self.load_resource(IMG_PATH + "blocks/explode " + str(i + 1) + ".png", RES_TYPE_IMAGE)

        # Load backgrounds
        for i in range(TOTAL_BGS):
            self.bgs[i] = self.load_resource(IMG_PATH + "bgs/level" + str(i + 1) + ".png", RES_TYPE_IMAGE)

        # Initialize other objects
        self.game_font = Font(DEFAULT_FONT, 28)
        self.pause_font = Font(DEFAULT_FONT, 12)

        # Precompute the sin lookup table...which might take some time, so we'll call it a resource to be loaded
        self.build_lookup_table(255, BLOCKS_CLEARED_DELAY)
        self.main.update_load_progress()

    # Creates a sin lookup table, which is, in this game mode, used for the transparency values
    # of the flashing line effect when lines clear. The amplitude and period are just parts of
    # your rudimentary sinusoidal function (i.e. A and B in this equation): y = Asin(2pi/B * x)
    def build_lookup_table(self, amplitude, period):
        self.sin_lookup = []

        for i in range(period + 1):
            self.sin_lookup.append(round(abs(amplitude * sin((2 * pi / period) * i))))

    # New game -- initialize everything to starting values
    def start(self, userdata=None):
        self.level = 1
        self.score = 0
        self.lines = 0
        self.total_time = 0
        self.tile_delay = INITIAL_DELAY
        self.slide_delay = INITIAL_DELAY
        self.sped_up_delay = self.tile_delay / 10
        self.tile_delay_increment = TILE_DELAY_INCREMENT
        self.min_tile_delay = 0
        self.time_since_last_move = 0
        self.blocks_cleared_delay = 0
        self.clear_event = EVENT_NONE
        self.game_over = False
        self.paused = False

        # Clear the game grid
        self.tile_grid = []

        for x in range(self.width):
            col = [' '] * self.height
            self.tile_grid.append(col)

        # Reset the next tetromino stack
        self.next = []

        # Generate a new tetromino
        self.reset()

        # Start the music
        self.start_music()

        # Set key repeat to gameplay settings
        key.set_repeat(GAME_KEY_DELAY, GAME_KEY_REPEAT)

        # Clear any stray events (players will thank me later, XD)
        event.clear()

    # Plays the first song for the first level
    def start_music(self):
        if self.main.prefs_controller.get(STREAM_MUSIC):
            music.load(MUSIC_PATH + SONG_NAMES[0])
            music.play(-1)
        else:
            self.songs[0].play(-1)

    # Only overridden to return high score data to the next state
    def stop(self):
        # Don't forget to stop the current song
        if not self.main.prefs_controller.get(STREAM_MUSIC):
            self.songs[SONG_ORDER[(self.level - 1) % len(SONG_ORDER)]].stop()

        return (self.main.state, self.score, self.level, self.total_time)

    #
    # Gameplay routines
    #

    # Attempts to move a tetromino down, and will clear lines if so.
    # Returns true if the tetromino was able to move down.
    def move_down(self):
        # If a line is cleared, then the next piece should be delayed
        should_get_next_piece = False
        blocks = self.current.get_blocks()

        # If this is a bomb, check if we hit anything
        if self.current.type == 'B' and self.block_will_collide((self.current.center_x, self.current.center_y + 1)):
            # Insert bomb tile into the grid
            self.tile_grid[int(self.current.center_x)][int(self.current.center_y)] = 'B'

            # Bombs clear the line they hit and anything above it...
            # 20 tiles cleared make one line (defined as constant).
            self.explode_blocks(self.current.center_y, SCORE_BOMB, TILES_BOMBED_FOR_LINE)
            self.bomb_snd.play()

            # Update some stuff
            self.blocks_cleared_delay = BLOCKS_CLEARED_DELAY
            self.clear_event = EVENT_BOMB

            # We stopped moving, so...yeah
            return False

        # Otherwise, check if the currently moving tetromino collided with any blocks
        else:
            blocks = self.current.get_blocks()

            for block in blocks:
                if self.block_will_collide((block[0], block[1] + 1), DETECT_VERT):
                    # Add the tiles to the tile grid and get a new tetromino
                    for new_block in blocks:
                        self.tile_grid[int(new_block[0])][int(new_block[1])] = self.current.type

                    # Since the tetromino is now part of the grid, get a new tetromino right away
                    self.lock_snd.play()
                    should_get_next_piece = True
                    break

        # If a line clears, then this should return false as well
        return self.handle_line_clears(should_get_next_piece)

    # Handle what happens if lines clear
    def handle_line_clears(self, should_get_next_piece):
        lines_cleared = self.get_lines_cleared()

        if lines_cleared > 0:
            # Play a sound
            if lines_cleared >= 4:  # How can you get more than 4? Don't forget the other game modes...
                self.tetris_snd.play()
            else:
                self.line_clear_snd.play()

            self.blocks_cleared_delay = BLOCKS_CLEARED_DELAY  # Delay to flash a bit
            self.clear_event = EVENT_LINE_CLEAR

            return False  # Didn't move down!
        elif should_get_next_piece:
            # Get a new piece and check for game over
            self.reset()
            self.check_game_over()

            return False  # Didn't move down!

        # Otherwise, just move the piece down
        self.current.center_y += 1
        self.check_for_sliding()  # If a piece locks, we want it to delay more than usual

        return True

    # Returns the number of lines that are full
    def get_lines_cleared(self):
        lines_cleared = 0

        for y in range(self.grid_y_offset, self.height):
            line_filled = True

            for x in range(self.width):
                # Empty/exploding/dynamite tiles don't count
                if self.tile_grid[int(x)][int(y)] == ' ' or self.tile_grid[int(x)][int(y)] == 'D' or self.tile_grid[int(x)][int(y)] == '1':
                    line_filled = False

            # Otherwise...line cleared!
            if line_filled:
                lines_cleared += 1
                self.full_lines[y] = True

        return lines_cleared

    # Does what it says
    def check_game_over(self):
        if self.current.type != 'B':  # How can you get topout with a bomb?
            for block in self.current.get_blocks():
                if self.block_will_collide(block):
                    self.game_over = True  # :(
                    self.main.fadeout_sound()

    # Moves a tetromino in a certain direction horizontally. Returns whether or not the move was successful.
    def move_horiz(self, tetromino, dx):
        # If bomb or dynamite, just check to see if there is anything to the left of this tile.
        if ((tetromino.type == 'B' or tetromino.type == 'D') and not self.block_will_collide((tetromino.center_x + dx, tetromino.center_y))):
            self.move_snd.play()
            tetromino.center_x += dx

            return True

        # Otherwise, we'll have to make sure the hard way
        else:
            can_move = True

            # Collision detection, somewhat...
            for block in tetromino.get_blocks():
                if self.block_will_collide((block[0] + dx, block[1])):
                    can_move = False  # Out of bounds, or tile is in the way

            if can_move:
                self.move_snd.play()
                tetromino.center_x += dx

            self.check_for_sliding()
            return can_move

    # Moves a tetromino to the left...if it's legal. Returns whether or not the move was successful.
    def move_left(self):
        return self.move_horiz(self.current, -1)

    # Moves a tetromino to the right...if it's legal. Returns whether or not the move was successful.
    def move_right(self):
        return self.move_horiz(self.current, 1)

    # Rotates the current tetromino...if it's legal
    def rotate(self, angle):
        if self.clear_event == EVENT_NONE:
            self.rotate_snd.play()
            self.current.rotate(angle)

            # Check if we're out of bounds
            for block in self.current.get_blocks():
                if self.block_will_collide(block):
                    self.current.rotate(-angle)  # Revert the rotation!
                    break

    # Checks if a block at the given location will collide if moved in a certain direction.
    # You can exclude certain directions to check by passing a different set of flags
    # specifying which directions to check (by default, it checks both directions).
    def block_will_collide(self, location, flags=(DETECT_HORIZ | DETECT_VERT)):
        new_x, new_y = location
        return ((flags & DETECT_HORIZ and (new_x < 0 or new_x >= self.width)) or
                (flags & DETECT_VERT and (new_y < 0 or new_y >= self.height)) or
                self.tile_grid[int(new_x)][int(new_y)] != ' ')

    # Resets the current tetromino to the next tetromino in the current stack
    def reset(self):
        self.current.reset(self.get_next_type())

    # Returns a random tetromino ID char from the current stack of tetrominoes.
    # If there are no more tetrominoes left, a new stack is generated.
    # (Specify pop as False if you don't want to modify the stack.)
    def get_next_type(self, pop=True):
        # Generate a new tetromino list if there's none left
        if len(self.next) < 1:
            while len(self.next) < len(NORMAL_TILES):
                selector = randint(0, len(NORMAL_TILES) - 1)

                if not NORMAL_TILES[selector] in self.next:
                    self.next.append(NORMAL_TILES[selector])

            # Add the bomb or dynamite
            selector = randint(1, 100)

            # Reverse the lists after adding the bomb/dynamite
            # so it isn't popped off first.
            if selector > LOWER_BOUND and selector < UPPER_BOUND:
                self.next.append('D')
                self.next.reverse()
            elif selector < LOWER_BOUND:
                self.next.append('B')
                self.next.reverse()

        if pop:
            # This means we're in a reset, so ignore the input for a bit so the player
            # doesn't accidentally drop too fast.
            self.speed_delay = SPEED_DELAY

            # Ignore input for a short instant to prevent inadvertant drops (players
            # will thank me later, XD), unless there's a line clear.
            if self.clear_event == EVENT_NONE:
                self.drop_delay = DROP_DELAY

            return self.next.pop()
        else:
            return self.next[len(self.next) - 1]

    # Finalization method to clear blocks from the screen after line(s) clears.
    def clear_lines(self):
        self.blocks_cleared_delay = 0

        # Update the grid and take care of scoring
        lines_cleared = self.adjust_full_lines()
        self.clear_detonated_blocks()
        self.update_score(lines_cleared)

        # Update line count and possibly level too
        self.update_lines(lines_cleared)

        # Get the next piece only if necessary
        if self.clear_event != EVENT_NONE and self.clear_event != EVENT_DYNAMITE:
            self.reset()

    # Handles scoring for lines cleared.
    def update_score(self, lines_cleared):
        if lines_cleared == 1:
            self.score += SCORE_SINGLE * self.level
        elif lines_cleared == 2:
            self.score += SCORE_DOUBLE * self.level
        elif lines_cleared == 3:
            self.score += SCORE_TRIPLE * self.level
        elif lines_cleared >= 4:
            self.score += SCORE_TETRIS * self.level

    # Updates total lines cleared and initiates level clearing
    def update_lines(self, lines_cleared):
        self.lines += lines_cleared

        if int((self.lines / 10) + 1) > self.level:
            # Woo, level cleared
            self.level_clear()

    # Moves all full ines up a notch. Returns total number of lines cleared
    def adjust_full_lines(self):
        lines_cleared = 0

        for i in range(self.height):
            if self.full_lines[i]:
                lines_cleared += 1
                self.full_lines[i] = False

                # Move down each line before it
                for x in range(self.width):
                    for y in range(i, 0, -1):
                        self.tile_grid[int(x)][int(y)] = self.tile_grid[int(x)][int(y - 1)]

        return lines_cleared

    # Goes to the next level
    def level_clear(self):
        self.levelup_snd.play()
        self.level += 1
        self.tile_delay = max(self.tile_delay - self.tile_delay_increment, self.min_tile_delay)
        self.sped_up_delay = self.tile_delay / 10

        # Check if we should start a different song
        if SONG_ORDER[(self.level - 1) % len(SONG_ORDER)] != SONG_ORDER[(self.level - 2) % len(SONG_ORDER)]:
            old_id = SONG_ORDER[(self.level - 2) % len(SONG_ORDER)]
            new_id = SONG_ORDER[(self.level - 1) % len(SONG_ORDER)]

            # Swap songs
            if self.main.prefs_controller.get(STREAM_MUSIC):
                music.stop()
                music.load(MUSIC_PATH + SONG_NAMES[new_id])
                music.play(-1)
            else:
                self.songs[old_id].stop()
                self.songs[new_id].play(-1)

    # Detonates the top-left most dynamite tile and, with it,
    # the line it is on and everything above it.
    def detonate(self):
        for y in range(self.grid_y_offset, self.height):
            for x in range(self.width):
                # Remove dynamite tiles and blow up stuff
                if self.tile_grid[int(x)][int(y)] == 'D':
                    # Dynamite clears the line its on and anything above it...
                    # 40 tiles cleared make one line (defined as constant).
                    self.explode_blocks(y, SCORE_BOMB, TILES_DETONATED_FOR_LINE)
                    self.bomb_snd.play()

                    # Update some stuff and bail out, since we've detonated already
                    self.blocks_cleared_delay = BLOCKS_CLEARED_DELAY
                    self.clear_event = EVENT_DYNAMITE

                    return

    # Makes all blocks go boom from the top of the screen to the specified y location.
    def explode_blocks(self, y_offset, score_per_block, blocks_per_line):
        blocks_cleared = 0

        for y in range(y_offset, 0, -1):
            for x in range(self.width):
                if self.tile_grid[int(x)][int(y)] != ' ':
                    # Award some points
                    self.score += score_per_block * self.level

                    # And maybe a line too...
                    blocks_cleared += 1

                    if blocks_cleared > blocks_per_line:
                        self.lines += 1
                        blocks_cleared = 0

                    self.tile_grid[int(x)][int(y)] = '1'  # Make affected tile explode

    # Kind of the "clean up" version of the above
    def clear_detonated_blocks(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.is_exploding_block(self.tile_grid[int(x)][int(y)]):
                    self.tile_grid[int(x)][int(y)] = ' '

    # Checks to see if we are currently sliding or not
    def check_for_sliding(self):
        if key.get_pressed()[self.main.prefs_controller.get(DROP_KEY)] or key.get_pressed()[self.main.prefs_controller.get(SPEEDUP_KEY)]:
            self.sliding = False
            return

        for block in self.current.get_blocks():
            # Something under this tetromino?
            if self.block_will_collide((block[0], block[1] + 1)):
                self.sliding = True
                return

        # Nope
        self.sliding = False

    # Checks if a block is an explosion frame or not
    def is_exploding_block(self, type):
        try:
            img = int(type)
            return True
        except ValueError:
            return False

    #
    # Game state routines (updating, input handling)
    #

    # Update the game state based on elapsed time
    def update(self, elapsed_time):
        # Should we really update?
        if self.paused or self.game_over:
            return

        # Update the clock, regardless of any clear events
        self.total_time += elapsed_time

        # If we're delaying, then we shouldn't update the tetromino
        if self.handle_delays(elapsed_time):
            self.time_since_last_move += elapsed_time
            self.update_tetromino(elapsed_time)

    # Takes care of any delays that are in effect (delay before being able to
    # drop, delay while line(s) are clearing, etc). Returns false whenever an
    # asynchronous delay is in effect (i.e. no updating should be done); other-
    # wise, this return true.
    def handle_delays(self, elapsed_time):
        # Check if there's a drop delay in effect
        if self.drop_delay > 0:
            self.drop_delay -= elapsed_time
            event.clear()  # Clear any stray events, just in case
            return False

        # Check if there's a speedup delay in effect
        if self.speed_delay > 0:
            self.speed_delay -= elapsed_time

        # Check if we are in the middle of clearing a line
        if self.blocks_cleared_delay > 0:
            self.blocks_cleared_delay -= elapsed_time

            if self.blocks_cleared_delay <= 0:
                self.clear_lines()
                self.clear_event = EVENT_NONE  # Reset the event
            else:
                # Check if we should update any explosions going on
                for x in range(self.width):
                    for y in range(self.height):
                        if self.is_exploding_block(self.tile_grid[int(x)][int(y)]):
                            if self.blocks_cleared_delay <= 0:
                                self.tile_grid[int(x)][int(y)] = ' '
                            else:
                                frame = EXPLOSION_FRAMES - int(self.blocks_cleared_delay / (BLOCKS_CLEARED_DELAY / EXPLOSION_FRAMES))
                                self.tile_grid[int(x)][int(y)] = str(frame)

                return False

        return True  # Nothing stopping us now

    # Moves the tetromino if the right amount of time has passed
    def update_tetromino(self, elapsed_time):
        # Use a different delay threshold depending on the situation
        speedup = key.get_pressed()[self.main.prefs_controller.get(SPEEDUP_KEY)] and self.speed_delay <= 0

        if speedup:
            delay_threshold = self.sped_up_delay
        elif self.sliding:
            delay_threshold = self.slide_delay
        else:
            delay_threshold = self.tile_delay

        # Is it time to move down?
        if self.time_since_last_move > delay_threshold:
            self.sliding = False  # Not sliding anymore, since we're moving down

            self.move_down()
            self.time_since_last_move = 0

            if speedup:
                self.score += SCORE_SPED_UP

    # Handles key input
    def key_down(self, keycode, unicode):
        # Where's the any key? I can't find the any key!!! OHNOES.
        if self.game_over:
            self.main.sound_controller.get_sound(SND_PATH + "menu/choose.ogg").play()
            self.main.state = STATE_HIGH_SCORES
            return

        # Check for pausing
        if keycode == self.main.prefs_controller.get(PAUSE_KEY):
            self.toggle_paused()

        # Quit?
        if self.paused and keycode == self.main.prefs_controller.get(QUIT_KEY):
            self.main.sound_controller.get_sound(SND_PATH + "menu/choose.ogg").play()
            self.main.state = STATE_MAIN_MENU

        # The rest...
        if not self.paused and self.clear_event == EVENT_NONE:
            self.handle_game_input(keycode)

    # Specific handler for actual gameplay
    def handle_game_input(self, keycode):
        # Any key will reset the delay threshold when sliding
        if self.sliding:
            collided = False

            for block in self.current.get_blocks():
                if self.block_will_collide((block[0] - 1, block[1])) or self.block_will_collide((block[0] + 1, block[1])):
                    collided = True

            if not collided:
                self.time_since_last_move = 0

        # Check for movement and stuff
        if keycode == self.main.prefs_controller.get(MOVE_LEFT_KEY):
            if self.move_left() and self.sliding:
                self.time_since_last_move = 0  # Rotating extends the sliding period

        elif keycode == self.main.prefs_controller.get(MOVE_RIGHT_KEY):
            if self.move_right() and self.sliding:
                self.time_since_last_move = 0  # Rotating extends the sliding period

        elif keycode == self.main.prefs_controller.get(ROTATE_RIGHT_KEY) or keycode == self.main.prefs_controller.get(ROTATE_LEFT_KEY):
            if keycode == self.main.prefs_controller.get(ROTATE_RIGHT_KEY):
                self.rotate(DEFAULT_ROTATION)
            else:
                self.rotate(-DEFAULT_ROTATION)

            if self.sliding:
                self.time_since_last_move = 0  # Rotating extends the sliding period

        elif keycode == self.main.prefs_controller.get(DROP_KEY) and self.drop_delay <= 0:
            # Moves the tetromino down until it settles into place (adding points for speedy drop).
            while self.move_down():
                self.score += SCORE_DROP

        elif keycode == self.main.prefs_controller.get(DETONATE_KEY):
            self.detonate()

        # If we got set to game over, then don't check for sliding
        if not self.game_over:
            self.check_for_sliding()

    # Toggles paused state and takes care of music/sound pausing
    def toggle_paused(self):
        # Do a screen transition
        self.paused = not self.paused
        self.main.transition_screen(TRANSITION_CROSSFADE, self.draw(None, False))

        # Pause/unpause the music as required
        music_ref = None

        if self.main.prefs_controller.get(STREAM_MUSIC):
            music_ref = music
        else:
            music_ref = mixer

        if self.paused:
            music_ref.pause()
        else:
            music_ref.unpause()

        # Play the paused sound
        self.paused_snd.play()

        # Clear any stray events (players will thank me later, XD)
        event.clear()

        # Toggle the key repeat between menu/game modes
        if self.paused:
            key.set_repeat()  # Disable for pause menu
        else:
            key.set_repeat(GAME_KEY_DELAY, GAME_KEY_REPEAT)

    #
    # Drawing routines
    #

    # Renders the scene
    def draw_scene(self, mode, surface):
        self.draw_environment(surface)
        self.draw_blocks(surface)

        # Draw the game over screen if necessary
        if self.game_over:
            self.draw_gameover_overlay(surface)

        # Draw the paused overlay if paused
        if self.paused:
            self.draw_paused_overlay(surface)

    # Draws the stuff that's not on the playing field
    def draw_environment(self, surface):
        # Draw the "environment" first -- bg and scorebar
        if self.main.prefs_controller.get(DRAW_BG):
            surface.blit(self.bgs[(self.level - 1) % TOTAL_BGS], (0, 0))
        else:
            surface.fill((0, 0, 0))

        surface.blit(self.scorebar, (0, 0))

        # Now draw the text stuff (current level, score, etc.)
        surface.blit(self.game_font.render(str(self.level), True, GAME_FONT_COLOR), (422, 369))
        surface.blit(self.game_font.render(str(self.score), True, GAME_FONT_COLOR), (342, 302))
        surface.blit(self.game_font.render(str(self.lines), True, GAME_FONT_COLOR), (437, 214))
        surface.blit(self.game_font.render(self.main.time_to_str(self.total_time), True, GAME_FONT_COLOR), (435, 132))

        self.draw_preview(surface)

    # Show the preview if we're allowed
    def draw_preview(self, surface):
        if self.main.prefs_controller.get(SHOW_PREVIEW):
            surface.blit(self.tile_previews[self.get_next_type(False)], (337, 135))

    # Draws all blocks on the screen
    def draw_blocks(self, surface):
        self.draw_current_tetromino(surface)
        self.draw_field_blocks(surface)

    # Draw the currently moving tetromino if the lines aren't flashing
    def draw_current_tetromino(self, surface):
        if self.clear_event != EVENT_LINE_CLEAR and self.clear_event != EVENT_BOMB:
            for block in self.current.get_blocks():
                self.draw_block(surface, self.current.type, block)

            # Draw the ghost piece if necessary
            if self.main.prefs_controller.get(DRAW_GHOST):
                self.draw_ghost_piece(surface)

            # And perhaps a "visual warning"
            if self.should_draw_warning():
                for block in self.current.get_blocks():
                    self.draw_block_overlay(surface, block)

    # Draw the ghost version of the tetromino
    def draw_ghost_piece(self, surface):
        y_offset = 0
        save_y = self.current.center_y

        # Move the tetromino down until it collides
        collided = False

        while not collided:
            for block in self.current.get_blocks():
                if self.block_will_collide(block):
                    collided = True

            if not collided:
                self.current.center_y += 1

        # Calculate the offset and restore the old y
        y_offset = self.current.center_y - save_y - 1
        self.current.center_y = save_y

        # Draw the blocks
        if y_offset > 0:
            for block in self.current.get_blocks():
                self.draw_block(surface, self.current.type, (block[0], block[1] + y_offset), True)

    # Determines if we should draw an "about to lock!" visual warning
    def should_draw_warning(self):
        draw_warning = self.sliding

        if not draw_warning:
            # One more check...
            for block in self.current.get_blocks():
                if self.block_will_collide((block[0], block[1] + 1), DETECT_VERT):
                    draw_warning = True

        return draw_warning

    # Draws the rest of the blocks on the playing field
    def draw_field_blocks(self, surface):
        # Draw the other blocks
        for y in range(self.grid_y_offset, self.height):
            for x in range(self.width):
                if self.tile_grid[int(x)][int(y)] != ' ':
                    self.draw_block(surface, self.tile_grid[int(x)][int(y)], (x, y))

            # Flash the lines we're clearing
            if self.full_lines[y]:
                self.draw_flashing_line(surface, y, self.sin_lookup[self.blocks_cleared_delay])

    # Draws a white, translucent rect over a line to make it flash
    def draw_flashing_line(self, surface, y, transparency):
        # Create a white surface to cover the line
        white = Surface((BLOCK_SIZE[0] * self.width, BLOCK_SIZE[1]))
        white.fill((255, 255, 255))

        # Set its transparency based on where we are in the blink and then blit it.
        white.set_alpha(transparency)
        surface.blit(white, (PIXEL_X_OFFSET, (y - self.grid_y_offset) * BLOCK_SIZE[0]))

    # Draws a single block at a given grid location
    def draw_block(self, surface, type, grid_loc, ghost=False):
        if ghost:
            block_img = self.ghost_tiles[type]
        else:
            block_img = self.tiles[type]

        # Calculate pixel coordinates (with a pixel offset on the x-axis)
        x = PIXEL_X_OFFSET + grid_loc[0] * block_img.get_width()
        y = (grid_loc[1] - self.grid_y_offset) * block_img.get_height()

        # Draw it
        surface.blit(block_img, (x, y))

    # Draws a little fade overlay when the piece is sliding
    def draw_block_overlay(self, surface, location):
        # Create a white surface to cover the block
        overlay = Surface(BLOCK_SIZE)
        overlay.fill((255, 255, 255))

        # Set its transparency based on how close we are to getting a next piece and then blit it.
        overlay.set_alpha(LOCK_DELAY_MAX_ALPHA * (float(self.time_since_last_move) / self.slide_delay))
        surface.blit(overlay, (PIXEL_X_OFFSET + location[0] * BLOCK_SIZE[0], (location[1] - self.grid_y_offset) * BLOCK_SIZE[0]))

    # Does what it says. ;)
    def draw_gameover_overlay(self, surface):
        self.game_font.set_bold(True)
        surface.blit(self.game_font.render("GAME OVER", True, GAME_OVER_SHADOW_COLOR), (106, 193))  # Shadow
        surface.blit(self.game_font.render("GAME OVER", True, GAME_OVER_COLOR), (105, 192))

        self.game_font.set_bold(False)
        surface.blit(self.game_font.render("Press any key", True, GAME_FONT_SHADOW_COLOR), (106, 233))  # Shadow
        surface.blit(self.game_font.render("Press any key", True, GAME_FONT_COLOR), (105, 232))
        surface.blit(self.game_font.render("to continue", True, GAME_FONT_SHADOW_COLOR), (118, 263))  # Shadow
        surface.blit(self.game_font.render("to continue", True, GAME_FONT_COLOR), (117, 262))

    # Also does what it says.
    def draw_paused_overlay(self, surface):
        surface.blit(self.paused_overlay, (0, 0))

        # Draw the keys to quit/resume
        surface.blit(self.pause_font.render(key.name(self.main.prefs_controller.get(PAUSE_KEY)), True, PAUSE_FONT_COLOR), (132, 240))
        surface.blit(self.pause_font.render(key.name(self.main.prefs_controller.get(QUIT_KEY)), True, PAUSE_FONT_COLOR), (132, 270))
