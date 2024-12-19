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
        self.screen = pg.display.set_mode((800, 600))  # иниц дисплея
        self.mock_game = Mock()
        self.mock_game.screen = self.screen  # экран для отрисовки

        # мок карта
        self.map = Map(self.mock_game)

    def tearDown(self):
        pg.quit()

    def test_initialization(self):
        # тест иниц карты
        self.assertEqual(self.map.rows, len(self.map.mini_map))
        self.assertEqual(self.map.cols, len(self.map.mini_map[0]))
        self.assertTrue(isinstance(self.map.world_map, dict))

    def test_get_map(self):
        # проверка заполненности карты 
        self.map.get_map()
        self.assertGreater(len(self.map.world_map), 0) 

        expected = {(0, 0), (0, 1), (1, 0)} 
        actual = set(self.map.world_map.keys())
        self.assertTrue(expected.issubset(actual))

    @patch('map.pg.draw.rect')
    def test_draw(self, mock_draw_rect):
        # проверка отрисовки
        self.map.draw()

        # проверка вызова доя всех блоков
        self.assertEqual(mock_draw_rect.call_count, len(self.map.world_map))


class TestNPC(unittest.TestCase):

    def setUp(self):
        # иниц pygame для графики
        pg.init()
        pg.display.set_mode((800, 600))  # создает экран для работы

        # mock для игровой логики
        self.mock_game = Mock()
        self.mock_game.player.get_pos.return_value = (400, 400)  # позиция игрока
        self.mock_game.objects = []  # тестовая сцена

        # пример нпс 
        self.npc = NPC(self.mock_game)

    def tearDown(self):
        pg.quit()

    def test_initialization(self):
        self.assertTrue(self.npc.alive)
        self.assertEqual(self.npc.health, 100)  
        self.assertEqual(self.npc.speed, 0.03)
        self.assertEqual(self.npc.size, 20)


class TestObjectHandler(unittest.TestCase):

    def setUp(self):
        self.mock_game = Mock()
        self.mock_game.get_score.return_value = 5
        self.mock_game.win_score = 10 

        self.handler = ObjectHandler(self.mock_game)

class TestObjectRenderer(unittest.TestCase):

    def setUp(self):
        pg.init()
        pg.display.set_mode((800, 600))

        # мок игры
        self.mock_game = Mock()
        self.mock_game.screen = pg.display.get_surface()
        self.mock_game.health = 100

        # экземпляр ObjectRenderer
        self.renderer = ObjectRenderer(self.mock_game)
        self.renderer.sky_image = pg.Surface((800, 600)) 
        self.renderer.digits = {str(i): pg.Surface((20, 20)) for i in range(10)}
        self.renderer.win_image = pg.Surface((400, 200)) 

    def tearDown(self):
        pg.quit()


class TestPathFinding(unittest.TestCase):
    def setUp(self):
        self.mock_game = Mock()
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
        self.mock_game.object_handler.npc_positions = set()

        self.pathfinding = PathFinding(self.mock_game)

    def test_get_graph(self):
        self.pathfinding.get_graph()
        graph = self.pathfinding.graph

        self.assertIn((0, 0), graph) 
        self.assertNotIn((1, 1), graph) 
        self.assertIn((0, 3), graph)

    def test_bfs(self):
        graph = {
            (0, 0): [(0, 1), (1, 0)],
            (0, 1): [(0, 0), (1, 1)],
            (1, 0): [(0, 0), (1, 1)],
            (1, 1): [(0, 1), (1, 0)]
        }
        start = (0, 0)
        goal = (1, 1)

        visited = self.pathfinding.bfs(start, goal, graph)
        self.assertIn(goal, visited) 
        self.assertEqual(visited[goal], (0, 1))

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
        self.mock_game = Mock()
        self.mock_game.map.world_map = {
            (1, 1): None
        }
        self.mock_game.weapon.reloading = False
        self.mock_game.delta_time = 1.0
        self.mock_game.screen = Mock()

        self.patcher_time = patch('player.pg.time.get_ticks', return_value=1000)
        self.mock_time = self.patcher_time.start()

        self.player = Player(self.mock_game)

    def tearDown(self):
        self.patcher_time.stop()

    def test_recover_health(self):
        self.player.health = 5
        self.mock_time.return_value = 2000
        self.player.recover_health()
        self.assertEqual(self.player.health, 6)

    def test_recover_health_max_limit(self):
        self.player.health = 10
        self.player.recover_health()
        self.assertEqual(self.player.health, 10)

    def test_check_health_recovery_delay(self):
        self.mock_time.return_value = 2000
        result = self.player.check_health_recovery_delay()
        self.assertTrue(result)

    @patch('player.pg.time.delay')
    @patch('player.pg.display.flip')
    def test_check_game_over(self, mock_display_flip, mock_time_delay):
        self.player.health = 0
        self.player.check_game_over()
        mock_display_flip.assert_called_once()
        mock_time_delay.assert_called_once_with(1500)

    def test_get_damage(self):
        self.player.health = 10
        self.player.get_damage(3)
        self.assertEqual(self.player.health, 7)

    def test_pos_property(self):
        self.assertEqual(self.player.pos, (self.player.x, self.player.y))

    def test_map_pos_property(self):
        self.assertEqual(self.player.map_pos, (int(self.player.x), int(self.player.y)))

    @patch('player.pg.MOUSEBUTTONDOWN')
    def test_single_fire_event(self, mock_event_type):
        mock_event = Mock()
        mock_event.type = pg.MOUSEBUTTONDOWN
        mock_event.button = 1
        self.player.shot = False
        self.mock_game.weapon.reloading = False

        self.player.single_fire_event(mock_event)
        self.assertTrue(self.player.shot)
        self.assertTrue(self.mock_game.weapon.reloading)

    @patch.object(Player, 'movement', return_value=None)
    @patch.object(Player, 'mouse_control', return_value=None)
    @patch.object(Player, 'recover_health', return_value=None)
    def test_update(self, mock_recover_health, mock_mouse_control, mock_movement):
        self.player.update()
        mock_movement.assert_called_once()
        mock_mouse_control.assert_called_once()
        mock_recover_health.assert_called_once()


class TestRayCasting(unittest.TestCase):
    def setUp(self):
        self.mock_game = Mock()
        self.mock_game.object_renderer.wall_textures = [Mock()] * 10  # имитация текстуры стен
        self.mock_game.map.world_map = {
            (1, 1): 1,
            (2, 2): 2
        }
        self.mock_game.player.pos = (1.5, 1.5)
        self.mock_game.player.map_pos = (1, 1)
        self.mock_game.player.angle = 0
        self.ray_casting = RayCasting(self.mock_game)

    @patch('raycasting.pg.transform.scale', return_value=Mock())
    @patch('raycasting.pg.Surface', return_value=Mock())
    def test_get_objects_to_render(self, mock_surface, mock_scale):
        self.ray_casting.ray_casting_result = [
            (1.0, 50, 1, 0.5),
            (2.0, 100, 2, 0.3)
        ]

        self.ray_casting.get_objects_to_render()

        self.assertGreater(len(self.ray_casting.objects_to_render), 0)
        self.assertEqual(len(self.ray_casting.objects_to_render), len(self.ray_casting.ray_casting_result))

    def test_ray_cast(self):
        self.ray_casting.ray_cast()

        self.assertGreater(len(self.ray_casting.ray_casting_result), 0)
        for result in self.ray_casting.ray_casting_result:
            self.assertEqual(len(result), 4)

    @patch.object(RayCasting, 'ray_cast', return_value=None)
    @patch.object(RayCasting, 'get_objects_to_render', return_value=None)
    def test_update(self, mock_get_objects_to_render, mock_ray_cast):
        self.ray_casting.update()

        mock_ray_cast.assert_called_once()
        mock_get_objects_to_render.assert_called_once()


class TestWeapon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.init()
        pg.display.set_mode((800, 600))  # мок дисплей

    @classmethod
    def tearDownClass(cls):
        pg.quit()

    def setUp(self):
        # мок объекта
        self.mock_game = Mock()
        self.mock_game.player = Mock()
        self.mock_game.screen = Mock()  # имитация blit

        self.weapon = Weapon(self.mock_game, scale=0.5)
        self.weapon.images = deque([pg.Surface((50, 50)) for _ in range(3)])
        self.weapon.num_images = len(self.weapon.images)

    def test_animate_shot(self):
        self.weapon.reloading = True
        self.weapon.animation_trigger = True
        self.weapon.frame_counter = 0

        self.weapon.animate_shot()

        self.assertEqual(self.weapon.frame_counter, 1)
        self.assertEqual(self.weapon.image, self.weapon.images[0])
        self.assertTrue(self.weapon.reloading)

        self.weapon.frame_counter = self.weapon.num_images - 1
        self.weapon.animate_shot()

        self.assertEqual(self.weapon.frame_counter, 0)
        self.assertFalse(self.weapon.reloading)

    def test_draw(self):
        self.weapon.draw()
        self.mock_game.screen.blit.assert_called_once_with(
            self.weapon.images[0], self.weapon.weapon_pos
        )

    def test_update(self):
        self.weapon.check_animation_time = Mock()
        self.weapon.animate_shot = Mock()

        self.weapon.update()

        self.weapon.check_animation_time.assert_called_once()
        self.weapon.animate_shot.assert_called_once()


class TestSpriteObject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.init()
        pg.display.set_mode((800, 600))

    @classmethod
    def tearDownClass(cls):
        pg.quit()

    def setUp(self):
        self.mock_game = Mock()
        self.mock_game.player = Mock()
        self.mock_game.screen = pg.Surface((800, 600))  # мок экран как pygame Surface
        self.mock_game.raycasting.objects_to_render = []

        self.sprite = SpriteObject(self.mock_game, pos=(5, 5), scale=0.7)

    def test_get_sprite(self):
        self.mock_game.player.x = 0
        self.mock_game.player.y = 0
        self.mock_game.player.angle = math.pi / 2

        self.sprite.get_sprite()

        # проверка, что метод get_sprite_projection был вызван
        self.assertTrue(len(self.mock_game.raycasting.objects_to_render) > 0)

    def test_get_sprite_projection(self):
        # нормализованное расстояние
        self.sprite.norm_dist = 10
        self.sprite.IMAGE_WIDTH = 100
        self.sprite.IMAGE_HEIGHT = 50
        self.sprite.SPRITE_SCALE = 0.5
        self.sprite.SPRITE_HEIGHT_SHIFT = 0.3
        self.sprite.screen_x = 400

        # мок render
        self.sprite.get_sprite_projection()
        self.assertTrue(len(self.mock_game.raycasting.objects_to_render) > 0)


class TestAnimatedSprite(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # иниц pygame для предотвращения ошибок
        pg.init()
        pg.display.set_mode((800, 600))

    @classmethod
    def tearDownClass(self):
        pg.quit()

    def setUp(self):
        # мок объект игры
        self.mock_game = Mock()
        self.mock_game.player = Mock()
        self.mock_game.screen = pg.Surface((800, 600)) 
        self.mock_game.raycasting.objects_to_render = []

        self.animated_sprite = AnimatedSprite(self.mock_game, pos=(5, 5), scale=0.7, animation_time=100)
        self.animated_sprite.images = deque([pg.Surface((50, 50)) for _ in range(3)])  # иок изображения

    def test_animate(self):
        # анимация для проверки
        self.animated_sprite.animation_trigger = True

        self.animated_sprite.animate(self.animated_sprite.images)

        self.assertEqual(self.animated_sprite.image, self.animated_sprite.images[0])

    def test_check_animation_time(self):
        # проверка работы времени анимации
        prev_time = pg.time.get_ticks()
        self.animated_sprite.animation_time_prev = prev_time - 200

        self.animated_sprite.check_animation_time()

        self.assertTrue(self.animated_sprite.animation_trigger)


if __name__ == "__main__":
    unittest.main()
