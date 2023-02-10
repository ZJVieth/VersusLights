
import math
import random

import pygame as pg
from pygame.display import flip
from pygame.locals import *
from agent import AIMoveRandom, Agent
from gpixel import GPixel

from player import Player
from settings import HEIGHT, WIDTH, Color, FPS, GRANITY, LIGHT_MIN, LIGHT_DECAY, Timer, get_delta_time, light_min, grid_width, grid_height
from ability import AbilityHandler
from abilities.basic_abilities import swirling_bolt, bolt, curved_bolt

pg.font.init()
font = pg.font.SysFont("Arial", 18)


def play(screen: pg.Surface, framerate_clock, controllers):
    '''
    SETUP GAMEPHASE
    '''
    screen.fill(0)

    grid = {}

    ah = AbilityHandler()

    ai = Agent(color=Color.CYAN, pos=(100, 100))
    ai.set_move_mode(AIMoveRandom(ai, distance=20))

    players = []
    for i, c in enumerate(controllers):
        if c is None:
            continue
        x = math.floor(random.random()*grid_width())
        y = math.floor(random.random()*grid_height())
        players.append(Player(i, (x, y), c, i))

    # add ais
    # players.append(ai)

    # player2.damage(20)

    hr_bottom = pg.Surface((WIDTH, 2))
    hr_bottom.fill(pg.Color('grey'))

    gameRunning = True
    while gameRunning:
        framerate_clock.tick(FPS)
        pg.display.update()
        delta_time = get_delta_time(framerate_clock.get_fps())

        screen.fill(0)

        fps = str(int(framerate_clock.get_fps()))
        fps_text = font.render(fps, 1, pg.Color('white'))
        screen.blit(fps_text, (10, 10))

        # Updating
        for p in players:
            p.update(delta_time, ah, players)
            p.update_damage_flash(delta_time)
            if p.dead():
                players.remove(p)
        ah.update(delta_time, players)
        ah.check_collision(players, delta_time)

        # # Player 2 Test
        # if not player2.dead():
        #     player2.ai_update(players[0])
        #     p2_timer += 1
        #     p2_fire_timer -= delta_time
        #     p2_fire_timer2 -= delta_time
        #     p2_fire_timer3 -= delta_time
        #     if p2_timer >= 10:
        #         p2_timer = 0

        #         # randomized movement
        #         r1 = random.random()*2 - 1
        #         r2 = random.random()*2 - 1
        #         player2.set_move(0, r1)
        #         player2.set_move(1, r2)

        #     if p2_fire_timer <= 0:
        #         p2_fire_timer = 0.4
        #         # ah.fire(homing_bolt(player2, players))
        #         # ah.fire(bolt(player2))
        #         # ah.fire(curved_x(player2))
        #     if p2_fire_timer2 <= 0:
        #         p2_fire_timer2 = 2
        #         # ah.fire(A_Bolt(player2))
        #         # ah.fire(curved_bolt(player2))
        #     if p2_fire_timer3 <= 0:
        #         p2_fire_timer3 = 2.5
        #         # ah.fire(swirling_bolt(player2))

        # Print Player Entities onto grid
        for i, p in enumerate(players):
            p.render(grid)
            if type(p) is Player:
                p.render_hp(screen, font, i)
                p.render_cursor(screen)

        # Print Ability Entities onto grid
        ah.render(grid)

        # Render grid
        pxarray = pg.PixelArray(screen)
        to_delete = []
        for pos, gp in grid.items():
            gp = grid[pos]
            # find black pixels
            if gp.dead():
                to_delete.append(pos)
                continue
            gp.render(pxarray)
        pxarray.close()

        # Remove black pixels from the grid
        for pos in to_delete:
            del grid[pos]

        # Render UI components
        screen.blit(hr_bottom, (0, 0))
        screen.blit(hr_bottom, (0, grid_height()*GRANITY))
        for i, p in enumerate(players):
            if type(p) is not Player:
                continue
            p.render_ui(screen, font, i)

        # Event Handling
        for event in pg.event.get():
            if event.type == QUIT:
                gameRunning = False
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    gameRunning = False

                # if event.key == K_w:
                #     player.set_move(UP, False)
                # if event.key == K_s:
                #     player.set_move(DOWN, False)
                # if event.key == K_a:
                #     player.set_move(LEFT, False)
                # if event.key == K_d:
                #     player.set_move(RIGHT, False)

            # if event.type == KEYDOWN:

                # if event.key == K_w:
                #     player.set_move(UP, True)
                # if event.key == K_s:
                #     player.set_move(DOWN, True)
                # if event.key == K_a:
                #     player.set_move(LEFT, True)
                # if event.key == K_d:
                #     player.set_move(RIGHT, True)

            # if event.type == MOUSEBUTTONDOWN:
            #     if event.button == M_RIGHT:
            #         ah.fire(A_Bolt(player, pg.mouse.get_pos()))

            if event.type == JOYAXISMOTION:
                for p in players:
                    if type(p) is not Player:
                        continue
                    if p.c_profile is None:
                        continue
                    if event.instance_id == p.c_instance:
                        if event.axis < 2:
                            p.set_move(event.axis, event.value)
                        if event.axis > 1 and event.axis < 4:
                            p.set_view(event.axis, event.value)

                        if event.value >= 0.99:
                            button = -1
                            if event.axis == 4:
                                button = 98
                            if event.axis == 5:
                                button = 99

                            p.ability_button_down(ah, button, players)

            if event.type == JOYBUTTONDOWN:
                for p in players:
                    if type(p) is not Player:
                        continue
                    if p.c_profile is None:
                        continue
                    if event.instance_id == p.c_instance:
                        p.ability_button_down(ah, event.button, players)

            if event.type == JOYBUTTONUP:
                for p in players:
                    if type(p) is not Player:
                        continue
                    if p.c_profile is None:
                        continue
                    if event.instance_id == p.c_instance:
                        p.ability_button_up(ah, event.button, players)
