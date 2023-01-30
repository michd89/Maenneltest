import datetime
import json
import socket

import pygame

from utils.client_server import MaenneltestClientServer
from utils.maenneltest import Maenneltest
from utils.game import MAX_FPS, get_fps_from_clock_tick
from utils.network import recv_msg, send_msg, send_game, UPDATE_TIMEDELTA, PORT, datetime_to_str, str_to_datetime, \
    PING_TIMEDELTA


def run_server():
    host = '0.0.0.0'

    game = Maenneltest()
    clock = pygame.time.Clock()
    server_time = datetime.datetime.now()
    last_send = server_time
    last_ping = server_time

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind((host, PORT))
    print('Server listening at {host}:{port} ...'.format(host=host, port=PORT))

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
                        if MaenneltestClientServer.get_client_by_address(client_addr):
                            # Don't add duplicate player inputs to the game_msgs list
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
                new_player = game.add_player(nickname)
                if new_player:
                    print('{nickname} joined game'.format(nickname=nickname))
                    # Client uses this for initial time synchronization
                    send_msg(server_sock, address, 'OK ' + datetime_to_str(server_time))
                    MaenneltestClientServer.add_player(address, nickname, new_player)
                    send_game(server_sock, address, game)
                    # TODO: Das müssen später dann auch die anderen Spieler mitkriegen
                else:
                    print('{nickname} already exsists'.format(nickname=nickname))
                    send_msg(server_sock, address, 'NOPE')
            elif message.startswith('PONG'):
                ping_server_time = str_to_datetime(message.split()[1])
                client = MaenneltestClientServer.get_client_by_name(nickname)
                if ping_server_time == client.ping_time:
                    client.ping = round((server_time - ping_server_time).total_seconds() * 1000)

            elif message.startswith('QUIT'):
                nickname = message.split(' ', 1)[1]
                print('{nickname} left the game'.format(nickname=nickname))
                if game.delete_player(nickname):
                    MaenneltestClientServer.remove_player(nickname)

        # Sort client input by time stamp
        # Just in case the messages didn't come in order
        # Will become even more important when player interaction is included
        game_msgs = sorted(game_msgs, key=lambda d: d[1])

        # Simulate movements based on inputs and server FPS
        # print(len(game_msgs))
        for game_msg in game_msgs:
            # TODO: Gibt es nur MOVE?
            _, time_stamp, nickname, step_time, x, y = game_msg
            time_stamp = str_to_datetime(time_stamp)
            # Just in case that older client messages arrived later
            client = MaenneltestClientServer.get_client_by_name(nickname)
            if not client.last_time_stamp or time_stamp > client.last_time_stamp:
                game.move_player(nickname, step_time, x, y)
                client.last_time_stamp = time_stamp

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
            for client in MaenneltestClientServer.clients:
                # TODO: Probably use bytearray for better network performance?

                # There is no last time stamp if the client didn't send any inputs yet
                if client.last_time_stamp:
                    latency = datetime.timedelta(milliseconds=round(client.ping/2))
                    server_time_string = datetime_to_str(server_time + latency)
                    last_time_stamp_string = datetime_to_str(client.last_time_stamp)
                    game_msg = ['GAME', server_time_string, last_time_stamp_string, poses]
                    msg = json.dumps(game_msg)
                    send_msg(server_sock, client.address, msg)
            last_send = server_time

        # Ping
        if server_time - last_ping >= PING_TIMEDELTA:
            for client in MaenneltestClientServer.clients:
                server_time_string = datetime_to_str(server_time)
                msg = 'PING ' + server_time_string
                send_msg(server_sock, client.address, msg)
                client.ping_time = server_time
                last_ping = server_time

            # Test print
            for client in MaenneltestClientServer.clients:
                print('{nickname} {ping}'.format(nickname=client.nickname, ping=str(client.ping)))


if __name__ == '__main__':
    run_server()
