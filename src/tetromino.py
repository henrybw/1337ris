#
# 1337ris -- tetromino.py
# Henry Weiss
#
# Represents the tetromino that is currently in the player's control (the one
# that is falling).  This keeps track of a 'center' tile (which the tetromino
# rotates around), with the other tiles being stored relative to the center
# tile.  Tetromino types (center tile is a *):
#
#  I      J     L     O     S     T     Z  
#        #       #    ##    ##   #*#   ##
# ##*#   #*#   #*#    *#   #*     #     *#
# 
# A 'B' tile is a bomb, while a 'D' tile is dynamite.
#

from headers import *

# Where all tetrominoes spawn from (well, most of them)
DEFAULT_START_POINT = (GRID_WIDTH / 2 - 1, 3)

class Tetromino:
    center_x, center_y = DEFAULT_START_POINT
    type = ''  # I, J, L, T, etc.
    blocks = []  # Pairs of coordinates (x, y)
    orientation = 0  # Primarily for the I tetromino
    
    # Intercepts changes to the center block location to update
    # the other blocks in the block list
    def __setattr__(self, attr, value):
        if attr.startswith("center_"):
            dx, dy = 0, 0
            
            if attr == "center_x":
                dx = value - self.center_x
            elif attr == "center_y":
                dy = value - self.center_y
            
            for i in range(len(self.blocks)):
                self.blocks[i] = (self.blocks[i][0] + dx, self.blocks[i][1] + dy)
        
        self.__dict__[attr] = value
    
    # Called whenever a new tetromino appears from the top. Setting
    # rotate_all to True lets the O tile rotate, even though it usually
    # shouldn't.
    def reset(self, type, start=DEFAULT_START_POINT, rotate_all=False):
        self.type = type
        self.rotate_all = rotate_all
        self.orientation = 0
        self.center_x, self.center_y = start
        
        # Adjust to make some tetrominoes centered
        if self.type == 'I' or self.type == 'T' or self.type == 'B' or self.type == 'D':
            self.center_y -= 1
        if self.type == 'I' or self.type == 'B' or self.type == 'D':
            self.center_x += 1
        
        # Now add the outside blocks
        self.blocks = []
        
        if self.type == 'I':
            self.blocks.append((self.center_x - 1, self.center_y))
            self.blocks.append((self.center_x + 1, self.center_y))
            self.blocks.append((self.center_x - 2, self.center_y))
        elif self.type == 'J':
            self.blocks.append((self.center_x - 1, self.center_y - 1))
            self.blocks.append((self.center_x - 1, self.center_y))
            self.blocks.append((self.center_x + 1, self.center_y))
        elif self.type == 'L':
            self.blocks.append((self.center_x + 1, self.center_y - 1))
            self.blocks.append((self.center_x + 1, self.center_y))
            self.blocks.append((self.center_x - 1, self.center_y))
        elif self.type == 'O':
            self.blocks.append((self.center_x + 1, self.center_y))
            self.blocks.append((self.center_x, self.center_y - 1))
            self.blocks.append((self.center_x + 1, self.center_y - 1))
        elif self.type == 'S':
            self.blocks.append((self.center_x + 1, self.center_y - 1))
            self.blocks.append((self.center_x, self.center_y - 1))
            self.blocks.append((self.center_x - 1, self.center_y))
        elif self.type == 'T':
            self.blocks.append((self.center_x, self.center_y + 1))
            self.blocks.append((self.center_x - 1, self.center_y))
            self.blocks.append((self.center_x + 1, self.center_y))
        elif self.type == 'Z':
            self.blocks.append((self.center_x - 1, self.center_y - 1))
            self.blocks.append((self.center_x, self.center_y - 1))
            self.blocks.append((self.center_x + 1, self.center_y))
    
    # Rotates the tetromino by a certain angle. If the specified
    # angle is not a multiple of 90, it will round down to the
    # previous multiple of 90 (e.g. passing 95 will rotate it 90
    # degrees). You can also specify a negative angle, which will
    # rotate it counter-clockwise.
    def rotate(self, angle):
        if not self.can_rotate(self.type):
            return
        
        # Get an angle within the four quadrants
        angle = (angle - angle % 90) % 360
        
        # Rotate the blocks around the center
        for i in range(angle / 90):
            for i in range(len(self.blocks)):
                relative_x = self.blocks[i][0] - self.center_x
                relative_y = self.blocks[i][1] - self.center_y
                
                # (x, y) rotated 90 degrees clockwise => (-y, x)
                self.blocks[i] = (-relative_y + self.center_x, relative_x + self.center_y)
            
            # Update the orientation
            self.orientation = (self.orientation + 90) % 360
            
            # Correct for the I tile
            if self.type == 'I':
                self.correct_for_i_tile()
    
    # Certain pieces don't rotate, so don't let them rotate
    def can_rotate(self, type):
        return (self.rotate_all or type != 'O') and type != 'B' and type != 'D'
    
    # Since 'I' tetrominoes don't really have a "center block,"
    # switching the location of the center block every rotation
    # will give the illusion that it's rotating around its center.
    def correct_for_i_tile(self):
        if self.orientation == 0:
            self.center_x += 1
        elif self.orientation == 90:
            self.center_y += 1
        elif self.orientation == 180:
            self.center_x -= 1
        elif self.orientation == 270:
            self.center_y -= 1
    
    # Gets all the blocks plus the center block in one nice list
    def get_blocks(self):
        return [(self.center_x, self.center_y)] + self.blocks
    
    # Returns the dimensions of this tetromino
    def get_size(self, in_pixels=False):
        # Find left and rightmost blocks
        left_x, right_x, up_y, down_y = self.get_extremities()
        
        # Scale if necessary
        if in_pixels:
            return (abs(left_x - right_x) * BLOCK_SIZE[0] + BLOCK_SIZE[0], abs(up_y - down_y) * BLOCK_SIZE[1] + BLOCK_SIZE[1])
        else:
            return (abs(left_x - right_x) + 1, abs(up_y - down_y) + 1)
    
    # Returns left-most, right-most, top-most, and bottom-most block coordinates
    def get_extremities(self):
        blocks = self.get_blocks()
        
        left_x, right_x = GRID_WIDTH, 0
        up_y, down_y = GRID_HEIGHT, 0
        
        for block in blocks:
            left_x = min(left_x, block[0])
            right_x = max(right_x, block[0])
            up_y = min(up_y, block[1])
            down_y = max(down_y, block[1])
        
        return (left_x, right_x, up_y, down_y)