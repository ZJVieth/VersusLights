

import random
from settings import Timer
from abilities.basic_bolts import BasicBolt
from effect import Effect


def flamethrower(*args):
    player = args[0]
    player.add_effect(E_Flamethrower())


class E_Flamethrower(Effect):

    def __init__(self) -> None:
        self.duration = 5
        self.frequency = 30
        self.flame_timer = Timer(1/self.frequency)

    def apply_to(self, *args):

        player = args[0]
        delta_time = args[1]
        ah = args[2]

        player.u_speed *= 0.5

        if self.flame_timer.timed_out(delta_time):

            # get a random angle offset between -15° and 15°
            angle = random.random()*30-15

            ah.fire(BasicBolt(player, angle_from_cursor=angle, lifetime=0.25))
