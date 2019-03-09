# Source code released under gpl v3 licence, see COPYING file

from pyglet import window, clock, image
from pyglet.gl import *  # pylint: disable=unused-wildcard-import
from pyglet.window import key
from random import choice, randint
from pyglet import font
from pyglet.font import Text

from grid import Grid
from snake import Snake

def draw_grid():
    global snakesArray, grid, squares_verts, colors, bonus_timeout
    verts_coord = []
    verts_color = []
    for y in range(grid.height):
        for x in range(grid.width):
            state, age = grid.get_point(x, y)
            color_index = 0
            fade = 1
            if state >= 1 and state <= 20:  # Snake
                snake = snakesArray[state - 1]
                if snake.reset or age > snake.tail:
                    grid.reset_point(x, y)
                else:
                    grid.set_point(x, y, (state, age + 1))
                    color_index = snake.color
                    fade -= 0.005 * age
                    if fade < 0.4:
                        fade = 0.4
            elif state >= 21 and state <= 40:  # Bonus
                if age > bonus_timeout:
                    grid.reset_point(x, y)
                else:
                    grid.set_point(x, y, (state, age + 1))
                    if state == 21:  # Good bonus
                        color_index = 11
                    else:  # Mild bonus
                        color_index = 12
            elif state == 255:  # Wall
                color_index = 10
            if color_index > 0:
                r, g, b = colors[color_index]
                verts_color.extend([r*fade, g*fade, b*fade]*4)
                verts_coord.extend(squares_verts[y][x])

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


def draw_arena():
    global arena_verts
    glBegin(GL_LINES)
    glColor3f(0.5, 0.5, 0.5)
    for i in range(4):
        glVertex2f(*arena_verts[i])
        glVertex2f(*arena_verts[i + 1])
    glEnd()


def draw_header():
    global arena_border, arena_height
    glColor3f(1, 1, 1)
    header_img.blit(arena_border, arena_border + arena_border + arena_height)


def draw_points():
    global snakesArray, font, points_coord
    for snake in snakesArray:
        if snake.type != 'drone':
            text = "KILL %-3d, DEATH %-3d, BONUS %-3d" % (
                snake.kill, snake.dead, snake.score)
            x, y = points_coord[snake.id - 1]
            r, g, b = colors[snake.color]
            txt = Text(font, text, x, y, color=(r, g, b, 1))
            txt.draw()


screen_width = 740
screen_height = 550

arena_width = 720
arena_height = 480
arena_border = 10

# 2,3,4,5,6,8,10,12,15,16,20,24,30,40
square_size = 10
grid_width = int(arena_width / square_size)
grid_height = int(arena_height / square_size)
# 8 = 90 x 60 = 5400 squares
# 10 = 72 x 48 = 3456 squares

win = window.Window(width=screen_width, height=screen_height)
header_img = image.load('header.png').texture
fps_limit = 12
clock.set_fps_limit(fps_limit)
#keyboard = key.KeyStateHandler()
font = font.load('Arial', 12, bold=True, italic=False)


@win.event
def on_key_press(symbol, modifiers):
    global snakesArray
    for snake in snakesArray:
        if snake.type == 'human':
            if symbol == snake.up and snake.dir != 2:
                snake.new_dir = 0
            elif symbol == snake.right and snake.dir != 3:
                snake.new_dir = 1
            elif symbol == snake.down and snake.dir != 0:
                snake.new_dir = 2
            elif symbol == snake.left and snake.dir != 1:
                snake.new_dir = 3
#win.on_key_press = on_key_press


arena_verts = [
    (arena_border-1, arena_border-2),
    (arena_border+arena_width+1, arena_border-2),
    (arena_border+arena_width+1, arena_border+arena_height),
    (arena_border-1, arena_border+arena_height),
    (arena_border-1, arena_border-2)
]
square_verts = [
    (0, 0),
    (square_size-1, 0),
    (square_size-1, square_size-1),
    (0, square_size-1)
]

points_coord = [
    (150, 530),
    (150, 510),
    (420, 530),
    (420, 510)
]

squares_verts = []
for y in range(grid_height):
    squares_verts.append([])
    for x in range(grid_width):
        squares_verts[y].append([])
        for vx, vy in square_verts:
            squares_verts[y][x].append(vx + arena_border + (x * square_size))
            squares_verts[y][x].append(vy + arena_border + (y * square_size))

#(id, age)
# id = 0          : empty
# id >= 1 e <=20  : snake (human, cpu, drone)
# id >=21 e <=40  : bonus
# id = 255        : wall
grid = Grid(grid_width, grid_height)

# set wall
for y in [10, 11, 48 - 12, 49 - 12]:
    for x in range(22, 67 - 18):
        grid.set_point(x, y, (255, 0))
for x in [10, 11, 78 - 18, 79 - 18]:
    for y in range(22, 37 - 12):
        grid.set_point(x, y, (255, 0))
# for y in range(10):
#  for x in range(90):
#    grid.set_point(x,y,(255,0))

colors = [
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

snakesArray = []
snakesArray.append(Snake(1, 'human', (key.UP, key.RIGHT,
                                      key.DOWN, key.LEFT), 1, grid.random_point()))
snakesArray.append(
    Snake(2, 'cpu', (key.W, key.D, key.S, key.A), 2, grid.random_point()))
snakesArray.append(
    Snake(3, 'cpu', (key.R, key.G, key.F, key.D), 3, grid.random_point()))
snakesArray.append(
    Snake(4, 'cpu', (key.U, key.K, key.J, key.H), 4, grid.random_point()))
snakesArray.append(Snake(5, 'drone', (0, 0, 0, 0), 8, grid.random_point()))
snakesArray.append(Snake(6, 'drone', (0, 0, 0, 0), 8, grid.random_point()))

#bonusArray = []
bonus_timeout = 74

for snake in snakesArray:
    grid.set_point(snake.x, snake.y, (snake.id, 0))


#counter = 0
while not win.has_exit:
    win.dispatch_events()
    dt = clock.tick()
    # print dt
    win.set_caption('Pytron v0.5 (fps: %s)' % (round(clock.get_fps())))

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    draw_header()
    draw_arena()

#  if counter == 3:
#    counter = 0
    grid.show_bonus()

    for snake in snakesArray:
        snake.reset = False
    for snake in snakesArray:
        snake.select_new_direction(grid)
        snake.dir = snake.new_dir
    for snake in snakesArray:
        snake.move(grid)
    # check draw
    for snake1 in snakesArray:
        for snake2 in snakesArray:
            if snake1.id != snake2.id:
                if snake1.new_x == snake2.new_x and snake1.new_y == snake2.new_y:
                    snake1.reset = True
                    snake2.reset = True
    for snake in snakesArray:
        snake.x = snake.new_x
        snake.y = snake.new_y
        snake.check_collision(grid, snakesArray)
#  else:
#    counter += 1
    draw_grid()
    draw_points()
    win.flip()

# print "Punteggio"
# for snake in snakesArray:
#  print snake.id, ": points:", snake.points, ", dead: ", snake.dead, ", kill: ", snake.kill
