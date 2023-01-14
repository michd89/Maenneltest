import datetime
import json
import socket

from utils.network import PORT, send_msg, recv_msg, str_to_datetime, UPDATE_TIMEDELTA, datetime_to_str


class MaenneltestLocal:
    def __init__(self):
        self.client_sock = None
        self.host = ''
        self.port = PORT
        self.nickname = ''
        self.client_time = None
        self.last_send = None
        self.latest_processed_state = None
        self.unprocessed_commands = []
        self.game = None

    def send_msg(self, msg, blocking=False):
        send_msg(self.client_sock, (self.host, PORT), msg, blocking)

    def join_game(self, host, nickname):
        try:
            addr = (host, self.port)
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_sock.connect(addr)
            self.nickname = nickname
            self.host = host
            self.send_msg('JOIN ' + nickname)
            msg, addr = recv_msg(self.client_sock, blocking=True)
            print('Response from server: {addr} {msg}'.format(addr=addr, msg=msg))
            if msg.startswith('OK'):
                client_time = msg.split()[1]
                self.client_time = str_to_datetime(client_time)
                self.last_send = self.client_time
                return 'OK'

            if msg == 'NOPE':
                return 'NOPE'
        except:
            return None

    def quit(self):
        self.send_msg('QUIT ' + self.nickname)

    def prepare_input(self, fps, step_time, acc_x, acc_y):
        self.client_time = self.client_time + datetime.timedelta(milliseconds=1000 / fps)
        client_time_string = datetime_to_str(self.client_time)

        # Handle gameplay related pressed keys
        self.unprocessed_commands.append(['MOVE', client_time_string, self.nickname, step_time, acc_x, acc_y])
        # Sort for the case the server set the local time backwards
        self.unprocessed_commands = sorted(self.unprocessed_commands, key=lambda d: d[1])

    # Send client inputs to server
    def send_input(self):
        if self.client_time - self.last_send >= UPDATE_TIMEDELTA:
            msg = json.dumps(self.unprocessed_commands)
            self.send_msg(msg)
            self.last_send = self.client_time

    # Receive and compute messages from server
    def handle_msgs(self):
        # Receive messages from server
        command_data = []
        game_data = []
        while True:
            try:
                server_msg, _ = recv_msg(self.client_sock)
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
                msg = 'PONG {pst} {nickname}'.format(pst=ping_server_time, nickname=self.nickname)
                self.send_msg(msg)

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
                    if playername == self.nickname:
                        self.latest_processed_state = (pos[0], pos[1])

            self.client_time = str_to_datetime(server_time)
            # Keep leftover unprocesed commands only
            self.unprocessed_commands = [cmd for cmd in self.unprocessed_commands if cmd[1] > last_time_stamp]

    def recalculate_unprocessed(self):
        # Recalculate all remaining unprocessed inputs
        # Start with state of last processed input
        self.game.players[self.nickname].pos_x = self.latest_processed_state[0]
        self.game.players[self.nickname].pos_y = self.latest_processed_state[1]
        for game_msg in self.unprocessed_commands:
            _, _, _, cmd_step_time, x, y = game_msg
            self.game.move_player(self.nickname, cmd_step_time, x, y)

    def do_step(self):
        # Send client inputs to server
        self.send_input()

        # Receive and compute messages from server
        self.handle_msgs()

        # Recalculate all remaining unprocessed inputs
        self.recalculate_unprocessed()
