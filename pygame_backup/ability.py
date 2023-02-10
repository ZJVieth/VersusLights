

from abilities.frost_abilities import frost_field, frost_seeker
from abilities.unlock_cursor import unlock_cursor
from abilities.speedball import speedball
from abilities.flamethrower import flamethrower
from abilities.basic_abilities import bolt, speed_bolt, homing_bolt, volley, swirling_bolt, curved_x, blink


def sign(input):
    if input < 0:
        return -1
    return 1


ABILITY_TABLE = {
    'Bolt': {'channel': None, 'release': bolt, 'cooldown': 0.4},
    'Speed Bolt': {'channel': None, 'release': speed_bolt, 'cooldown': 0.2},
    'Curved X': {'channel': None, 'release': curved_x, 'cooldown': 2},
    'Homing Bolt': {'channel': None, 'release': homing_bolt, 'cooldown': 1.5},
    'Frost Seeker': {'channel': None, 'release': frost_seeker, 'cooldown': 4},
    'Swirling Bolt': {'channel': None, 'release': swirling_bolt, 'cooldown': 2.5},
    'Volley': {'channel': None, 'release': volley, 'cooldown': 1},
    'Speedball': {'channel': None, 'release': speedball, 'cooldown': 10},
    'Flamethrower': {'channel': None, 'release': flamethrower, 'cooldown': 20},
    'Blink': {'channel': unlock_cursor, 'release': blink, 'cooldown': 20},
    'Frost Field': {'channel': unlock_cursor, 'release': frost_field, 'cooldown': 30}
}


class AbilityHandler:

    def __init__(self) -> None:
        self.active = []

    def fire(self, ability):
        if type(ability) is not list:
            ability = [ability]

        for a in ability:
            self.active.append(a)

    def update(self, delta_time, players):
        for a in self.active:
            if a is None:
                continue

            is_dead = a.update(delta_time, self, players)
            if is_dead:
                self.active.remove(a)

    def render(self, grid):
        for a in self.active:
            if a is None:
                continue
            a.render(grid)

    def check_collision(self, entities: list):
        for a in self.active:
            if a is None or not a.collision or a.dead():
                continue

            # player entities with ability entities
            for entity in entities:
                if not entity.collision or entity.dead():
                    continue
                if a.collider(entity):
                    a.affect(entity)
                    a.damage(a.hp)

            # ability entities with ability entities

            for b in self.active:
                if b is None or not b.collision or a == b or b.dead():
                    continue
                if a.collider(b):
                    a.affect(b)
                    b.affect(a)
