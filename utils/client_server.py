# TODO: Sollte das nicht eher eine Unterklasse vom Player werden?
class MaenneltestClientServer:
    def __init__(self, address, nickname, player):
        self.address = address
        self.nickname = nickname  # TODO: Ist der hier nicht redundant?
        self.player = player
        self.ping = 0
        self.ping_time = None
        self.last_time_stamp = None

