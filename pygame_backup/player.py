from abilities.unlock_cursor import remove_unlock_cursor
import math
from effect import Effect
from ability import ABILITY_TABLE, sign
import pygame as pg
from pygame import Vector2

from settings import GRANITY, HEIGHT, NR_ABILITIES, WIDTH, Color, combine_light, dist, grid_width, grid_height, UP, DOWN, LEFT, RIGHT, light_color, limit_bounds, out_of_bounds
from controller import ControllerProfile
from entity import Entity

MAX_HP = 20
HP_LENGTH = 200
HP_HEIGHT = 25
UI_POSITION = [
    # HP Bar position, cooldown offset direction,
    [(0, grid_height()*GRANITY+2), 1],
    [(0, grid_height()*GRANITY+2+HP_HEIGHT), 1],
    [(WIDTH-HP_LENGTH, grid_height()*GRANITY+2), -1],
    [(WIDTH-HP_LENGTH, grid_height()*GRANITY+2+HP_HEIGHT), -1]
]
HP_BG_BOX = pg.Surface((HP_LENGTH, HP_HEIGHT))
HP_BG_BOX.fill(pg.Color([100, 100, 100]))

PLAYER_SPEED = 60
PLAYER_MAX_HP = 20
PLAYER_RADIUS = 7


class Player(Entity):

    '''
    Constructor ----------------------------------------------------------------------
    '''

    def __init__(self, color: int, pos: tuple, controller_profile: ControllerProfile, controller_instance=-1) -> None:

        super().__init__(pos=pos, color=color, speed=PLAYER_SPEED,
                         radius=PLAYER_RADIUS, hp=PLAYER_MAX_HP)

        self.c_profile = controller_profile
        self.c_instance = controller_instance
        self.player = self

        '''
        Player specific effectable properties
        '''
        self.can_cast = True
        self.u_can_cast = self.can_cast

        self.cursor_unlocked = False
        self.u_cursor_unlocked = self.cursor_unlocked

        '''
        Event/Update Behaviour Fields
        '''
        # Motion Control
        self.motion_axis = [0.0, 0.0]

        # Cursor Control
        self.view_axis = [0.0001, 0.0]
        self.cursor_pos = (WIDTH/2, HEIGHT/2)
        self.cursor_angle_rad = 0

        # Ability Control
        self.channelling = [False]*NR_ABILITIES
        self.cooldowns = [0]*NR_ABILITIES

    '''
    Update Methods
    '''

    def update(self, delta_time, ah, players):
        super().update(delta_time, ah, players)

        self.update_cooldowns(delta_time)
        self.update_cursor(delta_time)

    def reset_effect_stack(self):
        super().reset_effect_stack()
        self.u_can_cast = self.can_cast
        self.u_cursor_unlocked = self.cursor_unlocked

    def update_cooldowns(self, delta_time):
        for i, c in enumerate(self.cooldowns):
            self.cooldowns[i] -= delta_time

    def update_dir(self, delta_time):
        self.dir = self.motion_axis

    def update_motion(self, delta_time):
        super().update_motion(delta_time)
        self.pos_real = limit_bounds(self.pos_real, grid=False)
        self.pos = limit_bounds(self.pos)

    def update_cursor(self, delta_time):

        # if the cursor is unlocked, simply move it by view-axis values and
        # quit the update
        if self.u_cursor_unlocked:
            self.cursor_pos = limit_bounds((
                self.cursor_pos[0] + self.view_axis[0] *
                self.c_profile.cursor_speed*delta_time,
                self.cursor_pos[1] + self.view_axis[1]*self.speed*7*delta_time,
            ), False)
            return

        # otherwise, calculate the smooth rotations of the cursor around the player
        # this math stuff makes me look smart, so Im not gonna explain any of it
        # otherwise youd realize how low level this is and Id look less smart

        center = Vector2((0, 0))
        v_cursor_dir = Vector2(self.view_axis)
        angle_deg = center.angle_to(v_cursor_dir)
        angle_rad = angle_deg * math.pi / 180

        dist_by_0 = abs(angle_rad) + abs(self.cursor_angle_rad)
        dist_by_pi = 2 * math.pi - abs(angle_rad) - abs(self.cursor_angle_rad)

        fac = 0.1
        t = angle_rad
        c = self.cursor_angle_rad
        r = c
        if sign(t) != sign(c) and dist_by_pi < dist_by_0:
            if t < 0 and c >= 0:
                a = math.pi-c + math.pi+t

            if c < 0 and t >= 0:
                a = -(math.pi+c + math.pi - t)
        else:
            a = t - c

        r += a * fac
        if r > math.pi:
            r = -2*math.pi + r
        if r < -math.pi:
            r = 2*math.pi + r

        self.cursor_angle_rad = r

        cursor_range = 30

        self.cursor_pos = limit_bounds((
            (self.pos[0] + math.cos(self.cursor_angle_rad)
             * cursor_range) * GRANITY,
            (self.pos[1] + math.sin(self.cursor_angle_rad)
             * cursor_range) * GRANITY
        ), False)

    '''
    Player Movement and Cursor Control
    called from event handling in main game loop
    '''

    def set_move(self, axis, value):
        self.motion_axis[axis] = value

    def set_view(self, axis, value):
        if abs(value) <= 0.05:
            return
        self.view_axis[axis-2] = value

    '''
    Ability Activation Handling
    called from event handling in main game loop
    '''

    def ability_button_down(self, ah, button: int, players: list):
        if not self.u_can_cast:
            return

        if button not in self.c_profile.buttons:
            return

        index = self.c_profile.buttons.index(button)

        # if the ability is still on cooldown, exit
        if self.cooldowns[index] > 0:
            return

        ability_name = self.c_profile.abilities[index]
        ability_obj = ABILITY_TABLE[ability_name]

        # if the ability has a channelling phase, only activate the channel part
        if ability_obj['channel'] is not None:
            ah.fire(ability_obj['channel'](self, players, button))
            self.channelling[index] = True
            return

        # otherwise simply activate the release part
        ah.fire(ability_obj['release'](self, players, button))

        # and activate the cooldown
        self.cooldowns[index] = ability_obj['cooldown']

    def ability_button_up(self, ah, button: int, players: list):

        if button not in self.c_profile.buttons:
            return

        index = self.c_profile.buttons.index(button)

        # if the ability is still on cooldown, simply exit
        if self.cooldowns[index] > 0:
            return

        ability_name = self.c_profile.abilities[index]
        ability_obj = ABILITY_TABLE[ability_name]

        # if the ability didnt have a channel, it was already released, so there is
        # nothing left to do here
        if ability_obj['channel'] is None:
            return

        # check if the ability was actually channelled first before it's being released
        # this prevents holding the button before the end of the cooldown and releasing
        # it still activating the second part
        if not self.channelling[index]:
            return

        # if it had a channel, it is likely that the ability unlocked the cursor
        # so look for cursor-lock effects caused by this ability and remove them
        remove_unlock_cursor(self, button)

        # then fire the ability
        ah.fire(ability_obj['release'](self, players, button))
        # and activate the cooldown
        self.cooldowns[index] = ability_obj['cooldown']

        self.channelling[index] = False

    '''
    Render Functions
    '''

    def render(self, grid):
        if self.dead():
            return
        self.render_circle(grid, dropoff=40, radius=self.u_radius)

    # deprecated
    def render_hp(self, screen: pg.Surface, font, i: int):
        txt = font.render(str(self.hp), 1, pg.Color(
            light_color(255, self.color)))
        screen.blit(txt, (50+i*50, 10))

    def render_ui(self, screen: pg.Surface, font, i: int):
        hp_pos = UI_POSITION[i][0]

        curr_hp_length = max(0, (self.hp / MAX_HP) * HP_LENGTH)
        hp_box = pg.Surface((curr_hp_length, HP_HEIGHT))
        hp_box.fill(pg.Color(light_color(255, self.color)))

        screen.blit(HP_BG_BOX, hp_pos)
        screen.blit(hp_box, hp_pos)

    # needs visual upgrade
    def render_cursor(self, screen):
        color = light_color(255, self.color)
        rect = pg.Surface((5, 5))
        rect.fill(pg.Color(color))
        screen.blit(rect, self.cursor_pos)

    def ai_update(self, target_player: Entity):
        self.cursor_pos = (
            target_player.pos[0]*GRANITY, target_player.pos[1]*GRANITY)
