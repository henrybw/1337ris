#
# 1337ris -- highscores.py
# Henry Weiss
#
# State class that handles adding new high scores. See constants.py for the
# two tuple formats used here.
#

from headers import *

CURSOR_BLINK_DELAY = 500
MAX_NAME = 23
CURSOR = '_'

class HighScores(MainMenu):
    total_resources = 1

    # Loads only one sound
    def load_resources(self):
        MainMenu.load_resources(self)
        self.new_score_snd = self.load_resource(SND_PATH + "new high score.ogg", RES_TYPE_SOUND)

    # Checks if the player got a new high score, and acts accordingly. The tuple
    # expected is explained in constants.py, under the userdata tuple.
    def start(self, userdata=None):
        # Initialize the instance variables
        self.file = HIGH_SCORE_FILES[userdata[USERDATA_MODE] - STATE_TRADITIONAL]
        self.name = ''
        self.cursor = CURSOR  # Blinks
        self.cursor_delay = CURSOR_BLINK_DELAY
        self.userdata = userdata

        # Check if this is a high score
        if userdata is None or not self.is_new_high_score(userdata):
            # Nothing for us to do
            self.main.state = STATE_MAIN_MENU
            return

        # Wee, high score
        self.new_score_snd.play()

        # Set key repeat to default settings
        key.set_repeat(INITIAL_KEY_DELAY, KEY_REPEAT_DELAY)

    # Determines if this score surpasses the current minimum high score
    def is_new_high_score(self, scoredata):
        # Check if the file even exists
        if not os.access(self.file, os.F_OK):
            # Well, since there's no file, then obviously this is a new high score
            return True

        # If it does, make sure the score we have is a high score
        high_scores = self.main.read_high_scores(self.file)

        return len(high_scores) < MAX_ENTRIES or min(high_scores[ENTRY_SCORE]) < scoredata[USERDATA_SCORE]

    # Updates the cursor
    def update(self, elapsed_time):
        self.cursor_delay -= elapsed_time

        if self.cursor_delay <= 0:
            # Blink
            if self.cursor == '':
                self.cursor = CURSOR
            else:
                self.cursor = ''

            # Reset delay
            self.cursor_delay = CURSOR_BLINK_DELAY

    # Takes user input until they press Return
    def key_down(self, keycode, unicode):
        if keycode == K_RETURN:
            # If this is too short, bail out
            if len(self.name) < 1:
                self.beep_snd.play()
                return

            # Save this high score first
            scores = self.main.read_high_scores(self.file)

            if len(scores) >= MAX_ENTRIES:
                # Delete the lowest score
                min_score = sys.maxint
                min_index = -1

                for i in range(len(scores)):
                    if scores[i][ENTRY_SCORE] < min_score:
                        min_score = scores[i][ENTRY_SCORE]
                        min_index = i

                del scores[min_index]

            # Append the new high score
            scores.append((self.userdata[USERDATA_SCORE], self.userdata[USERDATA_LEVEL], self.userdata[USERDATA_TIME], self.name))

            # And save it
            self.main.save_high_scores(self.file, scores)

            # Go to the high scores page
            self.main.states[STATE_MAIN_MENU].current_score_page = self.userdata[USERDATA_MODE] - STATE_TRADITIONAL
            self.main.states[STATE_MAIN_MENU].refresh_high_score_page()
            self.main.states[STATE_MAIN_MENU].mode = MODE_HIGH_SCORES

            # Return to the menu
            self.choose_snd.play()
            self.main.state = STATE_MAIN_MENU

            return

        if keycode == K_BACKSPACE:
            self.main.sound_controller.get_sound(SND_PATH + "move.ogg").play()
            self.name = self.name[:-1]  # Delete
            return

        # Too long?
        if len(self.name) + 1 > MAX_NAME:
            return

        # Check if this is alphanumeric
        if len(unicode) == 1 and ord(unicode) >= 32 and ord(unicode) <= 126:
            self.name += unicode
            self.main.sound_controller.get_sound(SND_PATH + "lock.ogg").play()

    # Renders the screen and what the user's entered so far
    def draw_scene(self, mode, surface):
        if self.main.prefs_controller.get(DRAW_BG):
            surface.blit(self.menu_anim[self.current_bg], (0, 0))
        else:
            surface.fill((0, 0, 0))

        # Draw the title text
        y_start = 105

        shadow = self.header_font.render("You got a new high score!", True, (0, 0, 0))
        text = self.header_font.render("You got a new high score!", True, DEFAULT_TEXT_COLOR)
        surface.blit(shadow, (1 + (SCREEN_WIDTH / 2 - shadow.get_width() / 2), y_start + 1))
        surface.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, y_start))

        shadow = self.header_font.render("Enter your name:", True, (0, 0, 0))
        text = self.header_font.render("Enter your name:", True, DEFAULT_TEXT_COLOR)
        surface.blit(shadow, (1 + (SCREEN_WIDTH / 2 - shadow.get_width() / 2), y_start + 1 + self.header_font.get_linesize() * 2))
        surface.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, y_start + self.header_font.get_linesize() * 2))

        # Draw the name
        shadow = self.text_font.render(self.name, True, (0, 0, 0))
        text = self.text_font.render(self.name, True, BRIGHT_TEXT_COLOR)
        surface.blit(shadow, (1 + (SCREEN_WIDTH / 2 - shadow.get_width() / 2), y_start + 1 + self.header_font.get_linesize() * 4))
        surface.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, y_start + self.header_font.get_linesize() * 4))

        # And draw the cursor
        cursor = self.text_font.render(self.cursor, True, DEFAULT_TEXT_COLOR)
        surface.blit(cursor, (SCREEN_WIDTH / 2 + text.get_width() / 2, y_start + self.header_font.get_linesize() * 4))
