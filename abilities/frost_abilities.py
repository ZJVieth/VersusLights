
# from player import Player
from abilities.basic_bolts import BasicBolt, HomingBolt
from area import Area
from effect import Effect, FlashEffect
from entity import Entity
from settings import Color, Timer


def frost_seeker(*args) -> HomingBolt:
    player = args[0]
    players = args[1]

    bolt = FrostBolt(player, players, radius=4, speed=80, damage=1, hp=3)
    bolt.add_effect(FlashEffect(color=Color.CYAN))

    return bolt


def frost_field(*args):
    player = args[0]

    outer = OuterFrostArea(player, radius=80, lifetime=10)

    inner = InnerFrostArea(player, radius=30, lifetime=10)
    inner.add_effect(FlashEffect(color=Color.CYAN, delay=0.4))

    return [outer, inner]


class OuterFrostArea(Area):
    def affect(self, entity: Entity, delta_time=None):
        if type(entity) is BasicBolt or entity is self.player or entity.player is self.player:
            return

        frost_list = entity.get_effects_of_type(OuterFrostEffect)
        if len(frost_list) == 0:
            entity.add_effect(OuterFrostEffect())


class InnerFrostArea(Area):

    damageTimer = Timer(1)

    def affect(self, entity: Entity, delta_time=None):
        if type(entity) is BasicBolt or entity is self.player or entity.player is self.player:
            return

        frost_list = entity.get_effects_of_type(InnerFrostEffect)
        if len(frost_list) == 0:
            entity.add_effect(InnerFrostEffect())

        # take one damage on area damage tick (once a second)
        if self.damageTimer.timed_out(delta_time):
            entity.damage(1)
            entity.add_effect(FrostEffect())


class OuterFrostEffect(Effect):
    duration = 0.5

    def apply_to(self, *args):
        player = args[0]
        player.u_speed *= 0.5


class InnerFrostEffect(Effect):
    duration = 0.5

    def apply_to(self, *args):
        player = args[0]
        player.u_speed *= 0.25


class FrostBolt(HomingBolt):

    def affect(self, entity: Entity, delta_time):
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
