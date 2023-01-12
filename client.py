import datetime
import json
import socket
import sys
import traceback

import pygame

from utils.graphics import redraw_game_screen, redraw_login_menu
from utils.game import MAX_FPS, get_fps_from_clock_tick, handle_line_typing, get_move, load_sounds, \
    quit_pygame_and_exit
from utils.network import join_game, UPDATE_TIMEDELTA, send_msg, recv_msg, recv_game, PORT, str_to_datetime, \
    datetime_to_str


def main():
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
                quit_pygame_and_exit()
            elif response == 'NOPE':
                print('NOPE')
                quit_pygame_and_exit()
            # TODO: Nur diese Fälle?
            else:  # OK
                client_sock, client_time = response
                client_time = str_to_datetime(client_time)
                last_send = client_time
                game = recv_game(client_sock)
                latest_processed_state = (game.players[nickname].pos_x, game.players[nickname].pos_y)
                logged_in = True

        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_msg(client_sock, (host, PORT), 'QUIT ' + nickname)
                quit_pygame_and_exit()

            # Handle typing (single keydowns)
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
            # Handle typing (single keydowns) of single sound (or exiting)
            else:
                if event.type == pygame.KEYDOWN:
                    pressed = pygame.key.get_pressed()
                    if pressed[pygame.K_RETURN]:
                        if not enter_pressed:
                            send_msg(client_sock, (host, PORT), 'QUIT ' + nickname)
                            quit_pygame_and_exit()
                            # pygame.mixer.Sound.play(test_sound)
                            enter_pressed = True
                if event.type == pygame.KEYUP:
                    pressed = pygame.key.get_pressed()
                    if not pressed[pygame.K_RETURN]:
                        enter_pressed = False

        # Handle pressed keys (constant pressing of keys)
        if logged_in:
            pressed = pygame.key.get_pressed()
            acc_x, acc_y = get_move(pressed)

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
                    server_msg, _ = recv_msg(client_sock)
                    try:
                        server_msg = json.loads(server_msg)
                        if server_msg[0] == 'GAME':
                            game_data.append(server_msg)
                    # TODO: Improve implementation of this
                    except json.decoder.JSONDecodeError:
                        if server_msg.startswith('PING'):
                            command_data.append(server_msg)
                except socket.error:
                    # TODO: Differentiate between "nothing received" and an "actual error"
                    break

            # Compute command messages
            for command_msg in command_data:
                if command_msg.startswith('PING'):
                    ping_server_time = command_msg.split()[1]
                    msg = 'PONG {pst} {nickname}'.format(pst=ping_server_time, nickname=nickname)
                    send_msg(client_sock, (host, PORT), msg)

            # Compute game related messages
            if game_data:
                # Sort by server time just in case the messages didn't come in order
                game_data = sorted(game_data, key=lambda d: d[1])
                for game_msg in game_data:
                    # TODO
                    # if game_msg[0] == 'GAME':  # Später
                    _, server_time, last_time_stamp, poses = game_msg

                    # Insert player state (note: Still Client Side Prediction only)
                    for playername, pos in poses.items():
                        if playername == nickname:
                            latest_processed_state = (pos[0], pos[1])

                client_time = str_to_datetime(server_time)
                # Keep leftover unprocesed commands only
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
