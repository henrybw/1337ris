#
# 1337ris -- main.py
# Henry Weiss
#
# The backbone of the game. Has many roles and responsibilities, but that is
# the most succint way of putting it. In more detail:
#
# - Runs the event loop and coordinates communication between other controller
#   objects.
# - Manages the game state, and any transitioning/communication between them.
# - Manages the resource pools (images and sounds), allowing access to shared
#   resources.
# - Contains a lot of what defines the application functionality (e.g. mini-
#   mizing, toggling fullscreen, etc.) -- basically glorified event handling.
# - Has several utility methods function, like a time formatter, a fade out
#   music function that takes streaming settings into account, and a high scores
#   file interface.
# - Executes screen transitions.
#
# Note: 1337ris uses a time-based animation system instead of a frame or
# tick-based update system. The pygame timer really bogs down the game for
# some reason, so I decided to use time-based animation in order to get
# decent response from the keys. (Maybe there's too much blitting? Perhaps
# it was due to pygame overhead? Or maybe SDL's timer just sucks. I'm
# guessing it's pygame overhead, but I don't really know.)
#

from .headers import *

# State constants found through trial-and-error (since pygame was so kind as
# to not specify the activate event states...)
INPUTFOCUSCHANGED_MAC = 3
INPUTFOCUSCHANGED_WIN = 2
MINIMIZE_MAC = 4
MINIMIZE_WIN = 6

# Stuff for screen transitions
TRANSITION_POINTS = 7  # How many bars will be used, for instance
TRANSITION_OVERLAP_SPEED = 1.125
TRANSITION_SPLIT_HORIZ_SPEED = 3.125
TRANSITION_SPLIT_VERT_SPEED = 2.125
TRANSITION_CATCHUP_SPEED = 4.75
TRANSITION_CATCHUP_OFFSET = 300  # Pixel difference between bars in catchup
TRANSITION_CROSSFADE_DELAY = 350  # In milliseconds
TRANSITION_BLOCKS_SPEED = 0.45
TRANSITION_BLOCK_SIZE = (40, 40)
TRANSITION_QUARTERS_SPEED = 1.125

class Main:
    # Initializes pygame and our helper controller objects.
    def __init__(self):
        # First, check if we can load things other than just BMPs
        if not image.get_extended():
            print("Fatal Error: extended image support not enabled.")
            exit()  # Bail out -- we can't load our resources

        # Otherwise, start up pygame
        mixer.pre_init(SOUND_FREQ)  # Higher quality sounds
        pygame.init()

        # And initialize our controller objects
        self.prefs_controller = PrefsController(PREFS_FILE, DEFAULTS)
        self.sound_controller = SoundController(self.prefs_controller.get(SOUND_VOLUME), self.prefs_controller.get(MUSIC_VOLUME))

        # Resource pool to keep track of images
        self.image_pool = {}

        # Initialize the display
        display.set_caption("1337ris")
        self.fullscreen = self.prefs_controller.get(RUN_FULLSCREEN)

        # Initialize and load the game states
        self.states = [MainMenu(self), HighScores(self), TraditionalMode(self), CrossCutMode(self), ConvergenceMode(self), PsychedelicMode(self)]
        self.state = STATE_LOADING

        # For keeping track of frame rate
        self.clock = Clock()
        self.fps_font = Font(DEFAULT_FONT, 12)

        # For pausing if app is deactivated and such
        self.active = True

        # Transitions
        self.in_transition = False
        self.current_transition = 0

        # Grab the total number of resources to load
        self.resources_loaded = -1
        self.total_resources = 0

        for state in self.states:
            self.total_resources += state.total_resources

    # Intercepts attribute changes
    def __setattr__(self, attr, value):
        # State changer. Notifies the old and new states of the transition.
        if attr == "state" and attr in self.__dict__:
            if self.state != STATE_LOADING:
                # Just choose a random transition
                transition = TRANSITION_RANDOM

                # Notify old state of change
                userdata = self.states[self.state].stop()
            else:
                # We really want crossfading to open the show
                transition = TRANSITION_CROSSFADE
                userdata = None  # Oh, and we need to declare this too

            if value != STATE_LOADING:
                # Some states will switch in their start method if something
                # failed or if the state wasn't ready to switch, so we need
                # to account for that
                expected_state = self.state

                # Switch states and notify new state of change
                self.states[value].start(userdata)

                if self.state != expected_state:
                    return  # A different call must have already taken care of this

                # Do transition with the new screen
                self.transition_screen(transition, self.states[value].draw(None, False))

        # Pauses sounds upon activation/deactivation events
        elif attr == "active":
            if not value and self.state >= STATE_TRADITIONAL:
                self.states[self.state].paused = True
                self.sound_controller.paused = True
            elif self.state < STATE_TRADITIONAL or not self.states[self.state].paused:
                self.sound_controller.paused = not value

        # Switches display modes
        elif attr == "fullscreen":
            # Hide the cursor in fullscreen
            mouse.set_visible(not value)

            # Finally switch the mode
            if value:
                display.set_mode(DIMENSIONS, FULLSCREEN)
            else:
                display.set_mode(DIMENSIONS)

        # Otherwise default behavior
        self.__dict__[attr] = value

    # Loads resources for each game state
    def load_resources(self):
        # Get the loading images ready
        self.loading_img = image.load(IMG_PATH + "loading.png")
        self.progress_bg = image.load(IMG_PATH + "progress bg.png")
        self.progress_complete = image.load(IMG_PATH + "progress complete.png")
        self.progress_bar = image.load(IMG_PATH + "progress.png")

        # Set up the viewable rect (how much of the progress bar should be shown)
        self.progress_rect = self.progress_bar.get_rect()

        # Draw the initial loading screen image
        self.update_load_progress()

        # Now load the resources
        for state in self.states:
            state.load_resources()

        # Delay a bit before we go to the main menu
        self.load_wait = 1000

    # Updates the resource counter and the progress bar
    def update_load_progress(self):
        self.resources_loaded += 1
        self.progress_rect.width = (float(self.resources_loaded) / self.total_resources) * self.progress_bar.get_width()

        # Check if the user is trying to quit (not perfect, but better than nothing...)
        events = event.get()

        for next_event in events:
            if next_event.type == KEYDOWN:
                if (next_event.key == K_q and key.get_mods() & KMOD_META) or (next_event.key == K_F4 and key.get_mods() & KMOD_ALT):
                    self.quit()

        # Draw the loading screen to the screen
        self.draw_loading_screen(display.get_surface())

        # And swap the buffers
        display.update()

    # Draws the loading screen onto the specified surface
    def draw_loading_screen(self, surface):
        surface.blit(self.loading_img, (0, 0))
        surface.blit(self.progress_bg, (SCREEN_WIDTH * 0.5 - self.progress_bg.get_rect().width * 0.5, 360))
        surface.blit(self.progress_bar, (SCREEN_WIDTH * 0.5 - self.progress_bar.get_rect().width * 0.5, 360), self.progress_rect)

        # Complete?
        if self.resources_loaded >= self.total_resources:
            surface.blit(self.progress_complete, (SCREEN_WIDTH * 0.5 - self.progress_complete.get_rect().width * 0.5, 360))

    # Runs the main event loop
    def run(self):
        last_time = time.get_ticks()

        while True:
            # Keep track of timing
            elapsed_time = time.get_ticks() - last_time
            last_time += elapsed_time  # Make sure we don't "lose" any time
            self.clock.tick()

            # Grab all waiting events from the queue (unless we're inactive, in which
            # case just wait for an event, so we don't hog up the CPU)
            if self.active:
                events = event.get()
            else:
                # The huge jump that will occur when waiting for an event might throw
                # off some of the time-based animations, so we're gonna prevent that.
                old_elapsed = elapsed_time
                events = [event.wait()]

                elapsed_time = old_elapsed
                last_time = time.get_ticks()

            for next_event in events:
                # Close window?
                if next_event.type == QUIT:
                    self.quit()

                # Handle activation events
                elif self.is_activation_event(next_event):
                    self.active = next_event.gain
                    continue

                # Handle key input (mostly special/system key commands first, then handoff to current state)
                elif next_event.type == KEYDOWN:
                    keycode = next_event.key

                    # "Boss keys", i.e. emergency bailout. Responds to Cmd-Q (Macs) and Alt-F4 (Windows)
                    if (keycode == K_q and key.get_mods() & KMOD_META) or (keycode == K_F4 and key.get_mods() & KMOD_ALT):
                        self.quit()

                    # Minimizing (Windows doesn't have a system shortcut for minimizing, so it doesn't get one here! Mwahaha!)
                    elif keycode == K_m and key.get_mods() & KMOD_META:
                        # Exit fullscreen in order to minimize
                        if self.fullscreen:
                            self.fullscreen = False

                        display.iconify()

                        # For some reason deactivate events aren't always posted...
                        self.active = False
                        continue

                    # Temporary full-screen toggling (Cmd-F for Macs, Alt-Enter/F11 for Windows)
                    elif (keycode == K_f and key.get_mods() & KMOD_META) or (keycode == K_RETURN and key.get_mods() & KMOD_ALT) or keycode == K_F11:
                        self.fullscreen = not self.fullscreen

                    # Otherwise just hand it off to the current game state
                    elif self.state != STATE_LOADING:
                        self.states[self.state].key_down(keycode, next_event.unicode)

            # Are we still in the middle of the loading screen pause?
            if self.state == STATE_LOADING:
                if self.load_wait <= 0:
                    self.state = STATE_MAIN_MENU
                else:
                    self.load_wait -= elapsed_time

                    # Just blit the loading complete screen and get out of here
                    self.draw_loading_screen(display.get_surface())
                    display.update()
                    continue

            # Update and redraw (only if the app is active)
            if self.active:
                # Check if a screen transition is in place
                if self.in_transition:
                    self.update_transition(elapsed_time)

                # Otherwise, update normally
                else:
                    self.states[self.state].update(elapsed_time)
                    self.states[self.state].draw()

                    # Draw frame rate
                    if self.prefs_controller.get(DRAW_FRAMERATE) or (key.get_pressed()[K_r] and
                      (key.get_mods() & KMOD_META or key.get_mods() & KMOD_CTRL)):
                        # Draw the frame rate plus a shadow so it can stand out on light backgrounds
                        shadow = self.fps_font.render("Frame Rate: %.3f fps" % self.clock.get_fps(), True, (0, 0, 0))
                        text = self.fps_font.render("Frame Rate: %.3f fps" % self.clock.get_fps(), True, (255, 255, 0))
                        display.get_surface().blit(shadow, (6, 463))
                        display.get_surface().blit(text, (5, 462))

                # And swap the buffers
                display.update()

    # Formats a millisecond counter into an actual, human-readable time display
    def time_to_str(self, millis):
        time_str = "%02d:%02d" % (int(millis / 60000 % 60), int(millis / 1000 % 60))

        if millis / 3600000 > 0:
            time_str = str(int(millis / 3600000)) + ":" + time_str  # We're into hours now... o_O

        return time_str

    # Reads the high scores file into a list of tuples. See the HighScores
    # class for a description of what the tuple format is.
    def read_high_scores(self, filename):
        # Check if the file even exists
        if not os.access(filename, os.F_OK):
            return []

        # Otherwise, gather the scores
        scores = []
        current_score = []  # For constructing the tuple
        index = 0

        for line in open(filename, 'rb'):
            line = line.strip()  # Remove newlines

            # Decrypt the current line
            data = line.decode().split(DELIMITER)
            data.reverse()
            string = ''

            for ch in data:
                if ch != '':
                    string += chr(-~(int(ch) ^ 127))

            # Name, at index one, is the only non-int type
            if index != ENTRY_NAME:
                current_score.append(int(string))
            else:
                current_score.append(string)

            # Finished reading one score entry?
            if index == TOTAL_ITEMS - 1:
                scores.append((current_score[0], current_score[1], current_score[2], current_score[3]))
                current_score = []
                index = 0
            else:
                index += 1

        return scores

    # Saves a list of high score tuple entries to the high scores file.  See the HighScores
    # class for a description of what the tuple format is.
    def save_high_scores(self, filename, scores):
        output = open(filename, 'wb')
        z = 1
        for entry in scores:
            for item in entry:
                # Convert to string
                item = str(item)

                # Save the data in reverse
                for i in range(len(item) - 1, -1, -1):
                    output.write((str(-~(ord(item[i]) ^ 127)) + DELIMITER).encode())

                # Add newline
                output.write("\n".encode())

        # Save the file
        output.close()

    # For testing if an event is an activation event or not (due to stupid differences
    # in SDL between OS X/Windows, and no constants that I'm aware of...)
    def is_activation_event(self, next_event):
        return (next_event.type == ACTIVEEVENT and
                (next_event.state == INPUTFOCUSCHANGED_MAC or next_event.state == INPUTFOCUSCHANGED_WIN or
                 next_event.state == MINIMIZE_MAC or next_event.state == MINIMIZE_WIN))

    # Fades out the sound for (by default) 1 second.
    def fadeout_sound(self, delay=1000):
        if self.prefs_controller.get(STREAM_MUSIC):
            music.fadeout(delay)

            while music.get_busy():
                pass
        else:
            mixer.fadeout(delay)

            while mixer.get_busy():
                pass

        # Clear any stray events from the queue
        event.clear()

    # Initiates a screen transition. The end parameter designates
    # the surface that should be drawn at the end of the transition.
    # The starting image is, by default, whatever is on the screen
    # at the time this is called, although you can pass in a custom
    # starting image. To get the end image, use a state's draw()
    # function, but make sure it doesn't draw to the screen. You can
    # then pass the returned surface to this function.
    def transition_screen(self, type, end, start=None):
        self.end = end

        # Get the starting images
        if start is None:
            self.start = display.get_surface().copy()
        else:
            self.start = start

        # Choose the transition
        if type == TRANSITION_RANDOM:
            self.current_transition = randint(0, TOTAL_TRANSITIONS - 1)
        else:
            self.current_transition = type

        # Setup certain variables for the screen transition
        if self.current_transition == TRANSITION_OPEN:
            self.x_pos = [SCREEN_WIDTH / 2, SCREEN_WIDTH / 2]

        elif self.current_transition == TRANSITION_CLOSE:
            self.x_pos = [SCREEN_WIDTH, 0]  # Start from outer edges of screen

        elif self.current_transition == TRANSITION_CATCHUP:
            self.x_pos = []

            for i in range(TRANSITION_POINTS):
                self.x_pos.append(-(i * TRANSITION_CATCHUP_OFFSET))

        elif self.current_transition == TRANSITION_CROSSFADE:
            self.delay = TRANSITION_CROSSFADE_DELAY

            # Make sure the start/end images don't have per-pixel transparency
            self.start.set_alpha(None)
            self.end.set_alpha(None)

        elif self.current_transition == TRANSITION_BLOCKS:
            # Break the screen up into tiles
            self.screen_blocks = []

            for y in range(0, SCREEN_HEIGHT, TRANSITION_BLOCK_SIZE[1]):
                for x in range(0, SCREEN_WIDTH, TRANSITION_BLOCK_SIZE[0]):
                    self.screen_blocks.append((x, y))

            # Scramble the list
            shuffle(self.screen_blocks)

            # For traversing the blocks list
            self.current_block = 0

            # Ensures the blocks get drawn no matter how fast the frame rate is
            self.delay_time = 0

        elif self.current_transition == TRANSITION_SPLIT_HORIZ:
            # Two bars on opposite sides of the screen
            self.x_pos = [-SCREEN_WIDTH, SCREEN_WIDTH]

        elif self.current_transition == TRANSITION_SPLIT_VERT:
            # Two bars on opposite sides of the screen
            self.y_pos = [-SCREEN_HEIGHT, SCREEN_HEIGHT]

        elif self.current_transition == TRANSITION_QUARTERS:
            self.x_pos = 0
            self.y_pos = 0

        # And let it start
        self.in_transition = True

    # Updating method for screen transitions that updates and draws
    # the current state of the transition during the event loop.
    def update_transition(self, elapsed_time):
        if self.current_transition == TRANSITION_OPEN:
            # Update shift positions
            self.x_pos[0] += elapsed_time * TRANSITION_OVERLAP_SPEED
            self.x_pos[1] -= elapsed_time * TRANSITION_OVERLAP_SPEED

            # Check if transition finished and correct if necessary
            if self.x_pos[0] > SCREEN_WIDTH or self.x_pos[1] < 0:
                self.x_pos[0] = SCREEN_WIDTH
                self.x_pos[1] = 0
                self.in_transition = False

            # Construct Rects to draw the portions (ceiling is used
            # to make sure the middle is always covered, regardless of
            # rounding/truncating).
            part1 = Rect(SCREEN_WIDTH / 2, 0, ceil(self.x_pos[0] - SCREEN_WIDTH / 2), SCREEN_HEIGHT)
            part2 = Rect(self.x_pos[1], 0, ceil(SCREEN_WIDTH / 2 - self.x_pos[1]), SCREEN_HEIGHT)

            # Draw those portions
            display.get_surface().blit(self.start, (0, 0))
            display.get_surface().blit(self.end, (SCREEN_WIDTH / 2, 0), part1)
            display.get_surface().blit(self.end, (self.x_pos[1], 0), part2)

        elif self.current_transition == TRANSITION_CLOSE:
            # Update shift positions
            self.x_pos[0] -= elapsed_time * TRANSITION_OVERLAP_SPEED
            self.x_pos[1] += elapsed_time * TRANSITION_OVERLAP_SPEED

            # Check if transition finished and correct if necessary
            if self.x_pos[0] < SCREEN_WIDTH / 2 or self.x_pos[1] > SCREEN_WIDTH / 2:
                self.x_pos[0] = SCREEN_WIDTH / 2
                self.x_pos[1] = SCREEN_WIDTH / 2
                self.in_transition = False

            # Construct Rects to draw the portions (ceiling is used
            # to make sure the middle is always covered, regardless of
            # rounding/truncating).
            part1 = Rect(SCREEN_WIDTH / 2, 0, ceil(self.x_pos[0] - SCREEN_WIDTH / 2), SCREEN_HEIGHT)
            part2 = Rect(self.x_pos[1], 0, ceil(SCREEN_WIDTH / 2 - self.x_pos[1]), SCREEN_HEIGHT)

            # Draw those portions
            display.get_surface().blit(self.end, (0, 0))
            display.get_surface().blit(self.start, (SCREEN_WIDTH / 2, 0), part1)
            display.get_surface().blit(self.start, (self.x_pos[1], 0), part2)

        elif self.current_transition == TRANSITION_CATCHUP:
            # Blit the start image first
            display.get_surface().blit(self.start, (0, 0))

            # Update shift positions
            for i in range(TRANSITION_POINTS):
                self.x_pos[i] += elapsed_time * TRANSITION_CATCHUP_SPEED

                # Correct if this bar has "caught up"
                if self.x_pos[i] >= SCREEN_WIDTH:
                    self.x_pos[i] = SCREEN_WIDTH

                    # Done?
                    if i == TRANSITION_POINTS - 1:
                        self.in_transition = False

                # Calculate this bar rect
                top = SCREEN_HEIGHT * (i / float(TRANSITION_POINTS))
                bottom = SCREEN_HEIGHT * ((i + 1) / float(TRANSITION_POINTS))
                bar = Rect(0, top, max(self.x_pos[i], 0), ceil(bottom - top))

                # Blit it
                display.get_surface().blit(self.end, (0, top), bar)

        elif self.current_transition == TRANSITION_CROSSFADE:
            # Update the time remaining
            self.delay -= elapsed_time

            # Done?
            if self.delay <= 0:
                self.delay = 0
                self.in_transition = False

            # Update the transparency values
            alpha = 255 * (float(self.delay) / TRANSITION_CROSSFADE_DELAY)
            self.start.set_alpha(alpha)
            self.end.set_alpha(255 - alpha)

            # Blit the two images now
            display.get_surface().blit(self.start, (0, 0))
            display.get_surface().blit(self.end, (0, 0))

        elif self.current_transition == TRANSITION_BLOCKS:
            blocks_to_draw = int(round((elapsed_time + self.delay_time) * TRANSITION_BLOCKS_SPEED))

            # Too fast?
            if blocks_to_draw < 1:
                self.delay_time += elapsed_time  # Save the elapsed time so we can use it next time
            else:
                self.delay_time = 0  # We can draw now
                display.get_surface().blit(self.start, (0, 0))

            # Draw the new screen in portions over the old screen
            for i in range(blocks_to_draw):
                # Extract the block rectangles and draw them
                for j in range(self.current_block + 1):
                    block = self.screen_blocks[j]
                    display.get_surface().blit(self.end, block, Rect(block, TRANSITION_BLOCK_SIZE))

                # Move onto next block
                self.current_block += 1

                # Done?
                if self.current_block >= len(self.screen_blocks):
                    self.in_transition = False
                    break

        elif self.current_transition == TRANSITION_SPLIT_HORIZ:
            # Update shift positions
            self.x_pos[0] += elapsed_time * TRANSITION_SPLIT_HORIZ_SPEED
            self.x_pos[1] -= elapsed_time * TRANSITION_SPLIT_HORIZ_SPEED

            # Done?
            if self.x_pos[1] < 0:
                # Correct if necessary
                self.x_pos[0] = 0
                self.x_pos[1] = 0
                self.in_transition = False

            # The two bars, are the exact same, except for their y starting location...
            bar1 = Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT / 2)
            bar2 = Rect(0, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT / 2)

            # ...where we blit the bars is more important
            display.get_surface().blit(self.start, (0, 0))
            display.get_surface().blit(self.end, (self.x_pos[0], 0), bar1)
            display.get_surface().blit(self.end, (self.x_pos[1], SCREEN_HEIGHT / 2), bar2)

        elif self.current_transition == TRANSITION_SPLIT_VERT:
            # Update shift positions
            self.y_pos[0] += elapsed_time * TRANSITION_SPLIT_VERT_SPEED
            self.y_pos[1] -= elapsed_time * TRANSITION_SPLIT_VERT_SPEED

            # Done?
            if self.y_pos[1] < 0:
                # Correct if necessary
                self.y_pos[0] = 0
                self.y_pos[1] = 0
                self.in_transition = False

            # See above comments, except applied to the x start and y location
            bar1 = Rect(0, 0, SCREEN_WIDTH / 2, SCREEN_HEIGHT)
            bar2 = Rect(SCREEN_WIDTH / 2, 0, SCREEN_WIDTH / 2, SCREEN_HEIGHT)

            display.get_surface().blit(self.start, (0, 0))
            display.get_surface().blit(self.end, (0, self.y_pos[0]), bar1)
            display.get_surface().blit(self.end, (SCREEN_WIDTH / 2, self.y_pos[1]), bar2)

        elif self.current_transition == TRANSITION_QUARTERS:
            # Update each shift point
            self.x_pos += elapsed_time * TRANSITION_QUARTERS_SPEED

            # Since the width:height ratio is usually not 1:1, we have to slow
            # down the y speed, since it has less distance to travel.
            self.y_pos += elapsed_time * (TRANSITION_QUARTERS_SPEED * (float(SCREEN_HEIGHT) / SCREEN_WIDTH))

            # Check if the transition is done and correct if necessary
            if self.x_pos > SCREEN_WIDTH / 2:
                self.x_pos = SCREEN_WIDTH / 2
                self.y_pos = SCREEN_HEIGHT / 2

                self.in_transition = False

            # Extract each portion of the image. The first portion is easy, since it is
            # relative to the origin, but the other portions are all relative to the
            # corner they started at (pt 1 from top left, pt 2 from top right, pt 3 from
            # bottom left, pt 4 from bottom right).
            part1 = Rect(0, 0, self.x_pos, self.y_pos)
            part2 = Rect(SCREEN_WIDTH - self.x_pos, 0, self.x_pos, self.y_pos)
            part3 = Rect(0, SCREEN_HEIGHT - self.y_pos, self.x_pos, self.y_pos)
            part4 = Rect(SCREEN_WIDTH - self.x_pos, SCREEN_HEIGHT - self.y_pos, self.x_pos, self.y_pos)

            # Now that we have the correct portions of the image, we can just use the
            # starting point relative to the image as the blitting location.
            display.get_surface().blit(self.start, (0, 0))
            display.get_surface().blit(self.end, part1.topleft, part1)
            display.get_surface().blit(self.end, part2.topleft, part2)
            display.get_surface().blit(self.end, part3.topleft, part3)
            display.get_surface().blit(self.end, part4.topleft, part4)

    # Self-explanatory
    def quit(self):
        pygame.quit()
        sys.exit()
