#
# 1337ris -- gamestate.py
# Henry Weiss
#
# Base class for the controller classes that handle the various game states,
# like the main menu and other game modes. Most of these functions don't
# do anything, however -- that's left up to the subclasses.
#

from .headers import *

# Resource types
(
    RES_TYPE_IMAGE,
    RES_TYPE_SOUND,
    RES_TYPE_MUSIC
) = range(3)

class GameState:
    #
    # Fields
    #

    # Specified by subclasses to let the main controller object know the total resource count
    total_resources = 0

    # Used by subclasses, like the main menu, that have different modes for one state
    mode = 0

    # Used by subclasses to detect when the game state is paused (e.g. window/app inactive, or other similar things)
    paused = False

    # Constructor. Used to notify game states of the main object for
    # communication with the controllers and such.
    def __init__(self, main):
        self.main = main

    #
    # Methods to be overrided by subclasses
    #

    # Called during startup to load all necessary resources for this game state. Resources
    # loaded via calls to load_resource() (see below) are guaranteed to be only loaded once --
    # the main controller object keeps track of a resource pool for each type of resource.
    # This can also be used for general object initialization, although that should not add
    # to the total resource count specified in the class fields.
    #
    # IMPORTANT: Make sure the total_resources variable matches the number of resources loaded
    # in this method, as it is for the loading progress bar. Incorrect figures would throw it off.
    def load_resources(self): pass

    # Called whenever the game enters into this state. Mostly this is used to initialize/reset
    # things like score, animations, sounds playing, etc. This can also be used for interstate
    # communication via the userdata parameter. Due to Python's typeless arguments, this can be
    # of any type the subclass will expect, e.g. a tuple, a dict, or even a full-blown object.
    # This can also be safely ignored -- few game states utilize this anyway.
    def start(self, userdata=None): pass

    # Called whenever the game is about to exit this state, usually when entering into another
    # state. Mostly used to stop sounds and possible clean up the state needs to do before
    # ending. This can also be used for interstate communcation by returning an object to be
    # passed as the userdata paramter to the next state's start() method (see above). This can
    # also be safely ignored.
    def stop(self): pass

    # The updating method, called during every iteration of the game loop. Use the elapsed_time
    # parameter to make calculations as to how much the state has changed in between frames.
    # Aside from key_down(), none of the methods mentioned here besides this one should directly
    # update the game state while the state is running, as that is this method's purpose.
    def update(self, elapsed_time): pass

    # Keyboard event handler. This is called whenever a key press event is read from the event
    # queue. This is where most of the keyboard response should be handled -- polling the key
    # state should be used as infrequently as possible, as the responsiveness of purely polling
    # can be diminished with low frame rates. The unicode field can be ignored, but it is useful
    # whenever text entry is needed.
    def key_down(self, keycode, unicode): pass

    # Helper method for draw(). While this is the method that subclasses must do their drawing in,
    # there is very little reason to call this method on its own. The separation of this from the
    # draw() method, as explained below, is for the purpose of screen transitions, and any type of
    # feature that requires the game be rendered somewhere other than the screen.
    def draw_scene(self, mode, surface): pass

    #
    # Utility methods
    #

    # Generic drawing function. This is the function you should call -- draw_scene() is supposed
    # to be a private, internal function. This abstraction will be used for screen transitions.
    #
    # You can pass in a different state mode and set draw_to_screen to True to draw to a surface
    # and have that returned, instead of drawing directly to the screen. Otherwise, the default
    # behavior is to just draw to the screen.
    def draw(self, mode=None, draw_to_screen=True):
        surface = display.get_surface()

        if mode == None:
            mode = self.mode  # Use the current mode by default

        if not draw_to_screen:
            surface = display.get_surface().copy()  # Use a new surface

        # Call the actual drawing function
        self.draw_scene(mode, surface)

        # Return the new surface is this was temporary
        if not draw_to_screen:
            return surface

    # Individual resource loader. This will automatically newly loaded object into their respective
    # resource pools, unless they already exist. The ID will be the resource filename provided.
    # Returns the newly created resource, or none if an unknown type was specified.
    def load_resource(self, filename, res_type):
        # Load the resource depending on the type
        new_rsrc = None

        if res_type == RES_TYPE_IMAGE:
            # Check if we already loaded this
            if filename in self.main.image_pool:
                return self.main.image_pool[filename]
            else:
                new_rsrc = image.load(filename)
                self.main.image_pool[filename] = new_rsrc

        elif res_type == RES_TYPE_SOUND:
            # Check if we already loaded this
            if self.main.sound_controller.get_sound(filename):
                return self.main.sound_controller.get_sound(filename)
            else:
                new_rsrc = Sound(filename)
                self.main.sound_controller.add_sound(new_rsrc, filename)

        elif res_type == RES_TYPE_MUSIC:
            # Sometimes streaming the sound will cause it to buzz or do
            # weird things. I don't know why, but this is one workaround...
            if not self.main.prefs_controller.get(STREAM_MUSIC):
                if self.main.sound_controller.get_sound(filename):
                    return self.main.sound_controller.get_sound(filename)
                else:
                    new_rsrc = Sound(filename)
                    self.main.sound_controller.add_sound(new_rsrc, filename, True)

        # Now update the resource counter for the loading screen
        self.main.update_load_progress()

        return new_rsrc
