import unittest
from unittest.mock import Mock, patch
from collections import deque
import pygame as pg
import math
from weapon import Weapon
from sprite_object import SpriteObject, AnimatedSprite
from raycasting import RayCasting
from player import Player
from pathfinding import PathFinding
from objects import ObjectHandler, ObjectRenderer
from npc import NPC
from map import Map
from main import Game

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    @patch('pygame.display.set_mode')
    @patch('pygame.init')
    def test_game_initialization(self, mock_pg_init, mock_set_mode):
        game = Game()
        mock_pg_init.assert_called_once()
        mock_set_mode.assert_called_once()

    @patch('pygame.event.get')
    def test_game_events_quit(self, mock_pg_event_get):
        mock_pg_event_get.return_value = [Mock(type=pg.QUIT)]
        with self.assertRaises(SystemExit):
            self.game.game_events()

    @patch('pygame.event.get')
    def test_game_events_key_escape(self, mock_pg_event_get):
        mock_pg_event_get.return_value = [Mock(type=pg.KEYDOWN, key=pg.K_ESCAPE)]
        with self.assertRaises(SystemExit):
            self.game.game_events()

    @patch('pygame.event.get')
    def test_game_events_global_event(self, mock_pg_event_get):
        mock_pg_event_get.return_value = [Mock(type=self.game.global_event)]
        self.game.game_events()
        self.assertTrue(not(self.game.global_trigger))

    @patch('pygame.mouse.get_pos')
    @patch('pygame.event.get')
    def test_menu_events_play_button(self, mock_pg_event_get, mock_mouse_get_pos):
        mock_mouse_get_pos.return_value = (100, 150)
        self.game.play_button = Mock(collidepoint=lambda x, y: True)
        mock_pg_event_get.return_value = [Mock(type=pg.MOUSEBUTTONDOWN)]
        with patch.object(self.game, 'start_game', return_value=None) as mock_start_game:
            self.game.menu_events(Mock(type=pg.MOUSEBUTTONDOWN))
            mock_start_game.assert_called_once()

    @patch('pygame.mouse.set_visible')
    @patch('pygame.event.set_grab')
    def test_start_game(self, mock_pg_event_grab, mock_pg_mouse_visible):
        self.game.start_game()
        self.assertTrue(self.game.game_active)
        mock_pg_event_grab.assert_called_with(True)
        mock_pg_mouse_visible.assert_called_with(False)

    @patch('pygame.mouse.set_visible')
    @patch('pygame.event.set_grab')
    def test_stop_game(self, mock_pg_event_grab, mock_pg_mouse_visible):
        self.game.stop_game()
        self.assertFalse(self.game.game_active)
        mock_pg_event_grab.assert_called_with(False)
        mock_pg_mouse_visible.assert_called_with(True)


if __name__ == "__main__":
    unittest.main()


class TestMap(unittest.TestCase):

    def setUp(self):
        # Инициализация pygame (так как используется для рисования)
        pg.init()
        self.screen = pg.display.set_mode((800, 600))  # Создаем игровой экран
        self.mock_game = Mock()
        self.mock_game.screen = self.screen  # Экран, который будет использоваться для отрисовки

        # Создаем экземпляр карты
        self.map = Map(self.mock_game)

    def tearDown(self):
        # Завершаем pygame
        pg.quit()

    def test_initialization(self):
        # Тестируем правильную инициализацию карты
        self.assertEqual(self.map.rows, len(self.map.mini_map))
        self.assertEqual(self.map.cols, len(self.map.mini_map[0]))
        self.assertTrue(isinstance(self.map.world_map, dict))

    def test_get_map(self):
        # Убедимся, что world_map правильно заполняется
        self.map.get_map()
        self.assertGreater(len(self.map.world_map), 0)  # Проверка, что карта не пуста

        # Проверяем несколько ключей
        expected = {(0, 0), (0, 1), (1, 0)}  # Пример координат
        actual = set(self.map.world_map.keys())
        self.assertTrue(expected.issubset(actual))  # Убедимся, что ключи присутствуют в карте

    @patch('map.pg.draw.rect')
    def test_draw(self, mock_draw_rect):
        # Проверяем метод отрисовки
        self.map.draw()

        # Убедимся, что метод pg.draw.rect вызван для каждого блока карты
        self.assertEqual(mock_draw_rect.call_count, len(self.map.world_map))


class TestNPC(unittest.TestCase):

    def setUp(self):
        # Инициализируем pygame (для графики и объектов)
        pg.init()
        pg.display.set_mode((800, 600))  # создает экран для работы

        # Создаем mock для игровой логики
        self.mock_game = Mock()
        self.mock_game.player.get_pos.return_value = (400, 400)  # позиция игрока
        self.mock_game.objects = []  # тестовая сцена

        # Создаем экземпляр NPC
        self.npc = NPC(self.mock_game)

    def tearDown(self):
        # Завершаем pygame
        pg.quit()

    def test_initialization(self):
        # Проверяем параметры и инициализацию NPC
        self.assertTrue(self.npc.alive)
        self.assertEqual(self.npc.health, 100)  # Предполагаемое значение здоровья по умолчанию
        self.assertEqual(self.npc.speed, 0.03)  # Скорость перемещения
        self.assertEqual(self.npc.size, 20)  # Размер


class TestObjectHandler(unittest.TestCase):

    def setUp(self):
        # Создание мока для игровой логики
        self.mock_game = Mock()
        self.mock_game.get_score.return_value = 5  # Устанавливаем mock для реального значения очков
        self.mock_game.win_score = 10  # Условие победы

        # Создание экземпляра ObjectHandler
        self.handler = ObjectHandler(self.mock_game)

class TestObjectRenderer(unittest.TestCase):

    def setUp(self):
        # Инициализация pygame
        pg.init()
        pg.display.set_mode((800, 600))

        # Создание мока игры
        self.mock_game = Mock()
        self.mock_game.screen = pg.display.get_surface()  # Эмуляция игрового экрана
        self.mock_game.health = 100  # Устанавливаем здоровье игрока

        # Создание экземпляра ObjectRenderer
        self.renderer = ObjectRenderer(self.mock_game)
        self.renderer.sky_image = pg.Surface((800, 600))  # Эмуляция изображения неба
        self.renderer.digits = {str(i): pg.Surface((20, 20)) for i in range(10)}  # Эмуляция цифр
        self.renderer.win_image = pg.Surface((400, 200))  # Эмуляция изображения победы

    def tearDown(self):
        # Завершение работы pygame
        pg.quit()


class TestPathFinding(unittest.TestCase):
    def setUp(self):
        # Создаем имитацию игры (mock_game)
        self.mock_game = Mock()
        # Мини-карта: 0 - свободно; 1 - стена
        self.mock_game.map.mini_map = [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0]
        ]
        self.mock_game.map.world_map = {
            (1, 1): 1,
            (1, 2): 1,
            (2, 1): 1
        }
        self.mock_game.object_handler.npc_positions = set()  # Нет NPC на пути

        # Создаем объект PathFinding с мок-игрой
        self.pathfinding = PathFinding(self.mock_game)

    def test_get_graph(self):
        # Проверяем построение графа
        self.pathfinding.get_graph()
        graph = self.pathfinding.graph

        # Примеры проверок
        self.assertIn((0, 0), graph)  # Узел (0,0) должен быть в графе
        self.assertNotIn((1, 1), graph)  # Узел (1,1) - препятствие, его быть не должно
        self.assertIn((0, 3), graph)  # Узел (0,3) в графе (свободная зона)

    def test_bfs(self):
        # Проверяем поиск в ширину
        graph = {
            (0, 0): [(0, 1), (1, 0)],
            (0, 1): [(0, 0), (1, 1)],
            (1, 0): [(0, 0), (1, 1)],
            (1, 1): [(0, 1), (1, 0)]
        }
        start = (0, 0)
        goal = (1, 1)

        visited = self.pathfinding.bfs(start, goal, graph)
        self.assertIn(goal, visited)  # Цель должна быть достигнута
        self.assertEqual(visited[goal], (0, 1))  # Шаг к цели должен быть корректным

    @patch.object(PathFinding, 'bfs', return_value={
        (3, 0): (2, 0),
        (2, 0): (1, 0),
        (1, 0): (0, 0),
        (0, 0): None
    })
    def test_get_path(self, mock_bfs):
        start = (0, 0)
        goal = (3, 0)
        path = self.pathfinding.get_path(start, goal)

        self.assertEqual(path, (1, 0))


class TestPlayer(unittest.TestCase):
    def setUp(self):
        # Создаем имитацию игры (mock_game)
        self.mock_game = Mock()
        self.mock_game.map.world_map = {
            (1, 1): None
        }
        self.mock_game.weapon.reloading = False  # Создаем атрибут для вооружения
        self.mock_game.delta_time = 1.0
        self.mock_game.screen = Mock()

        # Настраиваем mock для получения времени
        self.patcher_time = patch('player.pg.time.get_ticks', return_value=1000)
        self.mock_time = self.patcher_time.start()

        # Создаем объект Player с mock-игрой
        self.player = Player(self.mock_game)

    def tearDown(self):
        self.patcher_time.stop()

    def test_recover_health(self):
        # Проверяем восстановление здоровья
        self.player.health = 5
        self.mock_time.return_value = 2000  # Эмуляция задержки времени
        self.player.recover_health()
        self.assertEqual(self.player.health, 6)

    def test_recover_health_max_limit(self):
        # Проверяем, что здоровье не превышает максимум
        self.player.health = 10
        self.player.recover_health()
        self.assertEqual(self.player.health, 10)

    def test_check_health_recovery_delay(self):
        # Проверяем задержку для восстановления здоровья
        self.mock_time.return_value = 2000
        result = self.player.check_health_recovery_delay()
        self.assertTrue(result)

    @patch('player.pg.time.delay')
    @patch('player.pg.display.flip')
    def test_check_game_over(self, mock_display_flip, mock_time_delay):
        # Проверяем вызов при состоянии game over
        self.player.health = 0
        self.player.check_game_over()
        mock_display_flip.assert_called_once()
        mock_time_delay.assert_called_once_with(1500)

    def test_get_damage(self):
        # Проверяем получение урона
        self.player.health = 10
        self.player.get_damage(3)
        self.assertEqual(self.player.health, 7)

    def test_pos_property(self):
        # Проверяем свойство pos
        self.assertEqual(self.player.pos, (self.player.x, self.player.y))

    def test_map_pos_property(self):
        # Проверяем свойство map_pos
        self.assertEqual(self.player.map_pos, (int(self.player.x), int(self.player.y)))

    @patch('player.pg.MOUSEBUTTONDOWN')
    def test_single_fire_event(self, mock_event_type):
        # Проверяем одиночное событие выстрела
        mock_event = Mock()
        mock_event.type = pg.MOUSEBUTTONDOWN
        mock_event.button = 1

        # Установим начальное состояние
        self.player.shot = False
        self.mock_game.weapon.reloading = False

        self.player.single_fire_event(mock_event)
        self.assertTrue(self.player.shot)
        self.assertTrue(self.mock_game.weapon.reloading)

    @patch.object(Player, 'movement', return_value=None)
    @patch.object(Player, 'mouse_control', return_value=None)
    @patch.object(Player, 'recover_health', return_value=None)
    def test_update(self, mock_recover_health, mock_mouse_control, mock_movement):
        # Проверяем вызовы в методе update
        self.player.update()
        mock_movement.assert_called_once()
        mock_mouse_control.assert_called_once()
        mock_recover_health.assert_called_once()


class TestRayCasting(unittest.TestCase):
    def setUp(self):
        # Создаем имитацию игры (mock_game)
        self.mock_game = Mock()
        self.mock_game.object_renderer.wall_textures = [Mock()] * 10  # Имитируем текстуры стен
        self.mock_game.map.world_map = {
            (1, 1): 1,  # Пример карты с одной стеной
            (2, 2): 2
        }
        self.mock_game.player.pos = (1.5, 1.5)
        self.mock_game.player.map_pos = (1, 1)
        self.mock_game.player.angle = 0

        # Создаем экземпляр RayCasting с мок-объектом
        self.ray_casting = RayCasting(self.mock_game)

    @patch('raycasting.pg.transform.scale', return_value=Mock())
    @patch('raycasting.pg.Surface', return_value=Mock())
    def test_get_objects_to_render(self, mock_surface, mock_scale):
        # Устанавливаем тестовые значения для ray_casting_result
        self.ray_casting.ray_casting_result = [
            (1.0, 50, 1, 0.5),  # Пример данных
            (2.0, 100, 2, 0.3)
        ]

        # Вызываем метод get_objects_to_render
        self.ray_casting.get_objects_to_render()

        # Проверяем, заполнились ли объекты для рендера
        self.assertGreater(len(self.ray_casting.objects_to_render), 0)
        self.assertEqual(len(self.ray_casting.objects_to_render), len(self.ray_casting.ray_casting_result))

    def test_ray_cast(self):
        # Вызываем метод ray_cast
        self.ray_casting.ray_cast()

        # Проверяем, что результат рейтрейсинга заполнен
        self.assertGreater(len(self.ray_casting.ray_casting_result), 0)
        for result in self.ray_casting.ray_casting_result:
            self.assertEqual(len(result), 4)  # Должно быть 4 значения (depth, proj_height, texture, offset)

    @patch.object(RayCasting, 'ray_cast', return_value=None)
    @patch.object(RayCasting, 'get_objects_to_render', return_value=None)
    def test_update(self, mock_get_objects_to_render, mock_ray_cast):
        # Вызываем метод update
        self.ray_casting.update()

        # Проверяем, что методы ray_cast и get_objects_to_render были вызваны
        mock_ray_cast.assert_called_once()
        mock_get_objects_to_render.assert_called_once()


class TestWeapon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Инициализация pygame для предотвращения ошибок
        pg.init()
        pg.display.set_mode((800, 600))  # Создание dummy дисплея

    @classmethod
    def tearDownClass(cls):
        # Завершение работы с pygame после всех тестов
        pg.quit()

    def setUp(self):
        # Мок объекта игры
        self.mock_game = Mock()
        self.mock_game.player = Mock()
        self.mock_game.screen = Mock()  # Мокаем экран для имитации поведения blit

        # Инициализация объекта Weapon
        self.weapon = Weapon(self.mock_game, scale=0.5)
        self.weapon.images = deque([pg.Surface((50, 50)) for _ in range(3)])  # Мокаем изображения как deque
        self.weapon.num_images = len(self.weapon.images)

    def test_animate_shot(self):
        # Устанавливаем состояние перезарядки и активируем анимацию
        self.weapon.reloading = True
        self.weapon.animation_trigger = True
        self.weapon.frame_counter = 0

        # Вызываем метод
        self.weapon.animate_shot()

        # Проверяем ожидаемые изменения состояния
        self.assertEqual(self.weapon.frame_counter, 1)
        self.assertEqual(self.weapon.image, self.weapon.images[0])
        self.assertTrue(self.weapon.reloading)

        # Симулируем последний кадр анимации
        self.weapon.frame_counter = self.weapon.num_images - 1
        self.weapon.animate_shot()

        self.assertEqual(self.weapon.frame_counter, 0)
        self.assertFalse(self.weapon.reloading)

    def test_draw(self):
        # Вызываем метод draw и проверяем, взаимодействует ли он с мокированным экраном
        self.weapon.draw()
        self.mock_game.screen.blit.assert_called_once_with(
            self.weapon.images[0], self.weapon.weapon_pos
        )

    def test_update(self):
        # Мокаем методы, вызываемые внутри update
        self.weapon.check_animation_time = Mock()
        self.weapon.animate_shot = Mock()

        # Вызываем метод
        self.weapon.update()

        # Проверяем вызовы методов
        self.weapon.check_animation_time.assert_called_once()
        self.weapon.animate_shot.assert_called_once()


class TestSpriteObject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Инициализация pygame для предотвращения ошибок
        pg.init()
        pg.display.set_mode((800, 600))  # Создание dummy дисплея

    @classmethod
    def tearDownClass(cls):
        # Завершение работы с pygame после всех тестов
        pg.quit()

    def setUp(self):
        # Мокаем объект игры
        self.mock_game = Mock()
        self.mock_game.player = Mock()
        self.mock_game.screen = pg.Surface((800, 600))  # Мокаем экран как pygame Surface
        self.mock_game.raycasting.objects_to_render = []

        # Создаем объект SpriteObject
        self.sprite = SpriteObject(self.mock_game, pos=(5, 5), scale=0.7)

    def test_get_sprite(self):
        # Мокаем позицию игрока
        self.mock_game.player.x = 0
        self.mock_game.player.y = 0
        self.mock_game.player.angle = math.pi / 2

        # Вызываем метод get_sprite
        self.sprite.get_sprite()

        # Проверяем, что метод get_sprite_projection был вызван
        self.assertTrue(len(self.mock_game.raycasting.objects_to_render) > 0)

    def test_get_sprite_projection(self):
        # Устанавливаем нормализованное расстояние
        self.sprite.norm_dist = 10
        self.sprite.IMAGE_WIDTH = 100
        self.sprite.IMAGE_HEIGHT = 50
        self.sprite.SPRITE_SCALE = 0.5
        self.sprite.SPRITE_HEIGHT_SHIFT = 0.3
        self.sprite.screen_x = 400

        # Мокаем метод render
        self.sprite.get_sprite_projection()

        # Проверяем, что объекты добавляются в список для рендеринга
        self.assertTrue(len(self.mock_game.raycasting.objects_to_render) > 0)


class TestAnimatedSprite(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Инициализация pygame для предотвращения ошибок
        pg.init()
        pg.display.set_mode((800, 600))  # Создание dummy дисплея

    @classmethod
    def tearDownClass(self):
        # Завершение работы с pygame после всех тестов
        pg.quit()

    def setUp(self):
        # Мокаем объект игры
        self.mock_game = Mock()
        self.mock_game.player = Mock()
        self.mock_game.screen = pg.Surface((800, 600))  # Мокаем экран как pygame Surface
        self.mock_game.raycasting.objects_to_render = []

        # Создаем объект AnimatedSprite
        self.animated_sprite = AnimatedSprite(self.mock_game, pos=(5, 5), scale=0.7, animation_time=100)
        self.animated_sprite.images = deque([pg.Surface((50, 50)) for _ in range(3)])  # Мокаем изображения

    def test_animate(self):
        # Устанавливаем анимацию для проверки
        self.animated_sprite.animation_trigger = True

        # Вызываем метод animate
        self.animated_sprite.animate(self.animated_sprite.images)

        # Проверяем, что изображение было изменено
        self.assertEqual(self.animated_sprite.image, self.animated_sprite.images[0])

    def test_check_animation_time(self):
        # Проверяем работу времени анимации
        prev_time = pg.time.get_ticks()
        self.animated_sprite.animation_time_prev = prev_time - 200

        # Вызываем метод check_animation_time
        self.animated_sprite.check_animation_time()

        # Проверяем, что флаг анимации был обновлен
        self.assertTrue(self.animated_sprite.animation_trigger)


if __name__ == "__main__":
    unittest.main()
