class MaenneltestClientServer:
    def __init__(self, address, nickname, player):
        self.address = address
        self.nickname = nickname
        self.player = player
        self.ping = 0
        self.ping_time = None
        self.last_time_stamp = None

    @classmethod
    def get_client_by_name(cls, clients, nickname):
        for client in clients:
            if client.nickname == nickname:
                return client
        return None

    @classmethod
    def get_client_by_address(cls, clients, address):
        for client in clients:
            if client.address == address:
                return client
        return None

    def add_player(self):
        pass

    def remove_player(self):
        pass
