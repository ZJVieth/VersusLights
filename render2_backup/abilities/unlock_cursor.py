
from effect import Effect


def unlock_cursor(*args) -> None:
    player = args[0]
    button: int = args[2]
    player.add_effect(E_CursorUnlocked(button))


def remove_unlock_cursor(player, button: int) -> None:
    for e in player.get_effects_of_type(E_CursorUnlocked):
        if e.button == button:
            player.remove_effect(e)


class E_CursorUnlocked(Effect):

    def __init__(self, button: int) -> None:
        self.duration = None
        self.button = button

    def apply_to(self, *args):
        player = args[0]
        player.u_cursor_unlocked = True
