#
# 1337ris -- crosscutmode.py
# Henry Weiss
#
# State class that handles Cross-Cut Mode.
#

from headers import *

CENTER_START = (GRID_WIDTH / 2 - 1, (GRID_HEIGHT - GRID_Y_OFFSET) / 2)
INITIAL_MOVE_TIME = 10000
INCREMENT = 300
MIN_MOVE_TIME = 500  # Below this, it's probably impossible

class CrossCutMode(TraditionalMode):
    total_resources = 0
    
    # Changes some of the default values
    def __init__(self, main, size=(GRID_WIDTH, GRID_HEIGHT - GRID_Y_OFFSET)):
        TraditionalMode.__init__(self, main)
        self.size = size
        self.width, self.height = self.size
        self.grid_y_offset = 0
    
    # Tile delay is binded to the sliding delay in this mode (since we're always sliding)
    def __setattr__(self, attr, value):
        if attr == 'tile_delay':
            self.slide_delay = value
        
        self.__dict__[attr] = value
    
    # Changes some default values that don't have to be changed before the start method
    def start(self, userdata=None):
        TraditionalMode.start(self, userdata)
        self.tile_delay = INITIAL_MOVE_TIME
        self.tile_delay_increment = INCREMENT
        self.min_tile_delay = MIN_MOVE_TIME
        
    # Take out the "auto move down" property
    def update_tetromino(self, elapsed_time):
        # Make sure we're always "sliding" -- meaning we can just plop down wherever on the field
        self.sliding = True
        
        # Is it time to lock in?
        if self.time_since_last_move > self.tile_delay:
            self.add_tetromino_to_field()
    
    # Takes the current tetromino and incorporates it into the playing field
    def add_tetromino_to_field(self):
        if self.current.type == 'B':
            # Insert explosive into grid
            self.tile_grid[self.current.center_x][self.current.center_y] = '1'
            
            self.explode_blocks(self.current.center_y, SCORE_BOMB, TILES_BOMBED_FOR_LINE)
            self.bomb_snd.play()
            
            # Update some stuff
            self.blocks_cleared_delay = BLOCKS_CLEARED_DELAY
            self.clear_event = EVENT_BOMB
        else:
            for block in self.current.get_blocks():
                self.tile_grid[block[0]][block[1]] = self.current.type
            
            self.lock_snd.play()
            
            # Check if we cleared any lines
            self.handle_line_clears(True)
        
        # Prevent inadvertant movements for the next piece
        if self.clear_event == EVENT_NONE:
            self.drop_delay = DROP_DELAY
        
        self.time_since_last_move = 0
    
    # Overridden to move lines up if they're in the top half of the screen
    def adjust_full_lines(self):
        lines_cleared = 0
        
        # Make sure to check the top and bottom in the right direction (bottom half
        # is as normal, check lines from top to bottom, but top half is reversed).
        for i in range(self.height / 2, -1, -1) + range(self.height / 2, self.height):
            if self.full_lines[i]:
                lines_cleared += 1
                self.full_lines[i] = False
                
                # Check a different range based on where the line clear occurred,
                # since the lines shift in opposite directions depending on the
                # half of the screen they're in.
                if i >= self.height / 2:
                    interval = range(i, self.height / 2 - 1, -1)
                    copy_y = -1
                else:
                    interval = range(i, self.height / 2)
                    copy_y = 1
                
                # Move each line surrounding it, depending on where it is in the screen
                for x in range(self.width):
                    for y in interval:
                        # If we moved everything down, the middle line should "shift down" by
                        # copying a blank line instead the first line of whatever is in the
                        # other half of the screen, which prevents unnecessary block duplication.
                        if y == self.height / 2:
                            self.tile_grid[x][y] = ' '
                        elif y >= 0:  # Accounts for the off-by-one adjustment in the range
                            self.tile_grid[x][y] = self.tile_grid[x][y + copy_y]
    
        return lines_cleared
    
    # Overridden for basically the same reasons why adjust_full_lines was.
    def explode_blocks(self, y_offset, score_per_block, blocks_per_line):
        blocks_cleared = 0
        
        # Top half/bottom half will change the direction of the explosion
        if y_offset >= self.height / 2:
            interval = range(y_offset, self.height / 2, -1)
        else:
            interval = range(y_offset, self.height / 2 - 1)
        
        for y in interval:
            for x in range(self.width):
                if self.tile_grid[x][y] != ' ':
                    # Award some points
                    self.score += score_per_block * self.level
                    
                    # And maybe a line too...
                    blocks_cleared += 1
                    
                    if blocks_cleared > blocks_per_line:
                        self.lines += 1
                        blocks_cleared = 0
                    
                    self.tile_grid[x][y] = '1'  # Make affected tile explode
    
    # Makes the tetromino start from the center instead of the top
    def reset(self):
        self.current.reset(self.get_next_type(), CENTER_START)
    
    # Remap the keys
    def handle_game_input(self, keycode):
        # Check for movement and stuff
        if keycode == self.main.prefs_controller.get(MOVE_LEFT_KEY) and self.drop_delay <= 0:
            self.move_left()
        elif keycode == self.main.prefs_controller.get(MOVE_RIGHT_KEY) and self.drop_delay <= 0:
            self.move_right()
        elif keycode == self.main.prefs_controller.get(ROTATE_RIGHT_KEY) or keycode == self.main.prefs_controller.get(ROTATE_LEFT_KEY):
            if keycode == self.main.prefs_controller.get(ROTATE_RIGHT_KEY):
                self.rotate(DEFAULT_ROTATION)
            else:
                self.rotate(-DEFAULT_ROTATION)
        elif (keycode == self.main.prefs_controller.get(SPEEDUP_KEY) or keycode == self.main.prefs_controller.get(DROP_KEY)) and self.drop_delay <= 0:
            if keycode == self.main.prefs_controller.get(SPEEDUP_KEY):
                dy = 1
            else:
                # Move up this time
                dy = -1
            
            self.current.center_y += dy
            
            # Check for collisions and correct if necessary
            collided = False
            
            for block in self.current.get_blocks():
                if self.block_will_collide(block):
                    collided = True
            
            if collided:
                self.current.center_y -= dy
                self.add_tetromino_to_field()
            
        elif keycode == self.main.prefs_controller.get(DETONATE_KEY):
            self.detonate()
    
    # Draws the ghost version of the tetromino depending on which half of the screen it's in
    def draw_ghost_piece(self, surface):
        y_offset = 0
        save_y = self.current.center_y
        
        # Down or up?
        if self.current.center_y >= self.height / 2:
            dy = 1
        else:
            dy = -1
        
        # Move the tetromino down until it collides
        collided = False
        
        while not collided:
            for block in self.current.get_blocks():
                if self.block_will_collide(block):
                    collided = True
            
            if not collided:
                self.current.center_y += dy
        
        # Calculate the offset and restore the old y
        y_offset = self.current.center_y - save_y - dy
        self.current.center_y = save_y
        
        # Draw the blocks
        if y_offset != 0:
            for block in self.current.get_blocks():
                self.draw_block(surface, self.current.type, (block[0], block[1] + y_offset), True)