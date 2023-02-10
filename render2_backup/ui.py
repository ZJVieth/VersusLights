from typing import Dict
import pygame as pg


class UI:
    def __init__(self) -> None:
        self.btns = {}
        self.fontBase = pg.font.SysFont("Georgia", 30)

    def addButton(self, key: str, text: str, dim: tuple, pos: tuple):
        self.btns[key] = Button(text, dim, pos, self.fontBase)

    def render(self, screen: pg.Surface):
        for key, btn in self.btns.items():
            btn.render(screen)

    def updateButtons(self, mPos):
        mX, mY = mPos
        for key, btn in self.btns.items():
            bX, bY = btn.pos
            bW, bH = btn.dim
            if mX >= bX and mX <= bX + bW and mY >= bY and mY <= bY + bH:
                btn.click()

    def btnClick(self, key: str):
        btn = self.btns[key]
        if btn.clicked:
            btn.reset()
            return True
        return False


class Button:

    def __init__(self, initText: str, initDim: tuple, initPos: tuple, font):
        self.text = initText
        self.dim = initDim
        self.pos = initPos
        self.surf = pg.Surface(self.dim)
        self.surf.fill(pg.Color(255, 255, 255))

        surfText = font.render(self.text, False, pg.Color(100))
        self.surf.blit(surfText, (0, 0))

        self.clicked = False

    def reset(self):
        self.clicked = False

    def click(self):
        self.clicked = True

    def render(self, screen: pg.Surface):
        screen.blit(self.surf, self.pos)
