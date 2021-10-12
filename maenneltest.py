from random import randint


class Player:
    def __init__(self, nickname, pos_x, pos_y):
        self.nickname = nickname
        self.color = (0, 0, 0)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.speed = 3
        self.size = 50

    def move(self, acc_x, acc_y, win_width, win_height):
        if acc_x == '+':  # right
            self.pos_x += self.speed
            if self.pos_x + self.size > win_width:
                self.pos_x = win_width - self.size
        elif acc_x == '-':  # left
            self.pos_x -= self.speed
            if self.pos_x < 0:
                self.pos_x = 0
        if acc_y == '+':  # down
            self.pos_y += self.speed
            if self.pos_y + self.size > win_height:
                self.pos_y = win_height - self.size
        if acc_y == '-':  # up
            self.pos_y -= self.speed
            if self.pos_y < 0:
                self.pos_y = 0


class Maenneltest:
    def __init__(self):
        self.ready = False
        self.players = dict()
        # Hard code it here for simplicity
        self.win_width = 900
        self.win_height = 900

    def move_player(self, nickname, acc_x, acc_y):
        player = self.players.get(nickname)
        if player:
            player.move(acc_x, acc_y, self.win_width, self.win_height)

    def add_player(self, nickname):
        if self.players.get(nickname):
            return False
        # TODO: Randomized or fixed point?
        x = randint(10, self.win_width - 50)
        y = randint(10, self.win_height - 50)
        self.players[nickname] = Player(nickname, x, y)
        return True

    def delete_player(self, nickname):
        if self.players.pop(nickname):
            return True
        else:
            return False
