
import random
from game import empty_grid
from player import Player
from settings import Color, FPS, GRANITY, LIGHT_DECAY, WIDTH, HEIGHT, Timer, grid_height, grid_width, light_min
import pyglet as pyg


window = pyg.window.Window(WIDTH, HEIGHT)

grid = empty_grid()


def render_grid(grid) -> pyg.graphics.Batch:
    output = pyg.graphics.Batch()
    for x in range(0, grid_width()):
        for y in range(0, grid_height()):
            if sum(grid[x][y]) == 0:
                continue

            # apply decay
            grid[x][y] = [
                light_min(grid[x][y][0] - LIGHT_DECAY),
                light_min(grid[x][y][1] - LIGHT_DECAY),
                light_min(grid[x][y][2] - LIGHT_DECAY)
            ]

            circle = pyg.shapes.Circle(
                x*GRANITY, grid_height()-y*GRANITY, 1.0, color=(grid[x][y][0], grid[x][y][1], grid[x][y][2]), batch=output)

    return output


# DRAW Loop
@window.event
def on_draw():
    window.clear()

    global grid

    grid_batch = render_grid(grid)
    grid_batch.draw()


# UPDATE Loop
player2 = Player(Color.CYAN, (100, 100), None)
p2_timer = Timer(0.5)


def update(dt):

    if not player2.dead():
        if p2_timer.timed_out(dt):
            # randomized movement
            r1 = random.random()*2 - 1
            r2 = random.random()*2 - 1
            player2.set_move(0, r1)
            player2.set_move(1, r2)

    player2.render(grid)


if __name__ == '__main__':

    grid = empty_grid()

    pyg.clock.schedule_interval(update, 1/120.0)
    pyg.app.run()
