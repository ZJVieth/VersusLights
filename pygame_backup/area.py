

from entity import Entity
from settings import combine_light, dist, out_of_bounds, to_grid


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

        # Set the typically player-dependent basic properties
        if pos is None:
            pos = to_grid(player.cursor_pos)
        if color is None:
            color = player.color

        self.dir = (0, 0)

        super().__init__(pos=pos, color=color, speed=speed,
                         radius=radius, hp=hp, lifetime=lifetime)

        self.player = player

    def collider(self, entity: Entity):
        return False

    def render_circle(self, grid, dropoff=None, radius=None, value_offset=0):
        if radius is None:
            radius = self.u_radius

        aX, aY = (int(self.pos[0]), int(self.pos[1]))
        for x in [i for i in range(aX-radius, aX+radius) if abs(self.pos[0]-i) < radius]:
            for y in [i for i in range(aY-radius, aY+radius) if abs(self.pos[1]-i) < radius]:
                if out_of_bounds((x, y)):
                    continue

                d = int(dist((x, y), self.pos))
                # if d > self.radius:
                #     continue

                value = 150-d*2.75 + value_offset
                # if x in [aX-radius, aX+radius-1] or y in [aY-radius, aY+radius-1]:
                # if d == self.radius:
                #     value = 150

                grid[x][y] = combine_light(
                    grid[x][y], value, self.u_color)
