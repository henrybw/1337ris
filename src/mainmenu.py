#
# 1337ris -- mainmenu.py
# Henry Weiss
#
# State class that handles the main menu.
#

from headers import *

#
# Constants
#

MENU_FRAMES = 10
FRAME_DELAY = 100  # ms

INITIAL_KEY_DELAY = 500
KEY_REPEAT_DELAY = 30

# Info for each table column
HIGH_SCORES_TABLE = ['', 'Name', 'Score', 'Level', 'Time']
HIGH_SCORES_TABLE_OFFSETS = [10, 40, 385, 485, 560]

INITIAL_CREDITS_OFFSET = SCREEN_HEIGHT
CREDITS_SPEED = 0.0165
SPEED_UP = 7

COMMON_SETTINGS_OFFSET = 355
SETTINGS_X_OFFSET = 50  # Offsets for the settings items
SETTINGS_Y_OFFSET = 70

HELP_PATH = "data/help/page "
PIECE_PADDING = 15
HELP_PAGE_LOC = (25, 15)
HELP_X_OFFSET = 25
HELP_Y_OFFSET = 70
HELP_Y_NOTE_OFFSET = 450  # The little explanatory text ("press Esc to...", etc.)

DEFAULT_TEXT_COLOR = (255, 200, 0)
BRIGHT_TEXT_COLOR = (255, 255, 0)
WARNING_TEXT_COLOR = (255, 255, 255)

# What part of the menu are we in?
(
    MODE_MAIN_MENU,
    MODE_SETTINGS,
    MODE_KEY_CONFIG,
    MODE_CREDITS,
    MODE_HIGH_SCORES,
    MODE_ABOUT,
    MODE_HELP
) = range(7)

# Menu items
MENU_ITEMS = 10

(
    ITEM_TRADITIONAL,
    ITEM_CROSS_CUT,
    ITEM_CONVERGENCE,
    ITEM_PSYCHEDELIC,
    ITEM_SETTINGS,
    ITEM_HIGH_SCORES,
    ITEM_CREDITS,
    ITEM_ABOUT,
    ITEM_HELP,
    ITEM_QUIT
) = range(MENU_ITEMS)

# Settings
SETTINGS_ITEMS = 12
KEY_CONFIG_ITEMS = 13

(
    SETTING_MUSIC_VOL,
    SETTING_SOUND_VOL,
    SETTING_FULLSCREEN,
    SETTING_FRAMERATE,
    SETTING_STREAM,
    SETTING_BG,
    SETTING_PREVIEW,
    SETTING_GHOST,
    SETTING_KEYS,
    SETTING_RESET,
    SETTING_DONTSAVE,
    SETTING_SAVE
) = range(SETTINGS_ITEMS)

(
    KEY_LEFT,
    KEY_RIGHT,
    KEY_ROTATE_RIGHT,
    KEY_ROTATE_LEFT,
    KEY_SPEEDUP,
    KEY_DROP,
    KEY_DETONATE,
    KEY_PAUSE,
    KEY_QUIT,
    KEY_GENERAL,
    KEY_RESET,
    KEY_DONTSAVE,
    KEY_SAVE
) = range(KEY_CONFIG_ITEMS)

class MainMenu(GameState):
    total_resources = 7 + MENU_FRAMES + MENU_ITEMS

    # Resources
    menu_anim = [None] * MENU_FRAMES
    menu_items = [None] * MENU_ITEMS
    pointer = None
    credits_bg = None
    credits_header = None

    # Sounds and music
    music = None
    select_snd = None
    choose_snd = None
    back_snd = None
    beep_snd = None
    streaming = False

    # Menu settings
    mode = MODE_MAIN_MENU
    current_bg = 0
    next_frame_wait = FRAME_DELAY
    selected = 0
    selected_setting = 0
    choosing_key = False  # For key config
    current_score_page = 0  # For high scores
    current_scores = []
    confirm_score_clear = False
    help_page = 0
    total_help_pages = 0

    # Stuff for specific modes
    text_font = None
    subtitle_font = None
    header_font = None

    # Intercepts game mode changes to do a screen transition
    def __setattr__(self, attr, value):
        if attr == "mode":
            # Don't transition unless we're transitioning from/to the main menu
            if self.mode == MODE_MAIN_MENU or value == MODE_MAIN_MENU:
                # Initiate transition
                self.main.transition_screen(TRANSITION_RANDOM, self.draw(value, False))

        # Normal behavior
        self.__dict__[attr] = value

    # Loads resources
    def load_resources(self):
        # Menu animation
        for i in range(0, MENU_FRAMES):
            self.menu_anim[i] = self.load_resource(IMG_PATH + "menu/bgs/menu" + str(i + 1) + ".png", RES_TYPE_IMAGE)

        # Menu items
        for i in range(0, MENU_ITEMS):
            self.menu_items[i] = self.load_resource(IMG_PATH + "menu/items/item" + str(i + 1) + ".png", RES_TYPE_IMAGE)

        # The rest of the assets
        self.credits_bg = self.load_resource(IMG_PATH + "menu/credits.png", RES_TYPE_IMAGE)
        self.credits_header = self.load_resource(IMG_PATH + "menu/credits header.png", RES_TYPE_IMAGE)
        self.pointer = self.load_resource(IMG_PATH + "menu/items/pointer.png", RES_TYPE_IMAGE)
        self.select_snd = self.load_resource(SND_PATH + "menu/select.ogg", RES_TYPE_SOUND)
        self.choose_snd = self.load_resource(SND_PATH + "menu/choose.ogg", RES_TYPE_SOUND)
        self.back_snd = self.load_resource(SND_PATH + "menu/back.ogg", RES_TYPE_SOUND)
        self.beep_snd = self.load_resource(SND_PATH + "menu/beep.ogg", RES_TYPE_SOUND)

        # Music loading depends on whether we stream or not
        if self.main.prefs_controller.get(STREAM_MUSIC):
            self.main.update_load_progress()  # Don't break the loading system -- it's expecting us to load a resource
            self.streaming = True
        else:
            self.music = self.load_resource(MUSIC_PATH + "music1.ogg", RES_TYPE_MUSIC)
            self.streaming = False

        # Fonts
        self.text_font = Font(DEFAULT_FONT, 15)
        self.subtitle_font = Font(DEFAULT_FONT, 11)
        self.header_font = Font(DEFAULT_FONT, 34)
        self.help_font = Font(DEFAULT_FONT, 13)

        # No comment. You don't need to know. Nothing to see here.
        self.wut = False

    # Starts music playing and resets the menu animation
    def start(self, userdata=None):
        if self.main.prefs_controller.get(STREAM_MUSIC):
            music.load(MUSIC_PATH + "music1.ogg")
            music.play(-1)
        else:
            self.music.play(-1)

        self.current_bg = 0
        self.next_frame_wait = 0

        # Set key repeat to default settings
        key.set_repeat(INITIAL_KEY_DELAY, KEY_REPEAT_DELAY)

    # Stops the current menu music (uses the streaming variable instead of
    # the preference because this can occur in the middle of a transition
    # from streaming to non-streaming music, making the preference value
    # temporarily misleading).
    def stop(self):
        if self.streaming:
            music.stop()
        else:
            self.music.stop()

    # Updates the menu animation
    def update(self, elapsed_time):
        self.next_frame_wait -= elapsed_time

        # Check if we should go to the next frame
        if self.next_frame_wait <= 0:
            self.next_frame_wait = FRAME_DELAY
            self.current_bg += 1

            # Keep it within range
            self.current_bg = self.current_bg % len(self.menu_anim)

        # Update the scrolling credits
        if self.mode == MODE_CREDITS:
            speed = CREDITS_SPEED

            # Speed up?
            if key.get_pressed()[K_DOWN]:
                speed *= SPEED_UP

                # More?
                if key.get_mods() & KMOD_SHIFT:
                    speed *= 2

            # Or reverse?
            elif key.get_pressed()[K_UP]:
                speed *= -SPEED_UP

                # More?
                if key.get_mods() & KMOD_SHIFT:
                    speed *= 2

            # Or not at all?
            if key.get_mods() & KMOD_ALT:
                speed = 0

            # Update
            self.credits_offset -= elapsed_time * speed

            # Sanity check
            if self.credits_offset > INITIAL_CREDITS_OFFSET:
                self.credits_offset = INITIAL_CREDITS_OFFSET

            # Prevents credits from flying off-screen
            lower_bound = INITIAL_CREDITS_OFFSET - (len(file("data/credits.txt").readlines()) + 2) * self.text_font.get_linesize()

            if self.credits_offset < lower_bound:
                self.credits_offset = lower_bound

        # These aren't the lines you're looking for. Move along, move along...
        if self.mode == MODE_ABOUT:
            if key.get_pressed()[K_z] and key.get_mods() & KMOD_ALT:
                self.wut = True
            else:
                self.wut = False

    # Reloads a page of high scores.
    def refresh_high_score_page(self):
        self.current_scores = self.main.read_high_scores(HIGH_SCORE_FILES[self.current_score_page])
        self.current_scores.sort()
        self.current_scores.reverse()

        # Go through and swap any entries broken by time (since lower times should prevail)
        for i in range(len(self.current_scores) - 1):
            if (self.current_scores[i][ENTRY_SCORE] == self.current_scores[i + 1][ENTRY_SCORE] and
              self.current_scores[i][ENTRY_LEVEL] == self.current_scores[i + 1][ENTRY_LEVEL]):
                  temp = self.current_scores[i]
                  self.current_scores[i] = self.current_scores[i + 1]
                  self.current_scores[i + 1] = temp

        # If there aren't enough scores, pad the list
        if len(self.current_scores) < MAX_ENTRIES:
            for i in range(MAX_ENTRIES - len(self.current_scores)):
                self.current_scores.append(BLANK_ENTRY)

    # Handles key input, mostly for interface stuff
    def key_down(self, keycode, unicode):
        if self.mode == MODE_MAIN_MENU:
            self.handle_main_menu_input(keycode)

        elif self.mode == MODE_SETTINGS or self.mode == MODE_KEY_CONFIG:
            # Handle the "common items" that both modes have
            self.handle_common_settings_input(keycode)

            # Branch to their specific input handlers, but make
            # sure that they didn't bail out already.
            if self.mode == MODE_SETTINGS:
                self.handle_settings_input(keycode)
            elif self.mode == MODE_KEY_CONFIG:
                self.handle_key_config_input(keycode)

        elif self.mode >= MODE_CREDITS and self.mode <= MODE_ABOUT:
            # Just return to the main menu if the right key is pressed
            if not self.confirm_score_clear and (keycode == K_SPACE or keycode == K_ESCAPE or keycode == K_RETURN):
                self.back_snd.play()
                self.mode = MODE_MAIN_MENU

            # High scores has a little more, so we'll let them take care of that
            if self.mode == MODE_HIGH_SCORES:
                self.handle_high_scores_input(keycode)

        elif self.mode == MODE_HELP:
            self.handle_help_input(keycode)

    # Handles key input for the main menu
    def handle_main_menu_input(self, keycode):
        # Select a menu item?
        if keycode == K_SPACE or keycode == K_RETURN:
            self.choose_snd.play()

            # And then take action
            if self.selected == ITEM_TRADITIONAL:
                self.main.state = STATE_TRADITIONAL

            elif self.selected == ITEM_CROSS_CUT:
                self.main.state = STATE_CROSS_CUT

            elif self.selected == ITEM_CONVERGENCE:
                self.main.state = STATE_CONVERGENCE

            elif self.selected == ITEM_PSYCHEDELIC:
                self.main.state = STATE_PSYCHEDELIC

            elif self.selected == ITEM_SETTINGS:
                self.selected_setting = 0
                self.mode = MODE_SETTINGS

            elif self.selected == ITEM_HIGH_SCORES:
                # Read in the current high scores
                self.current_score_page = 0
                self.refresh_high_score_page()

                self.mode = MODE_HIGH_SCORES

            elif self.selected == ITEM_CREDITS:
                self.credits_offset = INITIAL_CREDITS_OFFSET

                self.mode = MODE_CREDITS

            elif self.selected == ITEM_ABOUT:
                self.mode = MODE_ABOUT

            elif self.selected == ITEM_HELP:
                self.help_page = 0

                # Determine how many help pages there are
                self.total_help_pages = 0

                while os.access(HELP_PATH + str(self.total_help_pages + 1) + ".txt", os.F_OK):
                    self.total_help_pages += 1

                self.mode = MODE_HELP

            elif self.selected == ITEM_QUIT:
                self.main.fadeout_sound(50)  # Short, but at least we can hear a blip of the choose sound
                self.main.quit()

        # Move the cursor
        if keycode == K_UP:
            self.selected -= 1
            self.select_snd.play()

        if keycode == K_DOWN:
            self.selected += 1
            self.select_snd.play()

        # Enforce proper bounds
        self.selected %= len(self.menu_items)

    # Handles common menu items between both forms of settings
    def handle_common_settings_input(self, keycode):
        if self.choosing_key:
            return  # Don't interfere with this process!

        # If they press Esc, highlight Don't Save
        if keycode == K_ESCAPE:
            if self.mode == MODE_SETTINGS:
                self.selected_setting = SETTING_DONTSAVE
            else:
                self.selected_setting = KEY_DONTSAVE

            self.select_snd.play()

        # Cancel and bail out
        elif keycode == K_SPACE or keycode == K_RETURN:
            if ((self.mode == MODE_SETTINGS and self.selected_setting == SETTING_DONTSAVE) or
                (self.mode == MODE_KEY_CONFIG and self.selected_setting == KEY_DONTSAVE)):
                # Clear any intermediate changes made
                self.main.prefs_controller.clear()
                self.main.prefs_controller.load()

                # Make changes take effect
                self.main.sound_controller.music_volume = self.main.prefs_controller.get(MUSIC_VOLUME)
                self.main.sound_controller.sound_volume = self.main.prefs_controller.get(SOUND_VOLUME)

                self.back_snd.play()
                self.mode = MODE_MAIN_MENU
            # Save it?
            elif ((self.mode == MODE_SETTINGS and self.selected_setting == SETTING_SAVE) or
                (self.mode == MODE_KEY_CONFIG and self.selected_setting == KEY_SAVE)):
                self.main.prefs_controller.save()
                self.choose_snd.play()

                # If we aren't streaming anymore, we might have to load the sounds
                self.mode = MODE_MAIN_MENU
                self.update_music()

            # Reset?
            elif ((self.mode == MODE_SETTINGS and self.selected_setting == SETTING_RESET) or
                (self.mode == MODE_KEY_CONFIG and self.selected_setting == KEY_RESET)):
                self.main.prefs_controller.reset()
                self.choose_snd.play()

            # Go to key config?
            elif self.selected_setting == SETTING_KEYS and self.mode == MODE_SETTINGS:
                self.choose_snd.play()
                self.mode = MODE_KEY_CONFIG
                self.selected_setting = KEY_GENERAL

            # Go to general settings?
            elif self.selected_setting == KEY_GENERAL and self.mode == MODE_KEY_CONFIG:
                self.choose_snd.play()
                self.mode = MODE_SETTINGS
                self.selected_setting = SETTING_KEYS

            # If the volumes were changed, make them take effect
            self.main.sound_controller.music_volume = self.main.prefs_controller.get(MUSIC_VOLUME)
            self.main.sound_controller.sound_volume = self.main.prefs_controller.get(SOUND_VOLUME)

        # Move the cursor
        if keycode == K_UP:
            self.selected_setting -= 1
            self.select_snd.play()

        if keycode == K_DOWN:
            self.selected_setting += 1
            self.select_snd.play()

        # Enforce proper bounds
        if self.mode == MODE_SETTINGS:
            self.selected_setting %= SETTINGS_ITEMS
        else:
            self.selected_setting %= KEY_CONFIG_ITEMS

    # Handles key input for the normal settings menu
    def handle_settings_input(self, keycode):
        # Change the volume levels?
        if self.selected_setting == SETTING_MUSIC_VOL or self.selected_setting == SETTING_SOUND_VOL:
            if self.selected_setting == SETTING_MUSIC_VOL:
                key = MUSIC_VOLUME
            else:
                key = SOUND_VOLUME

            if keycode == K_LEFT:
                self.select_snd.play()
                self.main.prefs_controller.set(key, max(self.main.prefs_controller.get(key) - 0.01, 0))
            elif keycode == K_RIGHT:
                self.select_snd.play()
                self.main.prefs_controller.set(key, min(self.main.prefs_controller.get(key) + 0.01, 1))

            # Take effect
            self.main.sound_controller.music_volume = self.main.prefs_controller.get(MUSIC_VOLUME)
            self.main.sound_controller.sound_volume = self.main.prefs_controller.get(SOUND_VOLUME)

        # Toggle the boolean preferences?
        elif (self.selected_setting >= SETTING_FULLSCREEN and self.selected_setting <= SETTING_GHOST and
          (keycode == K_SPACE or keycode == K_RETURN or keycode == K_LEFT or keycode == K_RIGHT)):
            self.select_snd.play()

            if self.selected_setting == SETTING_FULLSCREEN:
                self.main.prefs_controller.set(RUN_FULLSCREEN, not self.main.prefs_controller.get(RUN_FULLSCREEN))
            elif self.selected_setting == SETTING_FRAMERATE:
                self.main.prefs_controller.set(DRAW_FRAMERATE, not self.main.prefs_controller.get(DRAW_FRAMERATE))
            elif self.selected_setting == SETTING_STREAM:
                self.main.prefs_controller.set(STREAM_MUSIC, not self.main.prefs_controller.get(STREAM_MUSIC))
            elif self.selected_setting == SETTING_BG:
                self.main.prefs_controller.set(DRAW_BG, not self.main.prefs_controller.get(DRAW_BG))
            elif self.selected_setting == SETTING_PREVIEW:
                self.main.prefs_controller.set(SHOW_PREVIEW, not self.main.prefs_controller.get(SHOW_PREVIEW))
            elif self.selected_setting == SETTING_GHOST:
                self.main.prefs_controller.set(DRAW_GHOST, not self.main.prefs_controller.get(DRAW_GHOST))

    # Handles key input for the key config interface
    def handle_key_config_input(self, keycode):
        if self.choosing_key:
            # Check if that key isn't taken already
            for i in range(len(CONTROLS)):
                if i != self.selected_setting and self.main.prefs_controller.get(CONTROLS[i]) == keycode:
                    # Cancel the key change, if it's a duplicate
                    self.beep_snd.play()
                    return

            # Save the key they pressed, since we know it's not a duplicate
            self.main.prefs_controller.set(CONTROLS[self.selected_setting], keycode)
            self.choose_snd.play()
            self.choosing_key = False
            return

        if (keycode == K_SPACE or keycode == K_RETURN) and self.selected_setting <= KEY_QUIT:
            # Start the key config process
            self.choose_snd.play()
            self.choosing_key = True

    # Handles stuff for the high scores
    def handle_high_scores_input(self, keycode):
        # Are we asking if they want to clear the high scores?
        if self.confirm_score_clear:
            if keycode == K_RETURN:
                # Alright, clear the current high scores file
                os.remove(HIGH_SCORE_FILES[self.current_score_page])
                self.main.sound_controller.get_sound(SND_PATH + "level complete.ogg").play()

                # Load the high score data
                self.refresh_high_score_page()
            else:
                self.back_snd.play()

            self.confirm_score_clear = False
            return

        # Switch the high score page if it's an arrow key
        if keycode == K_LEFT:
            self.current_score_page = max(self.current_score_page - 1, 0)
            self.choose_snd.play()
        elif keycode == K_RIGHT:
            self.current_score_page = min(self.current_score_page + 1, len(HIGH_SCORE_FILES) - 1)
            self.choose_snd.play()
        elif keycode == K_BACKSPACE or keycode == K_DELETE:
            # Give them a warning first (only if the file exists though)
            self.confirm_score_clear = len(self.main.read_high_scores(HIGH_SCORE_FILES[self.current_score_page])) > 0

            if self.confirm_score_clear:
                self.beep_snd.play()

        # Load the high score data
        self.refresh_high_score_page()

    # Handles page switching for the help screens
    def handle_help_input(self, keycode):
        # Bail?
        if keycode == K_ESCAPE:
            self.mode = MODE_MAIN_MENU
            self.back_snd.play()

        # Switch page?
        direction = 0

        if keycode == K_RIGHT or keycode == K_SPACE or keycode == K_RETURN:
            direction = 1
            self.select_snd.play()

        elif keycode == K_LEFT:
            direction = -1
            self.select_snd.play()

        self.help_page = ((self.help_page + direction) % self.total_help_pages)

    # Updates the music source if the streaming setting changed
    def update_music(self):
        if self.streaming and not self.main.prefs_controller.get(STREAM_MUSIC):
            music.stop()
            self.main.total_resources = 6
            self.main.resources_loaded = 0

            # Now load the music files as objects
            self.main.state = STATE_LOADING
            self.main.load_resources()

            # Finally set this to false as well (otherwise, it would have thrown off the stop() function)
            self.streaming = False

        elif not self.streaming and self.main.prefs_controller.get(STREAM_MUSIC):
            # Deallocate the current music
            if self.music is not None:
                self.music.stop()
                del self.music

            # Delete the other resources too
            for key in self.main.sound_controller.music_pool.keys():
                del self.main.sound_controller.music_pool[key]

            # And stream now
            music.load(MUSIC_PATH + "music1.ogg")
            music.play(-1)
            self.streaming = True

    # Draws whatever part of the menu we're in.
    def draw_scene(self, mode, surface):
        # Draw the common background, if allowed (used for most menu screens)
        if mode != MODE_CREDITS:
            if self.main.prefs_controller.get(DRAW_BG):
                surface.blit(self.menu_anim[self.current_bg], (0, 0))
            else:
                surface.fill((0, 0, 0))

        # Now branch off and draw specific menu things
        if mode == MODE_MAIN_MENU:
            self.draw_main_menu(surface)
        elif mode == MODE_HIGH_SCORES:
            self.draw_high_scores(surface)
        elif mode == MODE_SETTINGS:
            self.draw_settings(mode, surface)
        elif mode == MODE_KEY_CONFIG:
            self.draw_key_config(mode, surface)
        elif mode == MODE_CREDITS:
            self.draw_credits(surface)
        elif mode == MODE_ABOUT:
            self.draw_about(surface)
        elif mode == MODE_HELP:
            self.draw_help(surface)

    # Helper function that does exactly what it says
    def draw_main_menu(self, surface):
        # Then draw the menu items
        for i in range(0, ITEM_SETTINGS):
            surface.blit(self.menu_items[i], (240, 30 * i + 90))

        # Makes a gap between the game modes and settings
        for i in range(ITEM_SETTINGS, len(self.menu_items)):
            surface.blit(self.menu_items[i], (240, 30 * i + 110))

        # Draw the pointer
        if self.selected < ITEM_SETTINGS:
            surface.blit(self.pointer, (200, 30 * self.selected + 90))
        else:
            surface.blit(self.pointer, (200, 30 * self.selected + 110))

        # Draw some explanatory text for gaming n00bs... :P
        shadow = self.text_font.render("Use arrow keys to move pointer. Press Space/Enter to select.", True, (0, 0, 0))
        text = self.text_font.render("Use arrow keys to move pointer. Press Space/Enter to select.", True, BRIGHT_TEXT_COLOR)

        surface.blit(shadow, (1 + (SCREEN_WIDTH / 2 - shadow.get_width() / 2), 436))
        surface.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, 435))

    # Draws the current high score page we're on
    def draw_high_scores(self, surface):
        # Header first
        shadow = self.header_font.render(GAME_MODES[self.current_score_page], True, (0, 0, 0))
        text = self.header_font.render(GAME_MODES[self.current_score_page], True, DEFAULT_TEXT_COLOR)

        surface.blit(shadow, (11, 16))
        surface.blit(text, (10, 15))

        # Table header
        y = 70
        self.text_font.set_underline(True)
        for i in range(len(HIGH_SCORES_TABLE)):
            shadow = self.text_font.render(HIGH_SCORES_TABLE[i], True, (0, 0, 0))
            text = self.text_font.render(HIGH_SCORES_TABLE[i], True, DEFAULT_TEXT_COLOR)
            surface.blit(shadow, (1 + HIGH_SCORES_TABLE_OFFSETS[i], y + 1))
            surface.blit(text, (HIGH_SCORES_TABLE_OFFSETS[i], y))

        self.text_font.set_underline(False)
        y += self.text_font.get_linesize()

        # Now draw the high scores
        rank = 1

        for entry in self.current_scores:
            # Reorder the tuple from sorting format to match the layout
            # of the high score table columns. Also convert the time count
            # to a human-readable form.
            entry = (str(rank) + '.', entry[ENTRY_NAME], str(entry[ENTRY_SCORE]), str(entry[ENTRY_LEVEL]), self.main.time_to_str(entry[ENTRY_TIME]))

            for i in range(len(entry)):
                shadow = self.text_font.render(entry[i], True, (0, 0, 0))
                text = self.text_font.render(entry[i], True, BRIGHT_TEXT_COLOR)
                surface.blit(shadow, (1 + HIGH_SCORES_TABLE_OFFSETS[i], y + 1))
                surface.blit(text, (HIGH_SCORES_TABLE_OFFSETS[i], y))

            y += self.text_font.get_linesize()
            rank += 1

        # And draw the instructions on the bottom
        y += self.text_font.get_linesize()

        if self.confirm_score_clear:
            text = "Are you sure you want to clear the high scores list? This is not undoable."
            text2 = "Press Return to confirm, or press any other key to cancel."
            color = WARNING_TEXT_COLOR
        else:
            text = "Press left and right to scroll through the different game modes. Press"
            text2 = "Backspace to clear the current list, or Esc or Space to return to menu."
            color = DEFAULT_TEXT_COLOR

        shadow = self.text_font.render(text, True, (0, 0, 0))
        label = self.text_font.render(text, True, color)
        surface.blit(shadow, (1 + HIGH_SCORES_TABLE_OFFSETS[0], y + 1))
        surface.blit(label, (HIGH_SCORES_TABLE_OFFSETS[0], y))

        y += self.text_font.get_linesize()
        shadow = self.text_font.render(text2, True, (0, 0, 0))
        label = self.text_font.render(text2, True, color)
        surface.blit(shadow, (1 + HIGH_SCORES_TABLE_OFFSETS[0], y + 1))
        surface.blit(label, (HIGH_SCORES_TABLE_OFFSETS[0], y))

    # Helper function that draws the normal settings interface
    def draw_settings(self, mode, surface):
        menu_y_offsets = []
        vals = ['No', 'Yes']
        x = SETTINGS_X_OFFSET
        y = SETTINGS_Y_OFFSET
        line_height = self.text_font.get_linesize()
        sub_height = self.subtitle_font.get_linesize()

        menu_y_offsets.append(y)
        surface.blit(self.text_font.render("Music Volume: %.0f%%" % (self.main.prefs_controller.get(MUSIC_VOLUME) * 100), True, DEFAULT_TEXT_COLOR), (x, y))
        y += line_height

        menu_y_offsets.append(y)
        surface.blit(self.text_font.render("Sound Volume: %.0f%%" % (self.main.prefs_controller.get(SOUND_VOLUME) * 100), True, DEFAULT_TEXT_COLOR), (x, y))
        y += line_height * 2  # Make a line break

        menu_y_offsets.append(y)
        surface.blit(self.text_font.render("Use Fullscreen Mode By Default: " + vals[self.main.prefs_controller.get(RUN_FULLSCREEN)], True, DEFAULT_TEXT_COLOR), (x, y))
        y += line_height

        surface.blit(self.subtitle_font.render("You can press Command-F or Alt-Enter or F11 to switch between fullscreen and windowed mode.", True, DEFAULT_TEXT_COLOR), (x, y))
        y += sub_height * 2  # Gap

        menu_y_offsets.append(y)
        surface.blit(self.text_font.render("Draw Frame Rate: " + vals[self.main.prefs_controller.get(DRAW_FRAMERATE)], True, DEFAULT_TEXT_COLOR), (x, y))
        y += line_height

        surface.blit(self.subtitle_font.render("You can press Command-R or Ctrl-R to temporary show the frame rate at any time.", True, DEFAULT_TEXT_COLOR), (x, y))
        y += sub_height * 2

        menu_y_offsets.append(y)
        surface.blit(self.text_font.render("Use Streaming Music: " + vals[self.main.prefs_controller.get(STREAM_MUSIC)], True, DEFAULT_TEXT_COLOR), (x, y))
        y += line_height

        surface.blit(self.subtitle_font.render("Uses less memory and speeds up load times; however, may cause slight quality distortion.", True, DEFAULT_TEXT_COLOR), (x, y))
        y += sub_height * 2

        menu_y_offsets.append(y)
        surface.blit(self.text_font.render("Draw Background Images: " + vals[self.main.prefs_controller.get(DRAW_BG)], True, DEFAULT_TEXT_COLOR), (x, y))
        y += line_height + sub_height

        menu_y_offsets.append(y)
        surface.blit(self.text_font.render("Show Next Piece Preview: " + vals[self.main.prefs_controller.get(SHOW_PREVIEW)], True, DEFAULT_TEXT_COLOR), (x, y))
        y += line_height + sub_height

        menu_y_offsets.append(y)
        surface.blit(self.text_font.render("Draw Ghost Piece: " + vals[self.main.prefs_controller.get(DRAW_GHOST)], True, DEFAULT_TEXT_COLOR), (x, y))
        y = COMMON_SETTINGS_OFFSET

        # The "common" menu items, which both general and key config have
        self.draw_common_settings(mode, surface, menu_y_offsets)

        # Draw the pointer
        surface.blit(self.pointer, (0, menu_y_offsets[self.selected_setting] - self.pointer.get_height() / 2 + line_height / 2))

        # Draw some explanatory text at the bottom
        surface.blit(self.subtitle_font.render("Press up and down to scroll through the options, then use the left/right arrows", True, DEFAULT_TEXT_COLOR), (x, 445))
        surface.blit(self.subtitle_font.render("space/return keys to set/choose the option, depending on what the option is.", True, DEFAULT_TEXT_COLOR), (x, 445 + sub_height))

    # Helper function that draws the key config interface
    def draw_key_config(self, mode, surface):
        menu_y_offsets = []
        key_labels = ['Move Piece Left:', 'Move Piece Right:', 'Rotate CW:', 'Rotate CCW:',
                      'Speed Up:', 'Drop Piece:', 'Detonate Dynamite:', 'Pause Game:', 'Quit to Menu:']
        line_height = self.text_font.get_linesize()
        sub_height = self.subtitle_font.get_linesize()
        x = SETTINGS_X_OFFSET
        y = SETTINGS_Y_OFFSET

        # Draw the little warning notice thing
        surface.blit(self.subtitle_font.render("Note: Cmd-Q, Cmd-M, Cmd-F, Cmd-R, Cmd-Tab, Alt-F4, Alt-Enter, F11, and Alt-Tab all trigger system-", True, DEFAULT_TEXT_COLOR), (x, y))
        y += sub_height
        surface.blit(self.subtitle_font.render("related functions (toggle fullscreen, close window, etc.), so be careful to not choose key combos", True, DEFAULT_TEXT_COLOR), (x, y))
        y += sub_height
        surface.blit(self.subtitle_font.render("that could accidentally trigger a special key combination.", True, DEFAULT_TEXT_COLOR), (x, y))
        y += sub_height * 2

        # Draw the key labels
        initial_y = y

        for label in key_labels:
            menu_y_offsets.append(y)
            surface.blit(self.text_font.render(label, True, DEFAULT_TEXT_COLOR), (x, y))
            y += line_height

        # The "common" menu items, which both general and key config have
        self.draw_common_settings(mode, surface, menu_y_offsets)

        # Draw the keys (all at equal offsets)
        x = 225
        y = initial_y

        for i in range(len(CONTROLS)):
            # If we're choosing a key, make sure the user knows which one
            name = key.name(self.main.prefs_controller.get(CONTROLS[i]))

            if self.choosing_key and self.selected_setting == i:
                surface.blit(self.text_font.render(name + " <press another key to change>", True, (255, 255, 255)), (x, y))
            else:
                surface.blit(self.text_font.render(name, True, BRIGHT_TEXT_COLOR), (x, y))

            y += line_height

        # Draw some explanatory text for the last one
        surface.blit(self.subtitle_font.render("Used from the pause menu.", True, DEFAULT_TEXT_COLOR), (SETTINGS_X_OFFSET, y))

        # Draw the pointer
        surface.blit(self.pointer, (0, menu_y_offsets[self.selected_setting] - self.pointer.get_height() / 2 + line_height / 2))

        # Draw some explanatory text at the bottom
        x = SETTINGS_X_OFFSET
        surface.blit(self.subtitle_font.render("Press up and down to scroll through the options, and press Space/Enter to select", True, DEFAULT_TEXT_COLOR), (x, 445))
        surface.blit(self.subtitle_font.render("a key to change. Then, press the new key you wish to bind to that control.", True, DEFAULT_TEXT_COLOR), (x, 445 + sub_height))

    # Menu items that both the normal settings and key config interfaces share.
    # The menu y offsets is a list of y coordinates used by the settings drawing
    # functions that keeps track of where the menu items are so the pointer can
    # be drawn next to them easily.
    def draw_common_settings(self, mode, surface, menu_y_offsets):
        x = SETTINGS_X_OFFSET
        y = COMMON_SETTINGS_OFFSET
        line_height = self.text_font.get_linesize()
        sub_height = self.subtitle_font.get_linesize()

        menu_y_offsets.append(y)

        # The "return to whatever mode you were in before" option
        if mode == MODE_SETTINGS:
            label = "Configure Keys..."
        else:
            label = "General Settings..."

        surface.blit(self.text_font.render(label, True, DEFAULT_TEXT_COLOR), (x, y))
        y += line_height + sub_height

        menu_y_offsets.append(y)
        surface.blit(self.text_font.render("Reset All to Defaults", True, DEFAULT_TEXT_COLOR), (x, y))
        y += line_height

        menu_y_offsets.append(y)
        surface.blit(self.text_font.render("Don't Save and Return to Menu", True, DEFAULT_TEXT_COLOR), (x, y))
        y += line_height

        menu_y_offsets.append(y)
        surface.blit(self.text_font.render("Save and Return to Menu", True, DEFAULT_TEXT_COLOR), (x, y))
        y += line_height

    # Draws the scrolling credits
    def draw_credits(self, surface):
        if self.main.prefs_controller.get(DRAW_BG):
            surface.blit(self.credits_bg, (0, 0))
        else:
            surface.fill((0, 0, 0))

        current_line = 1

        for line in file("data/credits.txt"):
            line = line.strip()

            # Check if this is a heading
            color = BRIGHT_TEXT_COLOR

            if line.startswith("#"):
                color = (255, 255, 255)
                line = line[1:]  # Strip the delimiter

            # Shadow + normal text
            surface.blit(self.text_font.render(line, True, (0, 0, 0)), (31, self.credits_offset + 1 + current_line * self.text_font.get_linesize()))
            surface.blit(self.text_font.render(line, True, color), (30, self.credits_offset + current_line * self.text_font.get_linesize()))

            current_line += 1

        # Blit the header to give that fading effect
        if self.main.prefs_controller.get(DRAW_BG):
            surface.blit(self.credits_header, (0, 0))
        else:
            cover = Surface((self.credits_header.get_width(), self.credits_header.get_height()))
            cover.fill((0, 0, 0))
            surface.blit(cover, (0, 0))

            # Draw a centered header
            header = self.header_font.render("Credits", True, DEFAULT_TEXT_COLOR)
            surface.blit(header, (SCREEN_WIDTH / 2 - header.get_width() / 2, 35))

    # Draws the about page
    def draw_about(self, surface):
        # Read in the about file and draw the text from there
        current_line = 1

        for line in file("data/about.txt"):
            line = line.strip()

            # EASTER EGG! WE W4S H4X3D!@!!!1!11!11 (a nice little treat, ain't it?)
            if self.wut:
                wewt = ["", "WE W4S H4X3D!!1  OH NOES!!11!1111!111", "WE W4S H4Xin3D!!11!11  IN BEWT KAMP", "", "IN A.D. 2101",
                        "WAR WAS BEGINNING.", "WHAT HAPPEN ?", "SOMEBODY SET UP US THE BOMB.", "WE GET SIGNAL.", "WHAT !",
                        "MAIN SCREEN TURN ON.", "IT'S YOU !!", "HOW ARE YOU GENTLEMEN !!", "ALL YOUR BASE ARE BELONG TO US.",
                        "YOU ARE ON THE WAY TO DESTRUCTION", "WHAT YOU SAY !!", "YOU HAVE NO CHANCE TO SURVIVE MAKE YOUR TIME. HA HA HA HA ....",
                        "CAPTAIN !!", "TAKE OFF EVERY 'ZIG'!!", "YOU KNOW WHAT YOU DOING.", "MOVE 'ZIG'.", "FOR GREAT JUSTICE."]
                line = wewt[current_line % len(wewt)]

            # Shadow + normal text
            surface.blit(self.text_font.render(line, True, (0, 0, 0)), (51, 61 + current_line * self.text_font.get_linesize()))
            surface.blit(self.text_font.render(line, True, DEFAULT_TEXT_COLOR), (50, 60 + current_line * self.text_font.get_linesize()))

            current_line += 1

    # Draws the current help page
    def draw_help(self, surface):
        if self.total_help_pages < 1:
            # Oops?
            surface.blit(self.text_font.render("No help files found.", True, (0, 0, 0)), (HELP_X_OFFSET + 1, HELP_Y_OFFSET + 1))
            surface.blit(self.text_font.render("No help files found.", True, DEFAULT_TEXT_COLOR), (HELP_X_OFFSET, HELP_Y_OFFSET))
        else:
            # Draw the help page number
            text = "Page " + str(self.help_page + 1) + " / " + str(self.total_help_pages)
            surface.blit(self.header_font.render(text, True, (0, 0, 0)), (HELP_PAGE_LOC[0] + 1, HELP_PAGE_LOC[1] + 1))
            surface.blit(self.header_font.render(text, True, BRIGHT_TEXT_COLOR), HELP_PAGE_LOC)

            y = HELP_Y_OFFSET  # Initial y location

            # Draw this help file
            for line in file(HELP_PATH + str(self.help_page + 1) + ".txt"):
                line = line.strip()

                # Encountered a "draw all tetrominoes" token?
                if line == "{{TETROMINOES}}":
                    y += self.help_font.get_linesize() / 2

                    # Project all the tetrominoes onto the help page area specified
                    current = Tetromino()
                    x_offset = HELP_X_OFFSET

                    for type in NORMAL_TILES:
                        current.reset(type)

                        # Calculate x/y offsets
                        left_x, right_x, up_y, down_y = current.get_extremities()

                        current.center_x -= left_x
                        current.center_y -= up_y

                        # Draw the block
                        for block in current.get_blocks():
                            block_img = self.main.image_pool[IMG_PATH + "blocks/" + type.lower() + ".png"]
                            surface.blit(block_img, (x_offset + block[0] * block_img.get_width(), y + block[1] * block_img.get_height()))

                        # Update the x-offset
                        x_offset += current.get_size(True)[0] + PIECE_PADDING

                    # And update the y-offset too
                    y += BLOCK_SIZE[1] * 2 + self.help_font.get_linesize() / 2

                else:
                    # Check if this is a heading
                    color = DEFAULT_TEXT_COLOR

                    if line.startswith("#"):
                        color = (255, 255, 255)
                        line = line[1:]  # Strip the delimiter

                    # Draw the line
                    surface.blit(self.text_font.render(line, True, (0, 0, 0)), (HELP_X_OFFSET + 1, y + 1))
                    surface.blit(self.text_font.render(line, True, color), (HELP_X_OFFSET, y))
                    y += self.help_font.get_linesize()

        # Draw the note
        surface.blit(self.help_font.render("(Use the arrows to scroll through the pages; press Esc to return to menu.)", True, (0, 0, 0)), (HELP_X_OFFSET + 1, HELP_Y_NOTE_OFFSET + 1))
        surface.blit(self.help_font.render("(Use the arrows to scroll through the pages; press Esc to return to menu.)", True, BRIGHT_TEXT_COLOR), (HELP_X_OFFSET, HELP_Y_NOTE_OFFSET))
