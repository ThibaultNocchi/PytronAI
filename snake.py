import random

from grid import Grid

class Snake:
    def __init__(self, snakeId: int, snakeType: str, keys: tuple, color: int, coord: tuple):
        """
        Initializes a snake.
            :param self: 
            :param snakeId:int: ID of the snake. Must be unique (I guess).
            :param snakeType:str: Type of the snake. Either "drone", "human" or "cpu".
            :param keys:tuple: Tuple of four Pyglet keys associated to the movements of the snake.
            :param color:int: Index of a colour from the "colors" variable defined in the body of the code.
            :param coord:tuple: Coordinates of the head in the grid.
        """
        self.id = snakeId
        self.type = snakeType

        if snakeType == 'drone':
            self.min_tail = 0
            self.max_tail = 0
            self.default_tail = 0
        else:
            self.min_tail = 9
            self.max_tail = 299
            self.default_tail = 29

        self.tail = self.default_tail
        self.x, self.y = coord
        self.new_x = self.x
        self.new_y = self.y
        # 0: Up // 1: Right // 2: Down // 3: Left
        self.dir = random.choice((0, 1, 2, 3))
        self.new_dir = self.dir
        self.score = 0
        self.reset = False
        self.up, self.right, self.down, self.left = keys
        self.color = color
        self.dead = 0
        self.kill = 0

        self.cpu_ai = [
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 3),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0),
            (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
             2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 1),
            (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
             3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 2)
        ]

        self.cpu_avoid = [
            (1, 1, 1, 3),
            (2, 2, 2, 0),
            (3, 3, 3, 1),
            (0, 0, 0, 2)
        ]

    def select_new_direction(self, grid: Grid):
        """
        Chooses a new direction for a CPU snake.
        It looks a few cells ahead, for the presence of a player, a wall or a bonus.
        It then changes its direction based on a probability.
            :param self: 
            :param grid:Grid: Grid object to reference to when choosing the direction.
        """
        if self.type == 'drone':
            self.new_dir = random.choice(self.cpu_ai[self.dir])
        elif self.type == 'cpu':
            avoid_detection = random.choice((2, 4, 4, 8, 8, 8))
            avoid_x = self.x
            avoid_y = self.y

            if self.dir == 0:
                avoid_y += avoid_detection
            elif self.dir == 1:
                avoid_x += avoid_detection
            elif self.dir == 2:
                avoid_y -= avoid_detection
            elif self.dir == 3:
                avoid_x -= avoid_detection

            if avoid_y > grid.height - 1:
                avoid_y -= grid.height
            if avoid_x > grid.width - 1:
                avoid_x -= grid.width
            if avoid_y < 0:
                avoid_y += grid.height
            if avoid_x < 0:
                avoid_x += grid.width

            state, age = grid.get_point( # pylint: disable=unused-variable
                avoid_x, avoid_y)

            if state == 0:
                self.new_dir = random.choice(self.cpu_ai[self.dir])
            elif state >= 1 and state <= 20:
                self.new_dir = random.choice(self.cpu_avoid[self.dir])
            elif state >= 21 and state <= 40:
                self.new_dir = self.dir
            elif state == 255:
                self.new_dir = random.choice(self.cpu_avoid[self.dir])

    def move(self, grid: Grid):
        """
        Moves the snake into its new position and checks if it is outside the boundaries.
            :param self: 
            :param grid:Grid: Grid to reference against.
        """
        if self.dir == 0:
            if self.y < grid.height - 1:
                self.new_y += 1
            else:
                self.new_y = 0
        elif self.dir == 1:
            if self.x < grid.width - 1:
                self.new_x += 1
            else:
                self.new_x = 0
        elif self.dir == 2:
            if self.y > 0:
                self.new_y -= 1
            else:
                self.new_y = grid.height - 1
        elif self.dir == 3:
            if self.x > 0:
                self.new_x -= 1
            else:
                self.new_x = grid.width - 1

    def check_collision(self, grid: Grid, snakesArray: list):
        """
        Checks if the snake if collisionning into something.
            :param self: 
            :param grid:Grid: Grid to reference against.
        """
        # global snakesArray
        if self.reset:
            pass
        state, age = grid.get_point( # pylint: disable=unused-variable
            self.x, self.y)
        if state == 0:  # If empty
            grid.set_point(self.x, self.y, (self.id, 0))
        elif state >= 1 and state <= 20:  # Snake
            if self.type == 'drone':
                grid.set_point(self.x, self.y, (self.id, 0))
            else:
                self.reset = True
                self.tail = self.default_tail
                self.dead += 1
                if state != self.id:
                    snakesArray[state-1].kill += 1
        elif state >= 21 and state <= 40:  # Bonus
            grid.set_point(self.x, self.y, (self.id, 0))
            if state == 21:  # Good bonus
                if self.tail != self.max_tail:
                    self.score += 1
                    self.tail += 10
                    if self.tail > self.max_tail:
                        self.tail = self.max_tail
            elif state == 22:  # Mild bonus
                if self.tail != self.min_tail:
                    self.score += 2
                    self.tail -= 5
                    if self.tail < self.min_tail:
                        self.tail = self.min_tail
        elif state == 255:  # Wall
            self.reset = True
            self.tail = self.default_tail
            self.dead += 1
