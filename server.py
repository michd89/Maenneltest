import datetime
import json
import socket

import pygame

from maenneltest import Maenneltest
from utils.game import MAX_FPS, get_fps_from_clock_tick
from utils.network import recv_msg, send_msg, send_game, UPDATE_TIMEDELTA, PORT, datetime_to_str, str_to_datetime


def run_server():
    host = '0.0.0.0'

    game = Maenneltest()
    clock = pygame.time.Clock()
    server_time = datetime.datetime.now()
    last_send = server_time
    clients = dict()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind((host, PORT))
    print('Server listening at {host}:{port} ...'.format(host=host, port=PORT))

    last_time_stamp = dict()

    # main loop
    while True:
        get_fps_from_clock_tick(MAX_FPS, clock)

        server_time = datetime.datetime.now()

        # Load incoming client data into buffers
        command_msgs = []
        game_msgs = []
        while True:
            try:
                client_msg, client_addr = recv_msg(server_sock)
                try:
                    client_msg = json.loads(client_msg)
                # Simple string as command
                # TODO: Improve implementation of this
                except json.decoder.JSONDecodeError:
                    pass

                # A command message is a single command
                # A game message is a list of lists with one or more game inputs ('MOVE' etc.)
                if type(client_msg) is list:
                    for msg in client_msg:
                        # Discard game messages from non-existing client
                        nickname = None
                        for name, address in clients.items():
                            if client_addr == address:
                                nickname = name
                                break
                        if nickname:
                            # Pairs of timestamp and player name must be unique
                            # Which means: Don't add duplicate player inputs to the game_msgs list
                            # because the client will repeatedly send unprocessed commands
                            new_time_and_name = (msg[1], msg[2])
                            times_and_names = []
                            for game_msg in game_msgs:
                                times_and_names.append((game_msg[1], game_msg[2]))
                            if new_time_and_name not in times_and_names:
                                game_msgs.append(msg)
                else:  # Single string with command input ('JOIN', 'PING' etc.)
                    # These commands are only bidirectional. Response won't be broadcasted, so save client_addr
                    command_msgs.append((client_msg, client_addr))
            except socket.error:  # Nothing received
                # TODO: Differentiate between "nothing received" and an "actual error"
                break
        # Process client commands (no actual player input)
        for message, address in command_msgs:
            if message.startswith('JOIN'):
                nickname = message.split(' ', 1)[1]
                if game.add_player(nickname):
                    print('{nickname} joined game'.format(nickname=nickname))
                    # Client uses this for initial time synchronization
                    send_msg(server_sock, address, 'OK ' + datetime_to_str(server_time))
                    clients[nickname] = address
                    send_game(server_sock, address, game)
                    # TODO: Das müssen später dann auch die anderen Spieler mitkriegen
                else:
                    print('{nickname} already exsists'.format(nickname=nickname))
                    send_msg(server_sock, address, 'NOPE')

        # Sort client input by time stamp
        # Just in case the messages didn't come in order
        # Will become even more important when player interaction is included
        game_msgs = sorted(game_msgs, key=lambda d: d[1])
        # last_time_stamp = dict()  # Lag das Problem an dieser Stelle oder woanders? Ist es gelöst?

        # Simulate movements based on inputs and server FPS
        for game_msg in game_msgs:
            _, time_stamp, nickname, step_time, x, y = game_msg
            time_stamp = str_to_datetime(time_stamp)
            # Just in case that older client messages arrived later
            if nickname not in last_time_stamp.keys() or time_stamp > last_time_stamp[nickname]:
                game.move_player(nickname, step_time, x, y)
                last_time_stamp[nickname] = time_stamp

        # Broadcast game state to clients every 100 ms
        # That's by now only Client Side Prediction, NOT Interpolation with other clients!
        if server_time - last_send >= UPDATE_TIMEDELTA:
            # Collect game state
            # By now every client only needs his own state
            # but we will already try and consider a multiple client environment
            poses = dict()
            for nickname, player in game.players.items():
                poses[nickname] = [player.pos_x, player.pos_y]

            # Send game state and individual last acknowledged time stamp to every client
            for nickname, address in clients.items():
                # TODO: Probably use bytearray for better network performance?

                # TODO: (server_time + Latenz) als Zeitstempel mitgeben
                # There is no last time stamp if the client didn't send any inputs yet
                if nickname in last_time_stamp.keys():
                    server_time_string = datetime_to_str(server_time)
                    last_time_stamp_string = datetime_to_str(last_time_stamp[nickname])
                    game_msg = ['GAME', server_time_string, last_time_stamp_string, poses]
                    msg = json.dumps(game_msg)
                    send_msg(server_sock, address, msg)
            last_send = server_time

        # TODO: Ping implementieren
        # Einmal je zwei (drei, ...?) Sekunden PING schicken
        # Clients schicken PONG zurück
        # Speichern und den Clients zum Anzeigen mitgeben
        # Vielleicht oben beim Broadcast mit


if __name__ == '__main__':
    run_server()
