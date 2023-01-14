import sys
import traceback

import pygame

from utils.client_local import MaenneltestLocal
from utils.graphics import redraw_game_screen, redraw_login_menu
from utils.game import MAX_FPS, get_fps_from_clock_tick, handle_line_typing, get_move, quit_pygame_and_exit
from utils.network import send_msg, recv_game, PORT


def main():
    pygame.init()
    # test_sound = load_sounds()

    host = ''
    nickname = ''
    menu_state = 'ENTER_HOST'  # ENTER_HOST, ENTER_NAME, CONNECTING, ERROR, NAME_TAKEN, INGAME
    enter_pressed = False
    clock = pygame.time.Clock()
    client = MaenneltestLocal()

    while True:
        fps = get_fps_from_clock_tick(MAX_FPS, clock)
        step_time = MAX_FPS / fps

        # User entered data, program tries to log in
        if menu_state == 'CONNECTING':
            response = client.join_game(host, nickname)
            if not response:
                print('No client')
                menu_state = 'ERROR'
            elif response == 'NOPE':
                print('NOPE')
                menu_state = 'NAME_TAKEN'
            elif response == 'OK':
                client.game = recv_game(client.client_sock)
                client.latest_processed_state = (client.game.players[client.nickname].pos_x, client.game.players[client.nickname].pos_y)
                menu_state = 'INGAME'

        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_msg(client.client_sock, (host, PORT), 'QUIT ' + client.nickname)
                quit_pygame_and_exit()

            # Handle typing (single keydowns)
            if event.type == pygame.KEYDOWN:
                if menu_state == 'ENTER_HOST' or menu_state == 'ENTER_NAME':
                    if menu_state == 'ENTER_HOST':
                        host = handle_line_typing(event, host)
                        if host[-1:] == '\r':
                            host = host[:-1]
                            menu_state = 'ENTER_NAME'
                            if not host:
                                host = 'localhost'
                            elif host == ' ':
                                host = 'ip'
                    elif menu_state == 'ENTER_NAME':
                        nickname = handle_line_typing(event, nickname, 21)
                        # Confirm entry
                        if len(nickname) <= 21 and nickname[-1:] == '\r':
                            nickname = nickname[:-1]
                            if not nickname:
                                nickname = 'Anonym'
                            menu_state = 'CONNECTING'
                        elif len(nickname) == 21 and nickname[-1:] != '\r':
                            nickname = nickname[:-1]
                else:
                    pressed = pygame.key.get_pressed()
                    if pressed[pygame.K_RETURN]:
                        if not enter_pressed:
                            send_msg(client.client_sock, (host, PORT), 'QUIT ' + client.nickname)
                            quit_pygame_and_exit()
                            # pygame.mixer.Sound.play(test_sound)
                            enter_pressed = True
                if event.type == pygame.KEYUP:
                    pressed = pygame.key.get_pressed()
                    if not pressed[pygame.K_RETURN]:
                        enter_pressed = False

        # Handle pressed keys (constant pressing of keys)
        if menu_state == 'INGAME':
            acc_x, acc_y = get_move(pygame.key.get_pressed())

            # Prepare data of current time step for the server
            client.prepare_input(fps, step_time, acc_x, acc_y)

            # Send current time step and handle response
            client.do_step()

        # Graphics
        if menu_state != 'INGAME':
            redraw_login_menu(host, nickname, menu_state)
        else:
            redraw_game_screen(client.game)

        if menu_state == 'ERROR' or menu_state == 'NAME_TAKEN':
            pygame.time.delay(3000)
            quit_pygame_and_exit()


def my_except_hook(exctype, value, tb):
    with open('exception.txt', 'w+') as file:
        for line in traceback.format_exception(exctype, value, tb):
            file.write(line)
    sys.__excepthook__(exctype, value, traceback)


if __name__ == '__main__':
    sys.excepthook = my_except_hook
    main()
