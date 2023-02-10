import math

from pygame import Vector2

from entity import Entity
from gpixel import GPixel
from settings import Timer, cos, deg_angle_player_to_cursor, deg_dir_from_angle, deg_rotate_dir, dist, combine_light, increment_with_bounds, normalize, out_of_bounds, sin, to_grid, toggle_bool

BOLT_HP = 2
BOLT_DAMAGE = 2
BOLT_SPEED = 120
BOLT_RADIUS = 2


class BasicBolt(Entity):

    '''
    Constructor ------------------------------------------------------------------
    '''

    def __init__(
            self,
            player,
            # bolt specific properties
            damage: float = BOLT_DAMAGE,
            dir: tuple = None,
            angle: float = None,  # in degrees
            angle_from_cursor: float = None,  # in degrees
            target_pos: tuple = None,

            # standard entity properties
            pos: tuple = None,
            color: int = None,
            speed: float = BOLT_SPEED,
            radius: int = BOLT_RADIUS,
            hp: float = BOLT_HP,
            lifetime: float = None,
            damage_flash: bool = True
    ) -> None:

        # Set the typically player-dependent basic properties
        if pos is None:
            pos = player.pos
        if color is None:
            color = player.color

        # Set Basic Entity Properties
        super().__init__(pos=pos, color=color, speed=speed,
                         radius=radius, hp=hp, lifetime=lifetime, damage_flash=damage_flash)

        self.player = player

        '''
        Basic Bolt Properties
        '''
        self.damage_value = damage

        '''
        Usually Player-based Properties
        '''

        # Direction Setting
        self.target = to_grid(player.cursor_pos)
        if target_pos is not None:
            self.target = target_pos

        if dir is not None:
            self.dir = dir

        # Calculate direction from given angle
        elif angle is not None or angle_from_cursor is not None:

            if angle_from_cursor is not None:
                angle = deg_angle_player_to_cursor(player) + angle_from_cursor

            self.dir = deg_dir_from_angle(angle)
            self.angle = angle

        # calculate direction from target position (default = cursor)
        else:
            self.dir = normalize((
                self.target[0] - self.pos[0],
                self.target[1] - self.pos[1]
            ))

        '''
        Update Behaviour Fields
        '''
        # Explosion on death
        self.exploding = False
        self.explode_range = 0

    '''
    Update Methods -------------------------------------------------------------------
    '''

    # collective update method
    # returns whether or not the entity is still alive
    # False -> alive, True -> dead
    def update(self, delta_time, ah, players) -> bool:

        # if the entity is exploding, we still pretend it is alive,
        # so that it is still being rendered by the ability handler
        if self.exploding:
            return False

        return super().update(delta_time, ah, players)

    '''
    Active Methods
    '''

    def on_death(self):
        self.exploding = True
        self.collision = False

    def affect(self, entity: Entity, delta_time=None):
        entity.damage(self.damage_value)

    def collider(self, entity: Entity) -> bool:
        if not self.collision or not entity.collision:
            return False

        if entity == self.player or entity.player == self.player:
            return False

        aX, aY = self.pos
        cX, cY = entity.pos
        dist = math.sqrt((cX-aX)**2 + (cY-aY)**2)
        if dist <= entity.radius + self.radius:
            return True

        return False

    '''
    Render Methods
    '''

    def render(self, grid):
        aX, aY = self.pos

        # render a hollow circle increasing in size before being destroyed
        # currently does not behave as expected, but result still looks good
        if self.exploding:
            self.explode_range += 1
            if self.explode_range > 100:  # end explosion animation
                self.destroy()
                return

            row = self.explode_range*2 - 1
            for dir in [(1, 0), (-1, 0), (0, 1), (0, -1)]:

                bX, bY = (aX+dir[0], aY+dir[1])
                bX, bY = (bX-math.floor(row/2)*dir[1],
                          bY-math.floor(row/2)*dir[0])

                for i in range(0, row):
                    bX, bY = (bX+i*dir[1], bY+i*dir[0])

                    if out_of_bounds((bX, bY)):
                        continue

                    value = 255-self.explode_range*50

                    pxl_pos = (bX, bY)
                    if pxl_pos in grid.keys():
                        gp = grid[pxl_pos]
                        # if self not in gp.entities:
                        gp.combine(value, self.u_color)
                        continue

                    grid[pxl_pos] = GPixel(bX, bY, value, self.u_color)

            return

        # standard circle rendering
        self.render_circle(grid, dropoff=100)


class SpeedBolt(BasicBolt):

    def __init__(
        self,
        player,
        # standard optional properties
        lifetime: float = None, hp: float = BOLT_HP, speed: float = BOLT_SPEED, radius: int = BOLT_RADIUS, damage: float = BOLT_DAMAGE, pos: tuple = None, color: int = None, dir: tuple = None, angle: float = None, angle_from_cursor: float = None, target_pos: tuple = None, flash_color: int = None, flash_delay: float = 0.2
    ) -> None:
        super().__init__(player, lifetime=lifetime, hp=hp, speed=speed, radius=radius, damage=damage, pos=pos, color=color, dir=dir,
                         angle=angle, angle_from_cursor=angle_from_cursor, target_pos=target_pos)
        self.speed = 150
        self.radius = 1
        self.damage_value = 1
        self.hp = 1


class HomingBolt(BasicBolt):

    def __init__(
        self,
        player,
        players,
        # standard optional properties
        lifetime: float = None, hp: float = BOLT_HP, speed: float = BOLT_SPEED, radius: int = BOLT_RADIUS, damage: float = BOLT_DAMAGE, pos: tuple = None, color: int = None, dir: tuple = None, angle: float = None, angle_from_cursor: float = None, target_pos: tuple = None, flash_color: int = None, flash_delay: float = 0.2
    ) -> None:
        super().__init__(player, lifetime=lifetime, hp=hp, speed=speed, radius=radius, damage=damage, pos=pos, color=color, dir=dir,
                         angle=angle, angle_from_cursor=angle_from_cursor, target_pos=target_pos)

        self.target_player = None
        self.no_target = False
        if len(players) <= 1:
            self.no_target = True
            return

        # find the player closest to the target location
        closest = None
        for p in players:
            if p is self.player:
                continue

            d = dist(self.target, p.pos)
            if closest is None or d < closest:
                closest = d
                self.target_player = p

        if self.target_player is None:
            self.no_target = True

    # should be updated for smoother direction changes
    def update_dir(self, delta_time):

        # if the target dies while the homing bolt is flying, simply continue
        # flying in the last calculated direction
        if self.target_player is None or self.target_player.dead():
            return

        tX, tY = self.target_player.pos
        aX, aY = self.pos
        target_dir = normalize((tX - aX, tY - aY))

        delta_dir = (
            target_dir[0] - self.dir[0],
            target_dir[1] - self.dir[1]
        )

        self.dir = (
            self.dir[0] + delta_dir[0] * 0.1,
            self.dir[1] + delta_dir[1] * 0.1
        )


class SwirlingBolt(BasicBolt):

    def __init__(
        self,
        player,
        # specific optional parameters
        max_range: int = 40,
        rotation_speed: float = 360,
        outward_speed: float = 20,
        # standard optional parameters
        lifetime: float = None, hp: float = BOLT_HP, speed: float = BOLT_SPEED, radius: int = BOLT_RADIUS, damage: float = BOLT_DAMAGE, pos: tuple = None, color: int = None, dir: tuple = None, angle: float = None, angle_from_cursor: float = None, target_pos: tuple = None, flash_color: int = None, flash_delay: float = 0.2
    ) -> None:

        if angle is None and angle_from_cursor is None:
            angle = deg_angle_player_to_cursor(player)

        super().__init__(
            player,
            # standard optional parameters,
            lifetime=lifetime, hp=hp, speed=speed, radius=radius, damage=damage, pos=pos, color=color, dir=dir,
            angle=angle, angle_from_cursor=angle_from_cursor, target_pos=target_pos
        )

        # Specific Properties
        self.max_range = max_range
        self.rotation_speed = rotation_speed
        self.outward_speed = outward_speed

        # Update Behaviour Fields
        self.range = 0

    def update_motion(self, delta_time):

        self.angle = increment_with_bounds(
            self.angle,
            self.rotation_speed * delta_time,
            (0, 360)
        )

        self.range = increment_with_bounds(
            self.range,
            self.outward_speed * delta_time,
            (None, self.max_range),
            wrap=False
        )

        offset_rotation = (
            cos(self.angle) * self.range,
            sin(self.angle) * self.range
        )

        # add relative position to players position
        self.pos_real = (
            self.player.pos[0] + offset_rotation[0],
            self.player.pos[1] + offset_rotation[1]
        )
        self.pos = (
            round(self.pos_real[0]),
            round(self.pos_real[1])
        )


class CurvedBolt(BasicBolt):

    def __init__(
        self,
        player,
        rot_dir,
        # standard optional properties
        lifetime: float = None, hp: float = BOLT_HP, speed: float = BOLT_SPEED, radius: int = BOLT_RADIUS, damage: float = BOLT_DAMAGE, pos: tuple = None, color: int = None, dir: tuple = None, angle: float = None, angle_from_cursor: float = None, target_pos: tuple = None, flash_color: int = None, flash_delay: float = 0.2
    ) -> None:
        super().__init__(player, lifetime=lifetime, hp=hp, speed=speed, radius=radius, damage=damage, pos=pos, color=color, dir=dir,
                         angle=angle, angle_from_cursor=angle_from_cursor, target_pos=target_pos)

        self.rot_dir = rot_dir

    def update_dir(self, delta_time):
        self.dir = deg_rotate_dir(self.dir, self.rot_dir)
