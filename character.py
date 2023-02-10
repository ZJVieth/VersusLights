

from entity import Entity
from settings import HEIGHT, NR_ABILITIES, WIDTH, limit_bounds


class Character(Entity):

    def __init__(
        self,
        nr_of_abilities: int = NR_ABILITIES,
        # typical entity properties
        pos: tuple = None,
        color: int = None,
        speed: float = None,
        radius: int = None,
        hp: float = None,
        lifetime: float = None,
        damage_flash: bool = True
    ) -> None:
        super().__init__(pos=pos, color=color, speed=speed, radius=radius,
                         hp=hp, lifetime=lifetime, damage_flash=damage_flash)

        self.player = self
        self.is_player = True

        '''
        Character specific effectable properties
        '''
        self.can_cast = True
        self.u_can_cast = self.can_cast

        '''
        Event/Update Behaviour Fields
        '''
        self.cursor_pos = (WIDTH/2, HEIGHT/2)

        self.cooldowns = [0]*nr_of_abilities
        self.channelling = [False]*nr_of_abilities

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

    def update_cooldowns(self, delta_time):
        for i, _ in enumerate(self.cooldowns):
            self.cooldowns[i] -= delta_time

    def update_cursor(self, delta_time):
        pass

    def update_motion(self, delta_time):
        super().update_motion(delta_time)
        self.pos_real = limit_bounds(self.pos_real, grid=False)
        self.pos = limit_bounds(self.pos)

    '''
    Render Functions
    '''

    def render(self, grid):
        if self.dead():
            return
        self.render_circle(grid, dropoff=40, radius=self.u_radius)
