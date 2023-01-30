class MaenneltestClientServer:
    clients = []

    def __init__(self, address, nickname, player):
        self.address = address
        self.nickname = nickname
        self.player = player
        self.ping = 0
        self.ping_time = None
        self.last_time_stamp = None

    @classmethod
    def get_client_by_name(cls, nickname):
        for client in cls.clients:
            if client.nickname == nickname:
                return client
        return None

    @classmethod
    def get_client_by_address(cls, address):
        for client in cls.clients:
            if client.address == address:
                return client
        return None

    @classmethod
    def add_player(cls, address, nickname, new_player):
        cls.clients.append(MaenneltestClientServer(address, nickname, new_player))

    @classmethod
    def remove_player(cls, nickname):
        cls.clients.remove(cls.get_client_by_name(nickname))
