from ability import ABILITY_TABLE, sign
from player import ControllerProfile
import sys
import pygame as pg
from pygame.locals import *

from game import play
from settings import NR_ABILITIES, TITLE, WIDTH, HEIGHT, FPS, light_color
from ui import UI


pg.init()
pg.font.init()
pg.joystick.init()

if __name__ == "__main__":

    '''
    SETUP ---------------------------------------------------------------------
    '''
    flags = FULLSCREEN | DOUBLEBUF | HWSURFACE
    pg.event.set_allowed(
        [QUIT, KEYDOWN, JOYAXISMOTION, JOYBUTTONUP, JOYBUTTONDOWN, MOUSEBUTTONUP])

    # , flags)  # , pg.FULLSCREEN)
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption(TITLE)
    framerate_clock = pg.time.Clock()

    uiMenu = UI()
    uiMenu.addButton('play', "Play", (100, 50), (100, 100))
    uiFont = pg.font.SysFont("Georgia", 18)

    joysticks = [pg.joystick.Joystick(x)
                 for x in range(0, pg.joystick.get_count())]
    print(joysticks)

    c_xbox = ControllerProfile("XBox One")
    c_xbox.set_button(0, 98, "Homing Bolt")
    c_xbox.set_button(1, 99, "Bolt")
    c_xbox.set_button(2, 4, "Swirling Bolt")
    c_xbox.set_button(3, 5, "Frost Field")
    c_xbox.set_button(4, 1, "Flamethrower")
    c_xbox.set_button(5, 0, "Bolt")

    c_switch = ControllerProfile("Nintendo Switch")
    c_switch.set_button(0, 98, "Volley")
    c_switch.set_button(1, 99, "Bolt")
    c_switch.set_button(2, 9, "Swirling Bolt")
    c_switch.set_button(3, 10, "Blink")
    c_switch.set_button(4, 0, "Flamethrower")
    c_switch.set_button(5, 1, "Bolt")

    profiles = [c_xbox, c_switch]

    controllers = [None]*len(joysticks)
    select_index = [0]*len(joysticks)

    '''
    MAIN LOOP ------------------------------------------------------------------
    '''
    programRunning = True
    while programRunning:
        framerate_clock.tick(FPS)
        pg.display.flip()

        screen.fill(pg.Color('black'))

        uiMenu.render(screen)

        for i, c in enumerate(controllers):
            if c is None:
                continue
            txt = uiFont.render(
                c.name, False, pg.Color(light_color(255, i)))
            screen.blit(txt, (50+i*350, 175))

            for j in range(NR_ABILITIES):
                str_content = str(c.buttons[j]) + ": " + c.abilities[j]
                if j == select_index[i]:
                    str_content = "-> " + str_content
                txt = uiFont.render(
                    str_content, False, pg.Color(light_color(255, i)))
                screen.blit(txt, (50+i*350, 225+j*50))

        if uiMenu.btnClick('play'):
            play(screen, framerate_clock, controllers)

        for event in pg.event.get():
            if event.type == QUIT:
                programRunning = False

            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    programRunning = False

            if event.type == MOUSEBUTTONUP:
                uiMenu.updateButtons(pg.mouse.get_pos())

            if event.type == JOYAXISMOTION:
                c_id = event.instance_id
                # print(event)
                if abs(event.value) >= 0.99:
                    if event.axis == 1:
                        select_index[event.instance_id] += sign(event.value)
                        if select_index[c_id] >= NR_ABILITIES:
                            select_index[c_id] = 0
                        if select_index[c_id] < 0:
                            select_index[c_id] = 5

                    if event.axis == 0:
                        c = controllers[c_id]
                        if c is not None:
                            next_index = list(ABILITY_TABLE.keys()).index(
                                c.abilities[select_index[c_id]]) + sign(event.value)
                            if next_index >= len(ABILITY_TABLE):
                                next_index = 0
                            if next_index < 0:
                                next_index = len(ABILITY_TABLE) - 1
                            c.set_button(
                                select_index[c_id], c.buttons[select_index[c_id]], list(ABILITY_TABLE.keys())[next_index])

                    if event.axis == 2:
                        c = controllers[c_id]
                        next_index = profiles.index(c) + sign(event.value)
                        if next_index >= len(profiles):
                            next_index = 0
                        if next_index < 0:
                            next_index = len(profiles) - 1
                        controllers[c_id] = profiles[next_index]

                    c = controllers[c_id]
                    if c is not None:
                        if event.axis == 4:
                            c.set_button(
                                select_index[c_id], 98, c.abilities[select_index[c_id]]
                            )
                        if event.axis == 5:
                            c.set_button(
                                select_index[c_id], 99, c.abilities[select_index[c_id]]
                            )

            if event.type == JOYBUTTONDOWN:
                # print(event.button)
                c = controllers[event.instance_id]
                if c is None:
                    controllers[event.instance_id] = profiles[0]
                else:
                    c.set_button(
                        select_index[event.instance_id], event.button, c.abilities[select_index[event.instance_id]]
                    )

    pg.joystick.quit()
    pg.quit()
    sys.exit()
