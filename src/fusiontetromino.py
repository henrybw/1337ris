#
# 1337ris -- fusiontetromino.py
# Henry Weiss
#
# Subclass of a normal tetromino that allows it to fuse with another tetromino.
#

from .headers import *

class FusionTetromino(Tetromino):
    # Adds the blocks of another tetromino to this tetromino. Since
    # there are two tetrominoes, you'll need to specify the new type.
    def __init__(self, new_type, left, right):
        self.type = new_type

        # Gather all the blocks together first
        blocks = left.get_blocks() + right.get_blocks()

        # Determine the centermost block and use that
        # for rotation.
        left_x, right_x, up_y, down_y = self.get_extremities()

        avg_x = (left_x + right_x) / 2
        avg_y = (up_y + down_y) / 2

        # Now find the block nearest to the average
        dists = []

        for block in blocks:
            dists.append((abs(avg_x - block[0]), abs(avg_y - block[1]), block))

        dists.sort()

        # Make that the center block
        self.center_x = dists[0][2][0]
        self.center_y = dists[0][2][1]

        # And append the rest of the blocks
        self.blocks = []

        for block in blocks:
            if block not in self.blocks and not (block[0] == self.center_x and block[1] == self.center_y):
                self.blocks.append(block)

    # Since we have no idea what this piece will be, we'll let anything rotate
    def can_rotate(self, type):
        return True

    # See above
    def correct_for_i_tile(self):
        pass
