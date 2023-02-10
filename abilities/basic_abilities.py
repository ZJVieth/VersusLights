import math
import random
from effect import FlashEffect
from settings import to_grid
from abilities.basic_bolts import BOLT_RADIUS, BasicBolt, CurvedBolt, HomingBolt, SpeedBolt, SwirlingBolt


def bolt(*args) -> BasicBolt:
    player = args[0]
    return BasicBolt(player)


def speed_bolt(*args) -> SpeedBolt:
    player = args[0]
    return SpeedBolt(player)


def homing_bolt(*args) -> HomingBolt:
    player = args[0]
    players = args[1]

    bolt = HomingBolt(player, players, radius=4, speed=80, damage=3, hp=3)
    bolt.add_effect(FlashEffect(priority=10))

    return bolt


def volley(*args):
    player = args[0]

    bolts = []

    for angle in [-15, 0, 15]:
        bolts.append(BasicBolt(player, angle_from_cursor=angle))

    return bolts


def swirling_bolt(*args):
    player = args[0]

    bolts = []
    increment = 360/3  # because the ability releases three bolts
    for i in range(3):
        angle = i*increment
        bolts.append(SwirlingBolt(player, angle=angle, lifetime=5))

    return bolts


def curved_bolt(*args):
    player = args[0]

    a_fac = [-1, 1]
    i = math.floor(random.random()*2)
    angle = a_fac[i] * 30

    return CurvedBolt(player, -a_fac[i], angle_from_cursor=angle)


def curved_x(*args):
    player = args[0]

    bolts = []

    for a_fac in [-1, 1]:
        angle = a_fac * 30
        bolts.append(CurvedBolt(player, -a_fac, angle_from_cursor=angle))

    return bolts


def wave_of_bolts(player, nr_bolts: int, bolt_type: type = BasicBolt, pos: tuple = None, lifetime: int = None):

    start_pos = player.pos
    if pos is not None:
        start_pos = pos

    bolts = []
    increment = 360/nr_bolts
    for i in range(nr_bolts):
        angle = i * increment
        bolts.append(bolt_type(player, angle=angle,
                     pos=start_pos, lifetime=lifetime))

    return bolts


def blink(*args):
    player = args[0]

    # generate bolts at current player location
    bolts = wave_of_bolts(player, nr_bolts=8)  # , lifetime=0.25)
    # then move the player
    player.set_pos(to_grid(player.cursor_pos))

    return bolts


def snipe(*args):
    player = args[0]

    bolt = BasicBolt(player, hp=4, damage=4, speed=400)
    return bolt
