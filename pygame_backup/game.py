
import math
import random

import pygame as pg
from pygame.locals import *

from player import Player
from settings import WIDTH, Color, FPS, GRANITY, LIGHT_MIN, LIGHT_DECAY, get_delta_time, light_min, grid_width, grid_height
from ability import AbilityHandler
from abilities.basic_abilities import swirling_bolt, bolt, curved_bolt

pg.font.init()
font = pg.font.SysFont("Arial", 18)


def empty_grid():
    output = []
    for x in range(0, grid_width()):
        output.append([])
        for y in range(0, grid_height()):
            output[x].append([LIGHT_MIN]*3)
    return output


def render_grid(screen, grid):

    for x in range(0, grid_width()):
        for y in range(0, grid_height()):
            if sum(grid[x][y]) == 0:
                continue

            # apply decay
            grid[x][y] = [
                light_min(grid[x][y][0] - LIGHT_DECAY),
                light_min(grid[x][y][1] - LIGHT_DECAY),
                light_min(grid[x][y][2] - LIGHT_DECAY)
            ]

            # actually render
            pg.draw.circle(screen, pg.Color(
                grid[x][y][0], grid[x][y][1], grid[x][y][2]), (x*GRANITY, y*GRANITY), 1)


def play(screen: pg.Surface, framerate_clock, controllers):
    '''
    SETUP GAMEPHASE
    '''
    screen.fill(0)

    grid = empty_grid()

    ah = AbilityHandler()

    player2 = Player(Color.CYAN, (100, 100), None)
    # player2.set_move(DOWN, True)
    p2_timer = 0
    p2_fire_timer = 0
    p2_fire_timer2 = 0
    p2_fire_timer3 = 0

    players = []
    for i, c in enumerate(controllers):
        if c is None:
            continue
        x = math.floor(random.random()*grid_width())
        y = math.floor(random.random()*grid_height())
        players.append(Player(i, (x, y), c, i))

    # add ais
    players.append(player2)

    player2.damage(20)

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
        ah.check_collision(players)

        # Player 2 Test
        if not player2.dead():
            player2.ai_update(players[0])
            p2_timer += 1
            p2_fire_timer -= delta_time
            p2_fire_timer2 -= delta_time
            p2_fire_timer3 -= delta_time
            if p2_timer >= 10:
                p2_timer = 0

                # randomized movement
                r1 = random.random()*2 - 1
                r2 = random.random()*2 - 1
                player2.set_move(0, r1)
                player2.set_move(1, r2)

            if p2_fire_timer <= 0:
                p2_fire_timer = 0.4
                # ah.fire(homing_bolt(player2, players))
                ah.fire(bolt(player2))
                # ah.fire(curved_x(player2))
            if p2_fire_timer2 <= 0:
                p2_fire_timer2 = 2
                # ah.fire(A_Bolt(player2))
                ah.fire(curved_bolt(player2))
            if p2_fire_timer3 <= 0:
                p2_fire_timer3 = 2.5
                ah.fire(swirling_bolt(player2))

        # Print Entities onto grid
        for i, p in enumerate(players):
            p.render(grid)
            p.render_hp(screen, font, i)
            p.render_cursor(screen)

        ah.render(grid)

        # Render grid
        render_grid(screen, grid)

        screen.blit(hr_bottom, (0, 0))
        screen.blit(hr_bottom, (0, grid_height()*GRANITY))

        for i, p in enumerate(players):
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
                    if p.c_profile is None:
                        continue
                    if event.instance_id == p.c_instance:
                        p.ability_button_down(ah, event.button, players)

            if event.type == JOYBUTTONUP:
                for p in players:
                    if p.c_profile is None:
                        continue
                    if event.instance_id == p.c_instance:
                        p.ability_button_up(ah, event.button, players)
