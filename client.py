import datetime
import json
import socket
import sys
import traceback

import pygame

from utils.graphics import redraw_game_screen, redraw_login_menu
from utils.game import MAX_FPS, get_fps_from_clock_tick, handle_line_typing, get_move, load_sounds
from utils.network import join_game, UPDATE_TIMEDELTA, send_msg, recv_msg, recv_game, PORT, str_to_datetime, \
    datetime_to_str


def main():
    # TODO WICHTIG: https://stackoverflow.com/a/18513365
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()

    client_sock = None
    host = ''
    entered_host = False
    nickname = ''
    entered_name = False
    logged_in = False
    client_time = None
    last_send = None
    latest_processed_state = None
    unprocessed_commands = []
    game = None
    run = True
    enter_pressed = False
    clock = pygame.time.Clock()
    # test_sound = load_sounds()

    while run:
        fps = get_fps_from_clock_tick(MAX_FPS, clock)
        step_time = MAX_FPS / fps

        # User entered data, program tries to log in
        if entered_host and entered_name and not logged_in:
            response = join_game((host, PORT), nickname)
            if not response:
                print('No client')
                pygame.quit()
                break
            elif response == 'NOPE':
                print('NOPE')
                pygame.quit()
                break
            else:  # OK
                client_sock, client_time = response
                client_time = str_to_datetime(client_time)
                last_send = client_time
                game = recv_game(client_sock)
                latest_processed_state = (game.players[nickname].pos_x, game.players[nickname].pos_y)
                logged_in = True

        # Handle user input
        # Handle typing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False

            # TODO: Kann man an dieser Stelle noch rumtippen, während der Client versucht, beizutreten?
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
                                nickname = 'Anonym'
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

            # Just advance client time here instead of catching special cases
            # TODO: See what happens here. Doesn't occour every time
            client_time = client_time + datetime.timedelta(milliseconds=1000/fps)
            client_time_string = datetime_to_str(client_time)

            # Handle gameplay related pressed keys
            unprocessed_commands.append(['MOVE', client_time_string, nickname, step_time, acc_x, acc_y])
            # Sort for the case the server set the local time backwards
            unprocessed_commands = sorted(unprocessed_commands, key=lambda d: d[1])

            # Send client inputs to server
            if client_time - last_send >= UPDATE_TIMEDELTA:
                msg = json.dumps(unprocessed_commands)
                send_msg(client_sock, (host, PORT), msg)
                last_send = client_time

            # Receive messages from server
            command_data = []
            game_data = []
            while True:
                try:
                    # Use game state with latest time stamp (if more than one is received)
                    server_msg, _ = recv_msg(client_sock)
                    try:
                        server_msg = json.loads(server_msg)
                        if server_msg[0] == 'GAME':
                            game_data.append(server_msg)
                    # TODO: Improve implementation of this
                    except json.decoder.JSONDecodeError:
                        pass
                    # if server_msg.startswith('PING'):
                    #     command_data.append(server_msg)
                except socket.error:
                    # TODO: Differentiate between "nothing received" and an "actual error"
                    break

            # Compute command messages
            for command_msg in command_data:
                pass

            # Compute game related messages
            if game_data:
                # Sort by server time just in case the messages didn't come in order
                game_data = sorted(game_data, key=lambda d: d[1])
                # for game_msg in game_data:  # Später
                # if game_msg[0] == 'GAME':  # Später
                game_msg = game_data[-1]  # Latest processed input
                _, server_time, last_time_stamp, poses = game_msg
                client_time = str_to_datetime(server_time)

                # Insert player state (note: Still Client Side Prediction only)
                for playername, pos in poses.items():
                    if playername == nickname:
                        latest_processed_state = (pos[0], pos[1])

                # Discard processed commands
                unprocessed_commands = [cmd for cmd in unprocessed_commands if cmd[1] > last_time_stamp]

            # Recalculate all remaining unprocessed inputs
            # Start with state of last processed input
            game.players[nickname].pos_x = latest_processed_state[0]
            game.players[nickname].pos_y = latest_processed_state[1]
            for game_msg in unprocessed_commands:
                _, _, _, cmd_step_time, x, y = game_msg
                game.move_player(nickname, cmd_step_time, x, y)

        # Graphics
        if run:
            if not logged_in:
                redraw_login_menu(host, nickname, entered_host, entered_name)
            else:
                redraw_game_screen(game)


def my_except_hook(exctype, value, tb):
    with open('exception.txt', 'w+') as file:
        for line in traceback.format_exception(exctype, value, tb):
            file.write(line)
    sys.__excepthook__(exctype, value, traceback)


if __name__ == '__main__':
    sys.excepthook = my_except_hook
    main()
