
import pygame as pg
from entity import Entity
from settings import GRANITY, HEIGHT, WIDTH, combine_light, dist, light_color, out_of_bounds, to_grid


class Area(Entity):

    def __init__(
            self,
            player,
            # area specific properties

            # standard entity properties
            pos: tuple = None,
            color: int = None,
            speed: float = None,
            radius: int = 50,
            hp: float = 1,
            lifetime: float = None,
    ) -> None:

        self.rerender = True

        # Set the typically player-dependent basic properties
        if pos is None:
            pos = to_grid(player.cursor_pos)
        if color is None:
            color = player.color

        self.dir = (0, 0)

        super().__init__(pos=pos, color=color, speed=speed,
                         radius=radius, hp=hp, lifetime=lifetime)

        self.player = player
        self.density = 1/2

    def damage(self, val):
        pass

    # an area has no effect by default
    def affect(self, entity: Entity, delta_time=None):
        pass

    # by default, the player creating an area will also collide with it
    # if that is not wanted, player must be excluded in area effect!
    def collider(self, entity: Entity):
        if not self.collision or not entity.collision:
            return False

        if dist(self.pos, entity.pos) <= self.radius:
            return True

        return False

    # rendering related functions
    def get_pixel_value(self, x, y, dropoff, offset):
        d = int(dist((x, y), self.pos))
        # return 150-d*2.75 + offset
        return 150-137*(d/self.radius) + offset
