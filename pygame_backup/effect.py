

from settings import Timer, toggle_bool, Color


class Effect:

    duration = 2
    priority = 1

    def update_duration(self, delta_time):
        if self.duration is None:
            return
        self.duration -= delta_time

    def timed_out(self):
        if self.duration is None:
            return False

        if self.duration <= 0:
            return True
        return False

    # to overwrite
    def apply_to(self, *args):
        player = args[0]
        delta_time = args[1]
        ah = args[2]
        players = args[3]


class FlashEffect(Effect):

    ON = True

    def __init__(self, priority: int = 1, color: int = Color.WHITE, delay: float = 0.2) -> None:
        self.priority = priority
        self.duration = None
        self.flash_timer = Timer(delay)
        self.state = False
        self.color = color

    def apply_to(self, *args):
        player = args[0]
        delta_time = args[1]

        if self.flash_timer.timed_out(delta_time):
            self.state = toggle_bool(self.state)

        if self.state == self.ON:
            player.u_color = self.color
