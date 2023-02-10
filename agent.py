
import random
from abc import ABC, abstractclassmethod
from character import Character
from player import PLAYER_MAX_HP, PLAYER_RADIUS, PLAYER_SPEED
from settings import NR_ABILITIES, Timer, deg_dir_from_angle, dist, normalize, reverse_dir


class AIMoveMode(ABC):

    dir: tuple = (0, 0)

    def __init__(self, agent) -> None:
        super().__init__()

        self.agent = agent

    @abstractclassmethod
    def get_dir(self, *args):
        pass


class AIMoveLinear(AIMoveMode):

    def __init__(
        self,
        agent,
        dir: tuple = None,
        dir_angle: float = None,
        timer: Timer = None,
        distance: int = None,
        reverse: bool = False
    ) -> None:
        super().__init__(agent)

        self.dir = dir
        if dir is None and dir_angle is not None:
            self.dir = deg_dir_from_angle(dir_angle)

        if self.dir is None:
            raise ValueError('dir or dir_angle have to be specified.')

        self.reverse = reverse
        self.timer: Timer = timer
        self.distance: float = distance
        self.start_point: tuple = agent.pos

    def get_dir(self, *args):
        delta_time = args[0]

        if (self.timer is not None and self.timer.timed_out(delta_time)) or (self.distance is not None and dist(self.agent.pos, self.start_point) >= self.distance):
            self.start_point = self.agent.pos
            if self.reverse:
                self.dir = reverse_dir(self.dir)
            else:
                self.dir = (0, 0)

        return self.dir


class AIMoveRandom(AIMoveMode):
    def __init__(
        self,
        agent,
        timer: Timer = None,
        distance: float = None
    ) -> None:
        super().__init__(agent)

        self.timer = timer
        self.distance = distance
        self.start_point = agent.pos

        dx = random.random()*2 - 1
        dy = random.random()*2 - 1
        self.dir = normalize((dx, dy))

    def get_dir(self, *args):
        delta_time = args[0]

        if (self.timer is not None and self.timer.timed_out(delta_time)) or (self.distance is not None and dist(self.agent.pos, self.start_point) >= self.distance):
            self.start_point = self.agent.pos

            dx = random.random()*2 - 1
            dy = random.random()*2 - 1
            self.dir = normalize((dx, dy))

        return self.dir


class Agent(Character):

    def __init__(
        self,
        # typical character properties
        nr_of_abilities: int = NR_ABILITIES,
        pos: tuple = None,
        color: int = None,
        speed: float = PLAYER_SPEED,
        radius: int = PLAYER_RADIUS,
        hp: float = PLAYER_MAX_HP,
        lifetime: float = None,
        damage_flash: bool = True
    ) -> None:
        super().__init__(nr_of_abilities=nr_of_abilities, pos=pos, color=color,
                         speed=speed, radius=radius, hp=hp, lifetime=lifetime, damage_flash=damage_flash)

        self.move_mode = AIMoveLinear(
            self, dir=(1, 0), timer=Timer(3), reverse=True)

    def set_move_mode(self, move_mode: AIMoveMode):
        self.move_mode = move_mode

    def update_dir(self, delta_time):
        self.dir = self.move_mode.get_dir(delta_time)
