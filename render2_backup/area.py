
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

    # IMPLEMENT!!!
    def collider(self, entity: Entity):
        return False

    def get_pixel_value(self, x, y, dropoff, offset):
        d = int(dist((x, y), self.pos))
        return 150-d*2.75 + offset

    def render_circle(self, screen, grid, dropoff=None, radius=None, value_offset=0):
        if radius is None:
            radius = self.u_radius

        aX, aY = self.pos
        for x in range(int(aX-radius), int(aX+radius)):
            for y in range(int(aY-radius), int(aY+radius)):
                if out_of_bounds((x, y)):
                    continue

                value = self.get_pixel_value(x, y, dropoff, value_offset)
                if value <= 0:
                    continue

                grid[x][y] = combine_light(
                    grid[x][y], value, self.u_color)

        surf_circle = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        surf_circle.set_alpha(10)
        col = light_color(255, self.u_color)
        pg.draw.circle(surf_circle, col, (aX*GRANITY,
                       aY*GRANITY), radius*GRANITY)

        screen.blit(surf_circle, (0, 0))

    # def render_circle(self, screen, grid, dropoff=None, radius=None, value_offset=0):
    #     if radius is None:
    #         radius = self.u_radius

    #     aX, aY = (int(self.pos[0]), int(self.pos[1]))
    #     for x in [i for i in range(aX-radius, aX+radius) if abs(self.pos[0]-i) < radius]:
    #         for y in [i for i in range(aY-radius, aY+radius) if abs(self.pos[1]-i) < radius]:
    #             if out_of_bounds((x, y)):
    #                 continue

    #             d = int(dist((x, y), self.pos))
    #             # if d > self.radius:
    #             #     continue

    #             value = 150-d*2.75 + value_offset
    #             # if x in [aX-radius, aX+radius-1] or y in [aY-radius, aY+radius-1]:
    #             # if d == self.radius:
    #             #     value = 150

    #             grid[x][y] = combine_light(
    #                 grid[x][y], value, self.u_color)

    #             r, g, b = grid[x][y]
    #             pg.draw.circle(screen, pg.Color(r, g, b),
    #                            (x*GRANITY, y*GRANITY), 1)
