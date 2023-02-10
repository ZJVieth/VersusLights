import math
import numpy as np
from pygame.math import Vector2

TITLE = "Game"
WIDTH = 1280
HEIGHT = 720
FPS = 30
GRANITY = 3

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

M_LEFT = 1
M_MIDDLE = 2
M_RIGHT = 3
M_SCROLLUP = 4
M_SCROLLDOWN = 5

LIGHT_MIN = 0
LIGHT_DECAY = 10

NR_ABILITIES = 5

V_ZERO = Vector2((0, 0))
V_ZERO_DIR = Vector2((1, 0))


class Color:
    YELLOW = 0
    GREEN = 1
    BLUE = 2
    RED = 3
    PURPLE = 4
    CYAN = 5
    WHITE = 6


class Timer:

    def __init__(self, delay, active: bool = True) -> None:
        self.delay = delay
        self.timer = delay
        if not active:
            self.timer = 0

    def timed_out(self, delta_time, reset: bool = True) -> bool:
        self.timer -= delta_time
        if self.timer <= 0:
            if reset:
                self.timer = self.delay
            return True
        return False

    def reset(self, delay: float = None):
        self.timer = self.delay
        if delay is not None:
            self.timer = delay


def increment_with_bounds(input, increment, bounds: tuple, wrap: bool = True):
    min, max = bounds
    output = input + increment
    if min is not None and output < min:
        output = max
        if not wrap:
            output = min
    if max is not None and output > max:
        output = min
        if not wrap:
            output = max
    return output


def toggle_bool(input: bool) -> bool:
    if input:
        return False
    return True


def normalize(v: tuple) -> tuple:
    m = mag(v)
    if m == 0:
        return (0, 0)
    return (v[0]/m, v[1]/m)


def mag(v: tuple) -> float:
    x, y = v
    return math.sqrt(x**2+y**2)


def rad_to_deg(input):
    return input * 180 / math.pi


def deg_to_rad(input):
    return input * math.pi / 180


def cos(input):
    return math.cos(deg_to_rad(input))


def sin(input):
    return math.sin(deg_to_rad(input))


def deg_dir_from_angle(deg_in):
    dir = (V_ZERO_DIR.x, V_ZERO_DIR.y)
    return deg_rotate_dir(dir, deg_in)


def deg_rotate_dir(dir_in, deg_in):
    v_in = Vector2(dir_in)
    v_out = v_in.rotate(deg_in)
    return (v_out.x, v_out.y)


# returns angle between two coordinates in radians
def rad_angle_from_to(t_from: tuple, t_to: tuple):
    fX, fY = t_from
    tX, tY = t_to
    t_dir = normalize((tX-fX, tY-fY))
    v_dir = Vector2(t_dir)

    return V_ZERO.angle_to(v_dir) * math.pi / 180


def rad_angle_player_to_cursor(player):
    return rad_angle_from_to(player.pos, to_grid(player.cursor_pos))


def deg_angle_player_to_cursor(player):
    return rad_to_deg(rad_angle_player_to_cursor(player))


def dist(p1: tuple, p2: tuple):
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)


def to_grid(real_pos: tuple) -> tuple:
    return (real_pos[0]//GRANITY, real_pos[1]//GRANITY)


def grid_to_real(pos: tuple) -> tuple:
    return limit_bounds(pos[0]*GRANITY, pos[1]*GRANITY)


def get_delta_time(fps):
    return 1 / fps


def light_min(input, prev=LIGHT_MIN):
    return min(max(prev, input), 255)


def grid_width():
    return WIDTH//GRANITY


def grid_height():
    return (HEIGHT-50)//GRANITY


def out_of_bounds(pos, offset=0) -> bool:
    x, y = pos
    if x >= grid_width() + offset or x < 0 - offset or y >= grid_height() + offset or y < 0 - offset:
        return True
    return False


def limit_bounds(pos: tuple, grid=True) -> tuple:
    bX = WIDTH
    bY = HEIGHT
    if grid:
        bX = grid_width()
        bY = grid_height()

    x, y = pos
    if x < 0:
        x = 0
    if x >= bX:
        x = bX - 1
    if y < 0:
        y = 0
    if y >= bY:
        y = bY - 1
    return (x, y)


def combine_light(light_in, new_val, new_color) -> tuple:
    new_light = light_color(new_val, new_color)
    color_out = (
        max(light_in[0], new_light[0]),
        max(light_in[1], new_light[1]),
        max(light_in[2], new_light[2]),
    )
    return color_out


def light_color(value, color) -> tuple:
    value = min(255, max(0, math.floor(value)))
    if color == Color.WHITE:
        return (value, value, value)
    if color == Color.RED:
        return (value, 0, 0)
    if color == Color.BLUE:
        return (0, 0, value)
    if color == Color.GREEN:
        return (0, value, 0)
    if color == Color.YELLOW:
        return (value, value, 0)
    if color == Color.PURPLE:
        return (value, 0, value)
    if color == Color.CYAN:
        return (0, value, value)
