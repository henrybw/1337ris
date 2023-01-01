#
# 1337ris -- psychedelicmode.py
# Henry Weiss
#
# State class that handles Psychedelic Mode. Derived from the traditional game mode.
#

from .headers import *

# Constants for this wacky mode
FLASH_DELAY = 30
CHECK_DELAY_RANGE = (3000, 8000)
FLOAT_SPEED = 0.1
PTS_PER_MOVE = 10
PTS_PER_LEVEL = 5000  # Since you basically can't get lines in this thing
ADDITIONAL_BOMB_CHANCES = 0.11

class PsychedelicMode(TraditionalMode):
    total_resources = 0
    flash_delay = 0
    check_delay = 0
    floating_blocks = []

    # Checks if we should advance to next level
    def __setattr__(self, attr, value):
        if attr == 'score':
            # Next level?
            if value >= self.level * PTS_PER_LEVEL:
                self.level_clear()

        self.__dict__[attr] = value

    # Setup the flash delay
    def start(self, userdata=None):
        self.floating_blocks = []
        TraditionalMode.start(self, userdata)
        self.flash_delay = FLASH_DELAY

    # In psychedelic mode, blocks will randomly disappear or be added to the tetromino.
    def move_down(self):
        if TraditionalMode.move_down(self):
            # Add some points
            self.score += PTS_PER_MOVE

            if self.current.type == 'B' or self.current.type == 'D':
                return True  # Explosives don't count

            # Randomly add or remove piece
            if random() < 0.5 and len(self.current.blocks) > 0:
                del self.current.blocks[randint(0, len(self.current.blocks) - 1)]
                return True
            else:
                # Pick a block to add to
                if len(self.current.blocks) > 0:
                    x, y = self.current.blocks[randint(0, len(self.current.blocks) - 1)]
                else:
                    x, y = self.current.center_x, self.current.center_y

                # Try adding to all sides, but make sure the block doesn't overlap/collide
                attempts = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
                shuffle(attempts)

                for loc in attempts:
                    if not self.block_will_collide((x + loc[0], y + loc[1])):
                        # Add it to the blocks
                        self.current.blocks.append((x + loc[0], y + loc[1]))
                        break

                return True

        return False

    # Make sure O's can reset
    def reset(self):
        self.current.reset(self.get_next_type(), DEFAULT_START_POINT, True)

    # Psychedelic mode is pretty harsh, so we'll add a healthy dose of bombs
    def get_next_type(self, pop=True):
        if pop and random() < ADDITIONAL_BOMB_CHANCES and len(self.next) > 0:
            self.next.append('B')

        return TraditionalMode.get_next_type(self, pop)

    # In psychedelic mode, the tile grid flashes different colors
    def update(self, elapsed_time):
        TraditionalMode.update(self, elapsed_time)

        # Update floating stuff
        if not self.paused:
            self.check_delay -= elapsed_time

            if self.check_delay <= 0:
                self.check_delay = randint(CHECK_DELAY_RANGE[0], CHECK_DELAY_RANGE[1])

                # Maybe turn some blocks into floating blocks?
                available_blocks = []

                for x in range(GRID_WIDTH):
                    for y in range(GRID_HEIGHT):
                        if self.tile_grid[int(x)][int(y)] != ' ' and not self.is_exploding_block(self.tile_grid[int(x)][int(y)]) and (x, y) not in self.floating_blocks:
                            available_blocks.append((x, y))

                # Pick a random block and make it float
                if len(available_blocks) > 0:
                    x, y = available_blocks[randint(0, len(available_blocks) - 1)]

                    self.floating_blocks.append((x * BLOCK_SIZE[0] + PIXEL_X_OFFSET, (y - self.grid_y_offset) * BLOCK_SIZE[1], self.tile_grid[int(x)][int(y)]))
                    self.tile_grid[int(x)][int(y)] = ' '

                    self.bomb_snd.play()

            # Update the floating blocks
            if len(self.floating_blocks) > 0:
                for i in range(len(self.floating_blocks)):
                    self.floating_blocks[i] = (self.floating_blocks[i][0], self.floating_blocks[i][1] - (FLOAT_SPEED * elapsed_time), self.floating_blocks[i][2])

                for block in self.floating_blocks:
                    # Remove?
                    if block[1] <= -BLOCK_SIZE[1]:
                        del block

            # Psychedelia
            self.flash_delay -= elapsed_time

            if self.flash_delay <= 0:
                self.flash_delay = FLASH_DELAY

                # Go through the grid and switch around the types
                for x in range(GRID_WIDTH):
                    for y in range(GRID_HEIGHT):
                        if self.tile_grid[int(x)][int(y)] != ' ' and self.tile_grid[int(x)][int(y)] != 'D' and not self.is_exploding_block(self.tile_grid[int(x)][int(y)]):
                            self.tile_grid[int(x)][int(y)] = NORMAL_TILES[randint(0, len(NORMAL_TILES) - 1)]

    # Draw the floating blocks too
    def draw_blocks(self, surface):
        for block in self.floating_blocks:
            surface.blit(self.ghost_tiles[block[2]], (block[0], block[1]))

        TraditionalMode.draw_blocks(self, surface)
