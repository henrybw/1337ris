#
# 1337ris -- soundcontroller.py
# Henry Weiss
#
# Keeps track of all sounds that are playing currently in a
# resource pool, so that things such as volume manipulation and
# resource management can be handled easily.
#
# Note: music is differentiated from normal sounds.
#

import pygame
from pygame import *
from pygame.mixer import *

class SoundController:
    # Constructor (with optional parameters for initial volume values)
    def __init__(self, sound_volume=1.0, music_volume=1.0):
        # The sound pools, represented by key-value pairs
        self.sound_pool = {}
        self.music_pool = {}

        # Default volumes
        self.music_volume = music_volume
        self.sound_volume = sound_volume

        # Global pausing
        self.paused = False

    # Intercepts attribute changes
    def __setattr__(self, attr, value):
        # Sets the global volume for all of the sounds
        if attr == "sound_volume":
            for sound in self.sound_pool.values():
                sound.set_volume(value)

        # Sets the global volume for the music
        elif attr == "music_volume":
            for song in self.music_pool.values():
                song.set_volume(value)

            # In case we're actually streaming
            music.set_volume(value)

        # Pause/resume all sounds
        elif attr == "paused":
            if value:
                mixer.pause()
                music.pause()
            else:
                mixer.unpause()
                music.unpause()

        # Default behavior otherwise
        self.__dict__[attr] = value

    # Add a sound object to the pool
    def add_sound(self, sound, sound_id, is_music=False):
        if is_music:
            self.music_pool[sound_id] = sound
            sound.set_volume(self.music_volume)
        else:
            self.sound_pool[sound_id] = sound
            sound.set_volume(self.sound_volume)

    # Retrieves a sound object from the pool given its ID
    def get_sound(self, sound_id):
        if sound_id in self.music_pool:
            return self.music_pool[sound_id]
        elif sound_id in self.sound_pool:
            return self.sound_pool[sound_id]
        else:
            return None  # Oops

    # Removes a sound object from the pool. Does
    # nothing if object is in neither pool.
    def remove_sound(self, sound_id):
        if sound_id in self.music_pool:
            del self.music_pool[sound_id]
        elif sound_id in self.sound_pool:
            del self.sound_pool[sound_id]
