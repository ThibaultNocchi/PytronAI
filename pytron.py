# Source code released under gpl v3 licence, see COPYING file

from pyglet import window, clock, image
from pyglet.gl import *  # pylint: disable=unused-wildcard-import
from pyglet.window import key
from random import choice, randint
from pyglet import font
from pyglet.font import Text

# Grid
class Grid:

    def __init__(self, width: int, height: int, bonus_timeout: int = 74):
        self.width = width
        self.height = height
        # 0,0 is bottom left.
        #(id, age)
        # id = 0          : empty
        # id >= 1 e <=20  : snake (human, cpu, drone)
        # id >=21 e <=40  : bonus
        # id = 255        : wall
        self.data = [[(0, 0)]*self.width for i in range(self.height)]
        self.snakes = []
        self.bonus_timeout = bonus_timeout
        self.bonus = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 21, 21)

    def new_snake(self, snakeType: str, keys: tuple, color: int):
        """
        Adds a new snake at a random position to the grid.
            :param self: 
            :param snakeId:int: ID of the snake.
            :param snakeType:str: Type of the snake.
            :param keys:tuple: Keys to move the snake.
            :param color:int: Color of the snake, as per the "colors" variable.
        """   
        newSnake = Snake(len(self.snakes) + 1, snakeType, keys, color, self.random_point())
        self.snakes.append(newSnake)
        self.set_point(newSnake.x, newSnake.y, (newSnake.id, 0))

    def new_wall(self, bottom_left: tuple, top_right: tuple):
        """
        Adds a new wall to the grid.
            :param self: 
            :param bottom_left:tuple: X and Y position of the bottom left.
            :param top_right:tuple: X and Y position of the top right.
        """   
        for x in range(bottom_left[0], top_right[0] + 1):
            for y in range(bottom_left[1], top_right[1] + 1):
                try:
                    self.data[y][x] = (255, 0)
                except IndexError:
                    pass

    def get_point(self, x: int, y: int) -> tuple:
        """
        Get the value associated to a coordinate into the grid.
            :param self: 
            :param x:int: X coord.
            :param y:int: Y coord.
        """
        return self.data[y][x]

    def set_point(self, x: int, y: int, value: tuple):
        """
        Set a value to a coordinate into the grid.
            :param self: 
            :param x:int: X coord.
            :param y:int: Y coord.
            :param value:tuple: Value to set.
        """
        self.data[y][x] = value

    def reset_point(self, x: int, y: int):
        """
        Reset the value associated to the coordinates.
            :param self: 
            :param x:int: X coord.
            :param y:int: Y coord.
        """
        self.data[y][x] = (0, 0)

    def random_point(self):
        """
        Returns a tuple of random coordinates with nothing in it at this position.
            :param self: 
        """
        bx = randint(0, self.width - 1)
        by = randint(0, self.height - 1)
        for y in range(self.height):
            by = (by + y) % self.height
            for x in range(self.width):
                bx = (bx + x) % self.width
                if self.data[by][bx] == (0, 0):
                    return (bx, by)
        return None, None

    def show_bonus(self):
        """
        Adds (or not) a bonus on the grid.
            :param self: 
        """
        b = choice(self.bonus)
        if b != 0:
            bx, by = self.random_point()
            self.set_point(bx, by, (b, 0))

    def update_grid(self, single_life: bool, draw_grid : bool = False, colors : list = [], squares_verts : list = []):
        
        for i in range(len(self.snakes)):

            if not single_life or not self.snakes[i].reset or self.snakes[i].type == "drone":

                # Choosing new direction for CPUs, and moving snakes into their new position.
                snake1 = self.snakes[i]
                snake1.reset = False
                snake1.select_new_direction(self)
                snake1.dir = snake1.new_dir
                snake1.move(self)

                # Checking for head to head collision with previously moved snakes.
                for j in range(i):
                    snake2 = self.snakes[j]
                    if snake1.id != snake2.id:
                        if snake1.new_x == snake2.new_x and snake1.new_y == snake2.new_y:
                            snake1.reset = True
                            snake2.reset = True
                            snake1.reset_tail()
                            snake2.reset_tail()
                            snake1.dead += 1
                            snake2.dead += 1
                            if single_life:
                                if snake2.type != "drone":
                                    snake2.remove_snake()
                                if snake1.type != "drone":
                                    snake1.remove_snake()
                                    continue

                if snake1.reset:
                    pass

                snake1.x = snake1.new_x
                snake1.y = snake1.new_y

                state, age = self.get_point(snake1.x, snake1.y)

                if state == 0: # If new cell is empty, the grid can easily be updated.
                    self.set_point(snake1.x, snake1.y, (snake1.id, 0))

                elif state >= 1 and state <= 20: # If new cell is already occupied by another snake.
                    if snake1.type == "drone":
                        self.set_point(snake1.x, snake1.y, (snake1.id, 0))
                    else:
                        snake1.reset = True
                        snake1.reset_tail()
                        snake1.dead += 1
                        if state != snake1.id: # If the snake's tail wasn't ours
                            self.snakes[state-1].kill += 1
                        if single_life:
                            snake1.remove_snake()
                            continue
                
                elif state >= 21 and state <= 40: # Bonus
                    self.set_point(snake1.x, snake1.y, (snake1.id, 0))
                    snake1.edit_tail(state, True)

                elif state == 255: # Wall
                    snake1.reset = True
                    snake1.reset_tail()
                    snake1.dead += 1
                    if single_life:
                        snake1.remove_snake()
                        continue

        if draw_grid:
            verts_coord = []
            verts_color = []

        for y in range(self.height):
            for x in range(self.width):
                state, age = self.get_point(x, y)

                if draw_grid:
                    color_index = 0
                    fade = 1

                if state >= 1 and state <= 20:  # Snake
                    snake = self.snakes[state - 1]
                    if snake.reset or age > snake.tail:
                        self.reset_point(x, y)
                    else:
                        self.set_point(x, y, (state, age + 1))
                        if draw_grid:
                            color_index = snake.color
                            fade -= 0.005 * age
                            if fade < 0.4:
                                fade = 0.4

                elif state >= 21 and state <= 40:  # Bonus
                    if age > self.bonus_timeout:
                        self.reset_point(x, y)
                    else:
                        self.set_point(x, y, (state, age + 1))
                        if draw_grid:
                            if state == 21:  # Good bonus
                                color_index = 11
                            else:  # Mild bonus
                                color_index = 12

                elif state == 255:  # Wall
                    if draw_grid:
                        color_index = 10

                if draw_grid:
                    if color_index > 0:
                        r, g, b = colors[color_index]
                        verts_color.extend([r*fade, g*fade, b*fade]*4)
                        verts_coord.extend(squares_verts[y][x])

        if draw_grid:
            verts_coord_size = len(verts_coord)
            verts_color_size = len(verts_color)
            verts_coord_gl = (GLfloat * verts_coord_size)(*verts_coord)
            verts_color_gl = (GLfloat * verts_color_size)(*verts_color)
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(3, GL_FLOAT, 0, verts_color_gl)
            glVertexPointer(2, GL_FLOAT, 0, verts_coord_gl)
            glDrawArrays(GL_QUADS, 0, verts_coord_size // 2)
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)

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

        self.reset_tail()
        self.x, self.y = coord
        self.new_x = self.x
        self.new_y = self.y
        # 0: Up // 1: Right // 2: Down // 3: Left
        self.dir = choice((0, 1, 2, 3))
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

    def remove_snake(self):
            self.tail = 0
            self.x = -1
            self.y = -1
            self.reset = True

    def reset_tail(self):
        """
        Resets values of snake, such as its tail's length.
            :param self: 
        """   
        self.tail = self.default_tail

    def edit_tail(self, bonusType: int, editScore: bool):
        """
        Edits the length of the tail based on the bonus eaten.
            :param self: 
            :param bonusType:int: Bonus type. May be 21 or 22.
            :param editScore:bool: Whether to edit the snake's score according to the bonus.
        """   
        if bonusType == 21:
            if editScore:
                self.score += 1
            if self.tail != self.max_tail:
                self.tail += 10
                if self.tail > self.max_tail:
                    self.tail = self.max_tail
        elif bonusType == 22:
            if editScore:
                self.score += 2
            if self.tail != self.min_tail:
                self.tail -= 5
                if self.tail < self.min_tail:
                    self.tail = self.min_tail

    def select_new_direction(self, grid: Grid):
        """
        Chooses a new direction for a CPU snake.
        It looks a few cells ahead, for the presence of a player, a wall or a bonus.
        It then changes its direction based on a probability.
            :param self: 
            :param grid:Grid: Grid object to reference to when choosing the direction.
        """
        if self.type == 'drone':
            self.new_dir = choice(self.cpu_ai[self.dir])
        elif self.type == 'cpu':
            avoid_detection = choice((2, 4, 4, 8, 8, 8))
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
                self.new_dir = choice(self.cpu_ai[self.dir])
            elif state >= 1 and state <= 20:
                self.new_dir = choice(self.cpu_avoid[self.dir])
            elif state >= 21 and state <= 40:
                self.new_dir = self.dir
            elif state == 255:
                self.new_dir = choice(self.cpu_avoid[self.dir])

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


class Game:

    def __init__(self, arena_width: int, arena_height: int, arena_border: int, square_size: int, draw: bool, fps_limit: int = 12, single_life: bool = False):
        
        self.single_life = single_life
        
        self.screen_width = arena_width + 2*arena_border
        self.screen_height = arena_height + 70
        self.arena_width = arena_width
        self.arena_height = arena_height
        self.arena_border = arena_border
        self.square_size = square_size

        self.grid_width = int(self.arena_width/self.square_size)
        self.grid_height = int(self.arena_height/self.square_size)

        if self.grid_width < 1 or self.grid_height < 1:
            raise ValueError("Square size too big or arena size too small.")

        self.iteration = 0

        self.draw = draw
        self.fps = fps_limit

        self.win = window.Window(width = self.screen_width, height = self.screen_height, visible=False)
        self.colors = []
        self.squares_verts = []
        if draw:
            self.header_img = image.load("header.png").texture
            clock.set_fps_limit(self.fps)
            self.font = font.load("Arial", 12, bold = True, italic = False)
            self.arena_verts = [
                (self.arena_border-1, self.arena_border-2),
                (self.arena_border+self.arena_width+1, self.arena_border-2),
                (self.arena_border+self.arena_width+1, self.arena_border+self.arena_height),
                (self.arena_border-1, self.arena_border+self.arena_height),
                (self.arena_border-1, self.arena_border-2)
            ]
            self.points_coord = [
                (150, self.screen_height - 20),
                (150, self.screen_height - 40),
                (420, self.screen_height - 20),
                (420, self.screen_height - 40)
            ]
            self.colors = [
                (0, 0, 0),
                (0, 0, 1),
                (1, 1, 0),
                (1, 0, 1),
                (0, 1, 1),
                (0.5, 0.5, 0),
                (0.5, 0, 0.5),
                (0, 0.5, 0.5),
                (1, 1, 1),
                (1, 1, 1),
                (1, 1, 1),
                (0, 1, 0),
                (1, 0, 0)
            ]
            self.square_verts = [
                (0, 0),
                (self.square_size-1, 0),
                (self.square_size-1, self.square_size-1),
                (0, self.square_size-1)
            ]
            for y in range(self.grid_height):
                self.squares_verts.append([])
                for x in range(self.grid_width):
                    self.squares_verts[y].append([])
                    for vx, vy in self.square_verts:
                        self.squares_verts[y][x].append(vx + self.arena_border + (x * self.square_size))
                        self.squares_verts[y][x].append(vy + self.arena_border + (y * self.square_size))

        self.grid = Grid(self.grid_width, self.grid_height)

    def draw_header(self):
        glColor3f(1, 1, 1)
        self.header_img.blit(self.arena_border, self.arena_border + self.arena_border + self.arena_height)

    def draw_points(self):
        for snake in self.grid.snakes:
            if snake.type != 'drone':
                text = "KILL %-3d, DEATH %-3d, BONUS %-3d" % (
                    snake.kill, snake.dead, snake.score)
                x, y = self.points_coord[snake.id - 1]
                r, g, b = self.colors[snake.color]
                txt = Text(self.font, text, x, y, color=(r, g, b, 1))
                txt.draw()

    def draw_arena(self):
        glBegin(GL_LINES)
        glColor3f(0.5, 0.5, 0.5)
        for i in range(4):
            glVertex2f(*(self.arena_verts[i]))
            glVertex2f(*(self.arena_verts[i + 1]))
        glEnd()

    def run(self):
        if self.draw:
            self.run_window()
        else:
            self.run_headless()

    def run_window(self):
        self.win.set_visible()
        while not self.win.has_exit:
            self.win.dispatch_events()
            clock.tick()
            self.win.set_caption('Pytron v0.5 (fps: %s)' % (round(clock.get_fps())))

            glClear(GL_COLOR_BUFFER_BIT)
            glLoadIdentity()

            self.draw_header()
            self.draw_arena()

            self.run_once(True)

            self.draw_points()
            self.win.flip()

    def run_headless(self):
        while not self.win.has_exit:
            self.run_once(False)

    def run_once(self, display: bool):
        self.grid.show_bonus()
        self.grid.update_grid(self.single_life, display, self.colors, self.squares_verts)
        self.iteration += 1
        if self.iteration % 1024 == 0:
                print(self.iteration)


game = Game(720, 480, 10, 10, True, 12, False)


@game.win.event
def on_key_press(symbol, modifiers):
    for snake in game.grid.snakes:
        if snake.type == 'human':
            if symbol == snake.up and snake.dir != 2:
                snake.new_dir = 0
            elif symbol == snake.right and snake.dir != 3:
                snake.new_dir = 1
            elif symbol == snake.down and snake.dir != 0:
                snake.new_dir = 2
            elif symbol == snake.left and snake.dir != 1:
                snake.new_dir = 3

# set wall
for y in [10, 11, 48 - 12, 49 - 12]:
    for x in range(22, 67 - 18):
        game.grid.new_wall((x,y), (x,y))
for x in [10, 11, 78 - 18, 79 - 18]:
    for y in range(22, 37 - 12):
        game.grid.new_wall((x,y), (x,y))

game.grid.new_snake('human', (key.UP, key.RIGHT, key.DOWN, key.LEFT), 1)
game.grid.new_snake('cpu', (key.W, key.D, key.S, key.A), 2)
game.grid.new_snake('cpu', (key.R, key.G, key.F, key.D), 3)
game.grid.new_snake('cpu', (key.U, key.K, key.J, key.H), 4)
game.grid.new_snake('drone', (0, 0, 0, 0), 8)
game.grid.new_snake('drone', (0, 0, 0, 0), 8)

game.run()
