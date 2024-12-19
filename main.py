import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from objects import *
from sprite_object import *
from weapon import *
from pathfinding import *


class Game:
    def __init__(self):
        # Инициализация игры
        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.game_active = False
        self.menu_background = pg.image.load("resources/textures/sky.png").convert()
        self.new_game()

    def new_game(self):
        # Создание игровых объектов
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.pathfinding = PathFinding(self)

    def update(self):
        # Обновление логики игры
        if self.game_active:
            self.player.update()
            self.raycasting.update()
            self.object_handler.update()
            self.weapon.update()
            pg.display.flip()
            self.delta_time = self.clock.tick(FPS)
            pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        # Отрисовка объектов игры
        if self.game_active:
            self.object_renderer.draw()
            self.weapon.draw()

    def game_events(self):
        # Обработка всех событий игры
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif self.game_active:
                if event.type == self.global_event:
                    self.global_trigger = True
                self.player.single_fire_event(event)
            else:
                self.menu_events(event)

    def menu_events(self, event):
        # Обработка событий меню
        if event.type == pg.MOUSEBUTTONDOWN:
            mx, my = pg.mouse.get_pos()
            if self.play_button.collidepoint(mx, my):
                self.start_game()
            elif self.quit_button.collidepoint(mx, my):
                pg.quit()
                sys.exit()

    def start_game(self):
        # Запуск игрового процесса
        self.game_active = True
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

    def stop_game(self):
        # Остановка игрового процесса
        self.game_active = False
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)

    def draw_menu(self):
        # Отрисовка меню с кнопками
        self.screen.blit(pg.transform.scale(self.menu_background, RES), (0, 0))
        font = pg.font.Font(None, 74)
        play_text = font.render("Играть", True, (255, 255, 255))
        quit_text = font.render("Выйти", True, (255, 255, 255))

        self.play_button = play_text.get_rect(center=(RES[0] // 2, RES[1] // 2 - 50))
        self.quit_button = quit_text.get_rect(center=(RES[0] // 2, RES[1] // 2 + 50))

        self.screen.blit(play_text, self.play_button)
        self.screen.blit(quit_text, self.quit_button)

        pg.display.flip()

    def run(self):
        # Главный игровой цикл
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        while True:
            self.game_events()
            if self.game_active:
                self.update()
                self.draw()
            else:
                self.draw_menu()


if __name__ == '__main__':
    game = Game()
    game.run()
