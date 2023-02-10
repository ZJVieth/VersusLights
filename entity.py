from abc import abstractmethod
import pygame as pg
from gpixel import GPixel

from settings import GRANITY, HEIGHT, WIDTH, Timer, grid_width, grid_height, Color, out_of_bounds, dist, combine_light, to_grid
from effect import Effect


class Entity():

    '''
    Constructor ---------------------------------------------------------------------
    '''

    def __init__(
        self,
        pos: tuple = (grid_width()/2, grid_height()/2),
        color: int = Color.WHITE,
        speed: float = 60,
        radius: int = 1,
        hp: float = 1,
        lifetime: float = None,
        damage_flash: bool = True
    ) -> None:
        '''
        Non-effectable Properties
        '''
        self.dir = None
        self.pos = pos
        self.pos_real = self.pos
        self.hp = hp
        self.lifetime = lifetime
        self.density = 1

        '''
        Effectable Properties
        '''
        # list of active effects
        self.effects = []

        self.color = color
        self.u_color = self.color

        self.speed = speed
        self.u_speed = self.speed

        self.radius = radius
        self.u_radius = self.radius

        # Behaviour Update Fields
        self.is_player = False
        self.collision = True
        self.destroyed = False
        self.damage_flash_timer = Timer(0.1, active=False)
        self.damage_flash_active = damage_flash

    '''
    Active Methods -----------------------------------------------------------------
    '''

    def on_death(self):
        self.destroy()

    def damage(self, val):
        self.hp -= val
        self.damage_flash_timer.reset()
        if self.hp <= 0:
            self.on_death()

    def destroy(self):
        self.collision = False
        self.destroyed = True

    '''
    Setters
    '''

    def set_pos(self, pos):
        self.pos_real = pos
        self.pos = pos

    '''
    Getters ---------------------------------------------------------------------
    '''

    def dead(self) -> bool:
        if out_of_bounds(self.pos, offset=50):
            return True
        return self.destroyed

    '''
    Effect-Based Methods
    '''

    def add_effect(self, effect: Effect):
        self.effects.append(effect)
        self.effects.sort(key=lambda x: x.priority)

    def remove_effect(self, effect: Effect):
        self.effects.remove(effect)

    def get_effects_of_type(self, search_type: type):
        out = []
        for e in self.effects:
            if type(e) == search_type:
                out.append(e)
        return out

    def reset_effect_stack(self):
        self.u_color = self.color
        self.u_speed = self.speed
        self.u_radius = self.radius

    def update_effects(self, delta_time, ah, players):
        # apply effect stack
        for e in self.effects:
            e.update_duration(delta_time)
            if e.timed_out():
                self.effects.remove(e)
            e.apply_to(self, delta_time, ah, players)

    '''
    Main Update Functions -------------------------------------------------------
    '''

    # additionally returns wether an entity is still alive or not
    # this is used for ability-based entities only, and has no
    # relevance for player entities
    # False -> alive, True -> dead
    def update(self, delta_time, ah, players) -> bool:

        self.update_lifetime(delta_time)

        if self.dead():
            return True

        self.reset_effect_stack()
        self.update_effects(delta_time, ah, players)

        self.update_dir(delta_time)
        self.update_motion(delta_time)
        self.update_damage_flash(delta_time)

        return False

    def update_lifetime(self, delta_time):
        if self.lifetime is None:
            return

        self.lifetime -= delta_time
        if self.lifetime <= 0:
            # self.damage(self.hp)
            self.destroy()

    def update_dir(self, delta_time):
        pass

    def update_motion(self, delta_time):
        if self.dir is None:
            return

        old_pos = self.pos

        self.pos_real = (self.pos_real[0] + self.dir[0]*self.u_speed*delta_time,
                         self.pos_real[1] + self.dir[1]*self.u_speed*delta_time)
        self.pos = (round(self.pos_real[0]),
                    round(self.pos_real[1]))

        if old_pos != self.pos:
            self.rerender = True

    def update_damage_flash(self, delta_time):
        if not self.damage_flash_active:
            return
        if not self.damage_flash_timer.timed_out(delta_time, reset=False):
            self.u_color = Color.PURPLE

    '''
    Rendering ----------------------------------------------------------------
    '''

    def render(self, grid):
        self.render_circle(grid)

    def get_pixel_value(self, x, y, dropoff, offset):
        d = dist(self.pos, (x, y))
        return 255 - d*dropoff + offset

    def render_circle(self, grid, dropoff=None, radius=None, value_offset=0):
        if radius is None:
            radius = self.u_radius

        aX, aY = self.pos
        for x in range(int(aX-radius), int(aX+radius), int(1/self.density)):
            for y in range(int(aY-radius), int(aY+radius), int(1/self.density)):
                if out_of_bounds((x, y)):
                    continue

                value = self.get_pixel_value(x, y, dropoff, value_offset)
                if value <= 0:
                    continue

                pxl_pos = (x, y)
                if pxl_pos in grid.keys():
                    grid[pxl_pos].combine(value, self.u_color)
                    continue

                grid[pxl_pos] = GPixel(x, y, value, self.u_color)
