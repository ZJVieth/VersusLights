
from effect import Effect


def speedball(*args):
    player = args[0]
    player.add_effect(E_Speedball())


class E_Speedball(Effect):

    def __init__(self) -> None:
        self.duration = 3  # seconds

    def apply_to(self, *args):
        player = args[0]
        player.u_can_cast = False
        player.u_radius -= 5
        player.u_speed += 60
