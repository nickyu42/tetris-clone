"""
A simple tetris clone powered by pygame and numpy

The game can be easily re-sized by changing BLOCK

The tetris pieces are in a 4 by 4 array
Each piece has 4 blocks and each tuple is the location of 1 block

t = [(1, 1), (1, 2), (1, 3), (2, 2)]

   0  1  2  3
0 [0, 0, 0, 0]
1 [0, 1, 1, 1]
2 [0, 0, 1, 0]
3 [0, 0, 0, 0]

TODO: - add ghost piece
      - add sound effects for moving, dropping,
        rotation and line clear
      - improve random block choice
      - clean up everything :/
"""

import numpy as np
import pygame as pg
import random
import sys
import os

BLOCK = 20
WIDTH = 16 * BLOCK
HEIGHT = 22 * BLOCK
SIZE = (WIDTH, HEIGHT)
FPS = 60

PIECES = {
    "o": [(1, 1), (1, 2), (2, 1), (2, 2)],
    "i": [(1, 0), (1, 1), (1, 2), (1, 3)],
    "s": [(1, 2), (1, 3), (2, 1), (2, 2)],
    "z": [(1, 1), (1, 2), (2, 2), (2, 3)],
    "l": [(1, 1), (1, 2), (1, 3), (2, 1)],
    "j": [(1, 1), (1, 2), (1, 3), (2, 3)],
    "t": [(1, 1), (1, 2), (1, 3), (2, 2)]
}

TYPES = ["o", "i", "s", "z", "l", "j", "t"]

COLORS = {
    "i": (0, 128, 255),     # light blue
    "j": (0, 0, 255),       # blue
    "l": (255, 128, 0),     # orange
    "o": (255, 255, 0),     # yellow
    "s": (0, 255, 0),       # green
    "t": (127, 0, 255),     # purple
    "z": (255, 0, 0),       # red
    "w": (255, 255, 255),   # white
    "b": (0, 0, 0)          # black
}


class Board:
    board = np.zeros((22, 10))
    background = pg.Surface([WIDTH, HEIGHT])

    def __init__(self):
        Board.board = np.array(Board.board, dtype=object)
        Board.background.fill(COLORS["b"])

        # draw borders
        for y in range(21):
            pg.draw.rect(Board.background, COLORS["w"],
                             [0, y * BLOCK, BLOCK, BLOCK], 1)
            pg.draw.rect(Board.background, COLORS["w"],
                             [10 * BLOCK + BLOCK, y * BLOCK, BLOCK, BLOCK], 1)

        for x in range(12):
            pg.draw.rect(Board.background, COLORS["w"],
                             [x * BLOCK, 0, BLOCK, BLOCK], 1)
            pg.draw.rect(Board.background, COLORS["w"],
                             [x * BLOCK, 20 * BLOCK + BLOCK, BLOCK, BLOCK], 1)

    def display_text(self, text, position, color):
        x, y = position
        font = pg.font.Font(r"C:\Windows\Fonts\vgafix.fon", int(BLOCK))
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        text_rect.center = (x, y)
        screen.blit(text_surf, text_rect)

    def check(self):
        """Checks for full lines and clears them"""
        full_lines = [i for i, line in enumerate(Board.board) if 0 not in line]
        if full_lines:
            for line in full_lines:
                Board.board = np.delete(Board.board, line, axis=0)
                Board.board = np.insert(Board.board, 0, [0 for i in range(10)], axis=0)
            return len(full_lines)
        else:
            return False

    def update_screen(self):
        """Update the inner game board"""
        # clear the inner board
        screen.blit(Board.background, [BLOCK, BLOCK, 10 * BLOCK, 20 * BLOCK],
                    [BLOCK, BLOCK, 10 * BLOCK, 20 * BLOCK])

        # draw the board onto the screen
        for y, row in enumerate(Board.board[1:]):
            for x, char in enumerate(row):
                if char != 0.0:
                    # draw white border around block
                    pg.draw.rect(screen, COLORS["w"],
                                     [x * BLOCK + BLOCK, y * BLOCK, BLOCK, BLOCK], 1)
                    # draw the block itself
                    pg.draw.rect(screen, COLORS[char],
                                     [x * BLOCK + BLOCK + 1, y * BLOCK + 1, BLOCK - 2, BLOCK - 2])

        # clear the head
        screen.blit(Board.background, [BLOCK, 0, 10 * BLOCK, BLOCK],
                    [BLOCK, 0, 10 * BLOCK, BLOCK])

    def update_score(self, score, lines):
        """Clear and display new score"""
        screen.blit(Board.background, [12 * BLOCK, BLOCK, 4 * BLOCK, 5 * BLOCK],
                    [12 * BLOCK, BLOCK, 4 * BLOCK, 5 * BLOCK])

        self.display_text("SCORE".format(score), (14 * BLOCK, BLOCK), COLORS["w"])
        self.display_text(str(score), (14 * BLOCK, 2 * BLOCK), COLORS["l"])
        self.display_text("LINES".format(score), (14 * BLOCK, 4 * BLOCK), COLORS["w"])
        self.display_text(str(lines), (14 * BLOCK, 5 * BLOCK), COLORS["l"])

    def update_next(self, type):
        """Draw on the right side the upcoming tetris block"""
        # clear area
        screen.blit(Board.background, [12 * BLOCK, 8 * BLOCK, 4 * BLOCK, 4 * BLOCK],
                    [12 * BLOCK, 8 * BLOCK, 4 * BLOCK, 5 * BLOCK])

        small_block = BLOCK / 2
        # set the margin depending on the width of the block
        if type == "o":
            margin = (4 * BLOCK - 2 * small_block) / 2
        elif type == "l":
            margin = (4 * BLOCK - 4 * small_block) / 2
        else:
            margin = (4 * BLOCK - 3 * small_block) / 2

        for y, x in PIECES[type]:
            pg.draw.rect(screen, COLORS["w"],
                         [12 * BLOCK + margin + (x - 1) * small_block, 8 * BLOCK + y * small_block,
                         small_block, small_block], 1)

            pg.draw.rect(screen, COLORS[type],
                         [12 * BLOCK + margin + (x - 1) * small_block + 1, 8 * BLOCK + y * small_block + 1,
                         small_block - 2, small_block - 2])

    def clear(self):
        Board.board[:, :] = 0.0


class Block:
    def __init__(self, block_type):
        self.type = block_type
        self.color = COLORS[block_type]

        # the center of the block
        self.pivet = np.array([5, 2])

        # the position of each block in the board
        self.position = []
        # create the four rectangles of the block
        for y, x in PIECES[block_type]:
            self.position.append([x + 3, y + 1])
        else:
            self.position = np.array(self.position)

        self.create_bl()

    def create_bl(self):
        """Update the block position in the board array"""
        for pos in self.position:
            Board.board[pos[1], pos[0]] = self.type

    def clear_bl(self):
        """Remove the block from the board array"""
        for pos in self.position:
            Board.board[pos[1], pos[0]] = 0

    def collide(self, new_position):
        """Checks if block will collide with wall or other blocks"""
        """return True if it does"""
        for x, y in new_position:
            # checks if a block leaves the board boundary
            if (
                x < 0 or
                x > 9 or
                y > 21
            ):
                return True
            # checks if there is already a block
            # on that position
            elif (
                            Board.board[y, x] != 0.0 and
                            [x, y] not in self.position
            ):
                return True
        else:
            return False

    def move_bl(self, direction="DOWN"):
        if direction == "DOWN":
            x_move = 0
            y_move = 1
        else:
            x_move = -1 if direction == "LEFT" else 1
            y_move = 0

        new_position = [[x + x_move, y + y_move] for x, y in self.position]

        if not self.collide(new_position):
            self.clear_bl()
            self.position = new_position
            self.pivet += [x_move, y_move]
            self.create_bl()

    def rotate_bl(self, direction="CW"):
        # CW = clockwise
        # CCW = counter clockwise
        new_position = []

        # rotational vector
        r = [1, -1] if direction == "CW" else [-1, 1]

        for pos in self.position:
            vector = pos - self.pivet
            vector *= r
            vector = vector[::-1]
            new_position.append((self.pivet + vector).tolist())

        if self.collide(new_position):
            for x, y in new_position:
                if x < 0:
                    new_position = [[x + 1, y] for x, y in new_position]
                    self.pivet += [1, 0]
                elif x > 9:
                    new_position = [[x - 1, y] for x, y in new_position]
                    self.pivet += [-1, 0]

        self.clear_bl()
        if self.type != "o":
            self.position = new_position
        self.create_bl()

    def is_active(self):
        """Checks if the block can still move down"""
        new_position = [[x, y + 1] for x, y in self.position]
        if self.collide(new_position):
            return False
        else:
            return True

    def drop(self):
        while self.is_active():
            self.move_bl("DOWN")

    @classmethod
    def check(cls, type):
        """Checks if the new block can be placed at the start position"""
        temp_position = []
        for y, x in PIECES[type]:
            temp_position.append([x + 3, y + 1])

        for pos in temp_position:
            if Board.board[pos[1] + 1, pos[0]] != 0.0:
                return False
        else:
            bl = cls(type)
            return bl


class Control:
    """Handles game logic and player input"""
    def __init__(self):
        self.done = False

        self.game_board = Board()

        self.next_block_type = random.choice(TYPES)
        self.bl = Block(self.next_block_type)
        self.next_block_type = random.choice(TYPES)

        screen.blit(Board.background, (0, 0))
        self.game_board.display_text("Next", (14 * BLOCK, 7 * BLOCK), COLORS["i"])
        self.game_board.update_score(0, 0)
        self.game_board.update_next(self.next_block_type)
        self.game_board.update_screen()

        self.level = 1
        self.score = 0
        self.lines = 0
        self.active_counter = 0          # counts how many times a block is stuck
        self.pressed_keys = []
        self.now = None
        self.ticks_taken = None
        self.gravity = None

        self.last = pg.time.get_ticks()  # time since last action
        self.seconds = int(self.last)    # amount of seconds since last action

    def event_handler(self):
        """Pygame event handler"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.bl.drop()
                    self.active_counter = self.level
                elif event.key == pg.K_RIGHT:
                    self.pressed_keys.append("RIGHT")
                elif event.key == pg.K_LEFT:
                    self.pressed_keys.append("LEFT")
                elif event.key == pg.K_DOWN:
                    self.pressed_keys.append("DOWN")
                elif event.key == pg.K_z:
                    self.bl.rotate_bl("CCW")
                elif event.key == pg.K_x:
                    self.bl.rotate_bl("CW")

            elif event.type == pg.KEYUP:
                if event.key == pg.K_RIGHT:
                    self.pressed_keys.remove("RIGHT")
                elif event.key == pg.K_LEFT:
                    self.pressed_keys.remove("LEFT")
                elif event.key == pg.K_DOWN:
                    self.pressed_keys.remove("DOWN")

    def update(self):
        """Game logic"""
        # create new block and erase full lines when block cant move
        if self.active_counter >= self.level + 1:
            # check if there are full lines
            # and update score, line counter
            full_lines = self.game_board.check()
            if full_lines:
                self.lines += full_lines
                self.score += [40, 100, 300, 1200, 2400, 3600][self.level] * full_lines

            # create new block
            self.bl = Block.check(self.next_block_type)
            self.score += 10

            # if a block cant be created
            # trigger game-over state
            if not self.bl:
                self.game_board.clear()
                self.score, self.lines, self.active_counter = 0, 0, 0
                self.level = 1
                self.bl = Block(self.next_block_type)

            # new block cant be the same as the previous
            temp = random.choice(TYPES)
            while temp == self.next_block_type:
                temp = random.choice(TYPES)
            self.next_block_type = temp

            self.active_counter = 0
            self.game_board.update_score(self.score, self.lines)
            self.game_board.update_next(self.next_block_type)

        self.now = pg.time.get_ticks()
        # gravity speed is based on the current level
        self.gravity = (1000 / 60) / (self.level * 8 / 512)
        self.ticks_taken = self.now - self.last

    def draw(self):
        """Update the screen"""
        if self.now - self.seconds >= 100 and self.pressed_keys:
            self.seconds = self.now
            self.bl.move_bl(self.pressed_keys[0])

        if self.ticks_taken >= self.gravity:
            self.last = self.now
            self.bl.move_bl("DOWN")

            if not self.bl.is_active():
                self.active_counter += 1

    def run(self):
        """Main loop"""
        clock = pg.time.Clock()

        while not self.done:
            self.event_handler()
            self.update()
            self.draw()
            self.game_board.update_screen()
            pg.display.update()
            clock.tick(FPS)

if __name__ == '__main__':
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.mixer.pre_init()
    pg.init()
    pg.display.set_caption("tetris")

    # start music
    pg.mixer.init()
    pg.mixer.music.load("theme.mp3")
    pg.mixer.music.set_volume(0.2)
    pg.mixer.music.play(-1)

    App = Control()
    App.run()

    pg.quit()
    sys.exit()
