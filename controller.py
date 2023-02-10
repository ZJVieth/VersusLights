from settings import NR_ABILITIES


class ControllerProfile:

    def __init__(self, init_name):
        self.name = init_name
        self.buttons = [0]*6
        self.abilities = ["Bolt"]*6
        self.cursor_speed = 420

    def set_button(self, index: int, button: int, ability: str):
        if index >= NR_ABILITIES:
            return
        self.buttons[index] = button
        self.abilities[index] = ability
