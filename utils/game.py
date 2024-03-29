import os
import sys

import pygame

MAX_FPS = 60


def get_fps_from_clock_tick(max_fps, clock):
    clock.tick(max_fps)
    fps = clock.get_fps()
    while fps == 0:  # PyGame clock needs some time for startup
        clock.tick(max_fps)
        fps = clock.get_fps()
    return fps


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
            return True, text_out
        if not max_len or len(text_out) < max_len:
            if ch in allowed_symbols:
                text_out = text_out + ch
            if ch == '/':  # Catch '-' button input when executed as exe
                text_out = text_out + '-'
    return False, text_out


def handle_input_enter_host(event, host):
    menu_state = 'ENTER_HOST'
    if event.type == pygame.KEYDOWN:
        pressed_enter, host = handle_line_typing(event, host)
        if pressed_enter:
            menu_state = 'ENTER_NAME'
            if not host:
                host = 'localhost'
            elif host == ' ':
                host = 'ip'
    return menu_state, host


def handle_input_enter_name(event, nickname):
    menu_state = 'ENTER_NAME'
    if event.type == pygame.KEYDOWN:
        pressed_enter, nickname = handle_line_typing(event, nickname, 20)
        if pressed_enter:
            menu_state = 'CONNECTING'
            if not nickname:
                nickname = 'Anonym'
    return menu_state, nickname


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


def load_sounds():
    # https://stackoverflow.com/a/18513365
    pygame.mixer.pre_init(44100, -16, 1, 512)

    pygame.mixer.set_num_channels(100)
    sounds_dir = 'sounds'
    sound_name = 'arcade-rising.wav'

    # https://stackoverflow.com/a/41989994
    # https://stackoverflow.com/a/42615559
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

    return test_sound


def quit_pygame_and_exit():
    pygame.quit()
    sys.exit()
