import os
import sys
import traceback

import pygame

from graphics import redraw_game_screen, redraw_login_menu
from utils import join_game, send


# TODO: Find solution for handling special characters and keys when executed as exe
# exe seems to use encoding for english keyboard layout
def handle_line_typing(event, text_in, max_len=None):
    allowed_symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-. '
    text_out = text_in
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_BACKSPACE]:
        text_out = text_out[:-1]
    else:
        try:
            ch = chr(event.key)
        except:
            ch = ''
        if pressed[pygame.K_RSHIFT] or pressed[pygame.K_LSHIFT]:
            ch = ch.upper()
        if pressed[pygame.K_KP_ENTER] or pressed[pygame.K_RETURN]:
            text_out += '\r'
        if not max_len or len(text_out) < max_len:
            if ch in allowed_symbols:
                text_out = text_out + ch
            if ch == '/':  # Catch '-' button input when executed as exe
                text_out = text_out + '-'
    return text_out


def get_move(pressed):
    acc_x = 0
    acc_y = 0
    if pressed[pygame.K_RIGHT]:
        acc_x += 1
    if pressed[pygame.K_LEFT]:
        acc_x -= 1
    if pressed[pygame.K_UP]:
        acc_y -= 1
    if pressed[pygame.K_DOWN]:
        acc_y += 1

    return acc_x, acc_y


def main():
    # TODO WICHTIG: https://stackoverflow.com/a/18513365
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()

    client_sock = None
    host = ''
    port = 50000
    entered_host = False
    nickname = ''
    entered_name = False
    logged_in = False
    game = None  # For suppressing warning
    run = True
    enter_pressed = False
    get_interval = 6
    game_step = get_interval
    clock = pygame.time.Clock()

    pygame.mixer.set_num_channels(100)
    sounds_dir = 'sounds'
    sound_name = 'arcade-rising.wav'
    # TODO WICHTIG: https://stackoverflow.com/a/41989994
    # Und: https://stackoverflow.com/a/42615559
    if getattr(sys, 'frozen', False):  # exe
        path = sys.executable  # with client.exe as last entry
        path_list = path.split(os.sep)
        if path_list[-1:] != os.sep:  # Since C: is valid as well as C:\
            path_list[0] += os.sep
        path = os.path.join(*path_list[:-2], sounds_dir, sound_name)  # remove "exes" and client.exe
        print(path)
        test_sound = pygame.mixer.Sound(path)
    else:  # py
        test_sound = pygame.mixer.Sound(os.path.join(sounds_dir, sound_name))

    while run:
        clock.tick(60)

        if entered_host and entered_name and not logged_in:
            client_sock = join_game((host, port), nickname)
            logged_in = True
            if client_sock == 'NOPE':
                print('NOPE')
                pygame.quit()
                break
            if not client_sock:
                print('No client')
                pygame.quit()
                break

        # Get current game state before handling user input
        if logged_in:
            try:
                if game_step == get_interval:
                    # Update game state from server
                    game = send(client_sock, (host, port), 'GET')
                    game_step = 1
                else:
                    # Interpolate positions for smoother movement
                    game.update_players()  # Locally
                    game_step += 1
            except Exception as e:
                print("Couldn't get game")
                print(e)
                break

        # Handle user input
        # Handle typing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False

            if not logged_in:
                if event.type == pygame.KEYDOWN:
                    if not entered_host:
                        host = handle_line_typing(event, host)
                        if host[-1:] == '\r':
                            host = host[:-1]
                            entered_host = True
                            if not host:
                                host = 'localhost'
                            elif host == ' ':
                                host = 'ip'
                    elif not entered_name:
                        nickname = handle_line_typing(event, nickname, 21)
                        # Confirm entry
                        if len(nickname) <= 21 and nickname[-1:] == '\r':
                            nickname = nickname[:-1]
                            if not nickname:
                                nickname = 'Namenloser Gust'
                            entered_name = True
                        elif len(nickname) == 21 and nickname[-1:] != '\r':
                            nickname = nickname[:-1]
            else:
                if event.type == pygame.KEYDOWN:
                    pressed = pygame.key.get_pressed()
                    if pressed[pygame.K_RETURN]:
                        if not enter_pressed:
                            pygame.quit()
                            exit()
                            # pygame.mixer.Sound.play(test_sound)
                            enter_pressed = True
                if event.type == pygame.KEYUP:
                    pressed = pygame.key.get_pressed()
                    if not pressed[pygame.K_RETURN]:
                        enter_pressed = False

        # Handle pressed keys
        if logged_in and run:
            pressed = pygame.key.get_pressed()
            acc_x, acc_y = get_move(pressed)
            # Hier noch ein lokales Update der rate-Werte?
            # game.move_player(nickname, acc_x, acc_y)
            # game.update_players()
            if game_step != get_interval:
                game.players[nickname].rate_x = acc_x
                game.players[nickname].rate_y = acc_y

            send(client_sock, (host, port), 'MOVE {} {} {}'.format(nickname, acc_x, acc_y))

        # Graphics
        if run:
            if not logged_in:
                redraw_login_menu(host, nickname, entered_host, entered_name)
            else:
                print(game.players.get(nickname).pos_y)
                redraw_game_screen(game)


def my_except_hook(exctype, value, tb):
    with open('exception.txt', 'w+') as file:
        for line in traceback.format_exception(exctype, value, tb):
            file.write(line)
    sys.__excepthook__(exctype, value, traceback)


if __name__ == '__main__':
    sys.excepthook = my_except_hook
    main()
