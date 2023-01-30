import sys
import traceback

import pygame

from utils.client_local import MaenneltestClientLocal
from utils.graphics import redraw_game_screen, redraw_login_menu
from utils.game import MAX_FPS, get_fps_from_clock_tick, get_move, quit_pygame_and_exit, \
    handle_input_enter_host, handle_input_enter_name


def main():
    pygame.init()
    # test_sound = load_sounds()

    host = ''
    nickname = ''
    menu_state = 'ENTER_HOST'  # ENTER_HOST, ENTER_NAME, CONNECTING, ERROR, NAME_TAKEN, INGAME
    acc_x = 0
    acc_y = 0
    clock = pygame.time.Clock()
    client = MaenneltestClientLocal()

    while True:
        fps = get_fps_from_clock_tick(MAX_FPS, clock)
        step_time = MAX_FPS / fps

        # User entered data, program tries to log in
        if menu_state == 'CONNECTING':
            menu_state = client.try_connect(host, nickname)

        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Closing the window
                if menu_state == 'INGAME':
                    client.quit()
                quit_pygame_and_exit()
            if menu_state == 'ENTER_HOST':
                menu_state, host = handle_input_enter_host(event, host)
            elif menu_state == 'ENTER_NAME':
                menu_state, nickname = handle_input_enter_name(event, nickname)
            elif menu_state == 'INGAME':
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_RETURN]:
                    client.quit()
                    quit_pygame_and_exit()
                acc_x, acc_y = get_move(pressed)

        # Let the actual game run
        if menu_state == 'INGAME':
            # Prepare data of current time step for the server
            client.prepare_input(fps, step_time, acc_x, acc_y)

            # Send current time step and handle response
            client.do_step()

        # Sounds
        # if play_sound:
        #     pygame.mixer.Sound.play(test_sound)

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
