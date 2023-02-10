import pygame as pg
from settings import GRANITY, HEIGHT, LIGHT_DECAY, WIDTH, combine_light, light_color


class GPixel:

    def __init__(self, x, y, value, color) -> None:
        self.pos = (x, y)
        self.light = light_color(value, color)

    def combine(self, value, color):
        self.light = combine_light(self.light, value, color)

    def render(self, pxarray):
        self.apply_decay()

        x, y = (self.pos[0]*GRANITY, self.pos[1]*GRANITY)
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return

        pxarray[x, y] = self.light

    def apply_decay(self):
        self.light = (
            max(0, self.light[0] - LIGHT_DECAY),
            max(0, self.light[1] - LIGHT_DECAY),
            max(0, self.light[2] - LIGHT_DECAY)
        )

    def dead(self):
        return self.light == (0, 0, 0)
