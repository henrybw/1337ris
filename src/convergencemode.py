#
# 1337ris -- convergencemode.py
# Henry Weiss
#
# State class that handles Convergence Mode. Derived from the traditional game mode.
#

from headers import *

class ConvergenceMode(TraditionalMode):
    total_resources = 0

    # This is the heart and soul of Convergence
    merging = True
    got_left_type = False  # Alternates between the left and right colors for fusion
    left = Tetromino()
    right = Tetromino()

    # Generates a left and right piece
    def reset(self):
        types = (self.get_next_type(), self.get_next_type())

        # Woops, make this a normal piece
        if 'B' in types or 'D' in types:
            self.merging = False

            if types[0] == 'B' or types[0] == 'D':
                self.current.reset(types[0])
            else:
                self.current.reset(types[1])

            return

        self.merging = True

        # Generate new types
        self.left.reset(types[0], (-1, 3))
        self.right.reset(types[1], (GRID_WIDTH, 3))

        # Put them on the left/right-most part of the screen
        can_move = False

        while not can_move:
            for block in self.left.get_blocks():
                if not self.block_will_collide(block):
                    can_move = True
                else:
                    self.left.center_x += 1

        can_move = False

        while not can_move:
            for block in self.right.get_blocks():
                if not self.block_will_collide(block):
                    can_move = True
                else:
                    self.right.center_x -= 1

    # If we're merging, rotate both the left and right pieces
    def rotate(self, angle):
        if self.merging:
            if self.clear_event == EVENT_NONE:
                self.rotate_snd.play()
                self.left.rotate(angle)
                self.right.rotate(angle)

                # Check if we're going to collide
                if self.left_right_collision():
                    self.left.rotate(-angle)  # Revert the rotation!
                    self.right.rotate(-angle)  # Revert the rotation!
                    return
        else:
            TraditionalMode.rotate(self, angle)

    # Can't move left until we've merged the pieces
    def move_left(self):
        if not self.merging:
            return TraditionalMode.move_left(self)

    # Can't move right until we've merged the pieces
    def move_right(self):
        if not self.merging:
            return TraditionalMode.move_right(self)

    # If we're merging, this moves the two pieces towards each other.
    def move_down(self):
        if self.merging:
            # Should we merge?
            if self.left_right_collision(True):
                # Determine the new type
                if self.got_left_type:
                    new_type = self.left.type
                else:
                    new_type = self.right.type

                self.got_left_type = not self.got_left_type

                # Create the current piece
                self.current = FusionTetromino(new_type, self.left, self.right)

                # And we're not merging now
                self.merging = False

                # Play the clicky sound
                self.lock_snd.play()

                # And delay a bit
                self.drop_delay = DROP_DELAY

            else:
                self.right.center_x -= 1
                self.left.center_x += 1

            return self.merging

        else:
            return TraditionalMode.move_down(self)

    # Game over works a little differently in Convergence
    def check_game_over(self):
        if self.merging:
            for block in self.left.get_blocks():
                if self.block_will_collide(block):
                    self.game_over = True  # :(
                    self.main.fadeout_sound()
                    return

            for block in self.right.get_blocks():
                if self.block_will_collide(block):
                    self.game_over = True  # :(
                    self.main.fadeout_sound()
                    return
        else:
            TraditionalMode.check_game_over(self)

    # Checks if the left/right pieces collided
    def left_right_collision(self, test_potential_collision=False):
        # First check if the center_x's are past each other
        if self.left.center_x >= self.right.center_x:
            return True

        # Check if any of the blocks are colliding
        for left_block in self.left.get_blocks():
            for right_block in self.right.get_blocks():
                if Rect(left_block, (1, 1)).colliderect(Rect(right_block, (1, 1))):
                    return True

        return False

    # Clearing lines via dynamite/bombs should be easier, since
    # this mode is rather harsh.
    def clear_blocks(self, y_offset, score_per_block, blocks_per_line):
        blocks_per_line /= 2
        TraditionalMode.clear_blocks(self, y_offset, score_per_block, blocks_per_line)

    # Draws the left/right pieces if merging
    def draw_current_tetromino(self, surface):
        if self.merging:
            # Draw the currently moving blocks
            for block_loc in self.left.get_blocks():
                self.draw_block(surface, self.left.type, block_loc)

            for block_loc in self.right.get_blocks():
                self.draw_block(surface, self.right.type, block_loc)

        else:
            TraditionalMode.draw_current_tetromino(self, surface)

    # In Convergence, preview is kinda...useless
    def draw_preview(self, surface):
        pass
