import pygame
from utils.game import get_fps_from_clock_tick, quit_pygame_and_exit
from utils.graphics import redraw_game_screen
from utils.maenneltest import Maenneltest

MAX_FPS = 60
PLAYER_RIGHT = 'Mimi'
PLAYER_LEFT = 'Mama'
MOVE_LEFT = (1, 0)
MOVE_RIGHT = (-1, 0)
MOVE_UP = (0, -1)
MOVE_DOWN = (0, 1)
KEY_MAPPINGS = [
    {"player": PLAYER_LEFT, "keys": {
        pygame.K_d: MOVE_LEFT,
        pygame.K_a: MOVE_RIGHT,
        pygame.K_w: MOVE_UP,
        pygame.K_s: MOVE_DOWN,
    }},
    {"player": PLAYER_RIGHT, "keys": {
        pygame.K_RIGHT: MOVE_LEFT,
        pygame.K_LEFT: MOVE_RIGHT,
        pygame.K_UP: MOVE_UP,
        pygame.K_DOWN: MOVE_DOWN,
    }},
]


def main():
    pygame.init()
    clock = pygame.time.Clock()
    game = Maenneltest()
    add_players(game)

    while True:
        advance_game(game, clock)


def add_players(game):
    game.add_player(PLAYER_LEFT)
    game.add_player(PLAYER_RIGHT)


def advance_game(game, clock):
    close_game_if_quit()
    fps = get_fps_from_clock_tick(MAX_FPS, clock)
    delta_time = MAX_FPS / fps  # Instead of "step_time"
    compute_player_inputs(game, delta_time)
    redraw_game_screen(game)


def close_game_if_quit():
    if any(event.type == pygame.QUIT for event in pygame.event.get()):
        quit_pygame_and_exit()


def compute_player_inputs(game, delta_time):
    pressed = pygame.key.get_pressed()
    for mapping in KEY_MAPPINGS:
        move_player_from_input(pressed, mapping['keys'], game, mapping['player'], delta_time)


def move_player_from_input(pressed, directions, game, player, delta_time):
    for key, (dx, dy) in directions.items():
        if pressed[key]:
            game.move_player(player, delta_time, dx, dy)


if __name__ == '__main__':
    main()
