import datetime
import socket

from utils.client_server import MaenneltestClientServer
from utils.maenneltest import Maenneltest


class MaenneltestServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.game = Maenneltest()
        self.server_sock = None
        self.server_time = datetime.datetime.now()
        self.last_send = self.server_time
        self.last_ping = self.server_time
        self.clients = []

    def start_serving(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_sock.bind((self.host, self.port))
        print('Server listening at {host}:{port} ...'.format(host=self.host, port=self.port))

    def get_client_by_name(self, nickname):
        for client in self.clients:
            if client.nickname == nickname:
                return client
        return None

    def get_client_by_address(self, address):
        for client in self.clients:
            if client.address == address:
                return client
        return None

    def add_player(self, address, nickname):
        new_player = self.game.add_player(nickname)
        if new_player:
            self.clients.append(MaenneltestClientServer(address, nickname, new_player))
            return True
        else:
            return False

    def remove_player(self, nickname):
        if self.game.delete_player(nickname):
            self.clients.remove(self.get_client_by_name(nickname))
            return True
        else:
            return False


