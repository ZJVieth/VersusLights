

from abilities.basic_bolts import HomingBolt
from area import Area
from effect import Effect, FlashEffect
from entity import Entity
from settings import Color


def frost_seeker(*args) -> HomingBolt:
    player = args[0]
    players = args[1]

    bolt = FrostBolt(player, players, radius=4, speed=80, damage=1, hp=3)
    bolt.add_effect(FlashEffect(color=Color.CYAN))

    return bolt


def frost_field(*args):
    player = args[0]

    area = Area(player, radius=50, lifetime=10)
    area.add_effect(FlashEffect(color=Color.CYAN, delay=0.4))

    return area


class FrostBolt(HomingBolt):

    def affect(self, entity: Entity):
        super().affect(entity)
        entity.add_effect(FrostEffect())


class FrostEffect(Effect):

    def __init__(self) -> None:
        self.duration = None

    def apply_to(self, *args):
        player = args[0]
        frost_list = player.get_effects_of_type(FrostEffect)

        if len(frost_list) >= 4:
            for e in frost_list:
                player.remove_effect(e)
            player.add_effect(ImmobilizeEffect(duration=3))


class ImmobilizeEffect(Effect):

    def __init__(self, duration: float = 1) -> None:
        self.duration = duration
        self.priority = 99

    def apply_to(self, *args):
        player = args[0]
        player.u_speed = 0
