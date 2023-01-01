#
# 1337ris -- prefscontroller.py
# Henry Weiss
#
# Handles saving and loading game preferences. Preferences must
# be manually saved in order to take affect.
#

import os, ConfigParser

# The section where all the preferences are. You can change this
# if you really want to, but there's not much point.
PREFS_SECTION = "Preferences"

class PrefsController:
    # Constructor. You must include the pathname of the preference
    # file (doesn't have to exist, but it will be the reference point),
    # and a dictionary containing a list of the preferences with their
    # default values.
    def __init__(self, prefs_file, defaults):
        # Initialize the prefs to include our section
        self.defaults = defaults
        self.prefs_file = prefs_file
        self.prefs = ConfigParser.RawConfigParser(self.defaults)
        self.prefs.add_section(PREFS_SECTION)

        # Create the prefs file if it's not there
        if not os.access(self.prefs_file, os.F_OK):
            self.save()

        # Read in the existing prefs
        self.load()

    # Gets an attribute from the preferences
    def get(self, key):
        # Make sure the key is valid
        if key in self.defaults:
            if key.endswith('int'):
                return self.prefs.getint(PREFS_SECTION, key)
            elif key.endswith('float'):
                return self.prefs.getfloat(PREFS_SECTION, key)
            elif key.endswith('bool'):
                return self.prefs.getboolean(PREFS_SECTION, key)
            else:
                return self.prefs.get(PREFS_SECTION, key)

    # Sets an attribute in the preferences
    def set(self, key, value):
        # Make sure the key is valid
        if key in self.defaults:
            self.prefs.set(PREFS_SECTION, key, str(value))

    # Reads in preferences from disk
    def load(self):
        self.prefs.read(self.prefs_file)

    # Saves the preferences to disk
    def save(self):
        output = file(self.prefs_file, "wb")
        self.prefs.write(output)
        output.close()

    # Clears all changes that have been made
    def clear(self):
        for key in self.defaults.keys():
            self.prefs.remove_option(PREFS_SECTION, key)

    # Reverts to the default preferences
    def reset(self):
        for key in self.defaults.keys():
            self.set(key, self.defaults[key])
