class Player:
    def __init__(self, nickname, pos_x, pos_y):
        self.nickname = nickname
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.speed = 3
        self.size = 50

    # TODO: Collision check
    def move(self, x, y, win_width, win_height):
        if x == '+':  # right
            self.pos_x += self.speed
        elif x == '-':  # left
            self.pos_x -= self.speed
        if y == '+':  # down
            self.pos_y += self.speed
        if y == '-':  # up
            self.pos_y -= self.speed


class Maenneltest:
    def __init__(self):
        self.ready = False
        self.players = dict()
        self.win_width = None
        self.win_height = None

    def move_player(self, nickname, x, y):
        player = self.players.get(nickname)
        if player:
            player.move(x, y, self.win_width, self.win_height)

    def add_player(self, nickname):
        if self.players.get(nickname):
            return False
        # TODO: Randomized or fixed point?
        x = 42
        y = 42
        self.players['nickname'] = Player(nickname, x, y)
        return True

    def delete_player(self, nickname):
        if self.players.pop(nickname):
            return True
        else:
            return False

    def new_game(self, win_width, win_height):
        self.win_width = win_width
        self.win_height = win_height
