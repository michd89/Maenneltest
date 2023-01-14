from random import randint

from utils.global_values import WIDTH, HEIGHT


class Player:
    def __init__(self, nickname, pos_x, pos_y):
        self.nickname = nickname
        self.color = (0, 0, 0)
        self.rate_x = 0
        self.rate_y = 0
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.speed = 3
        self.size = 50

    def move(self, step_time, direction_x, direction_y, win_width, win_height):
        self.rate_x = step_time * direction_x * self.speed
        self.rate_y = step_time * direction_y * self.speed
        self.pos_x += self.rate_x
        self.pos_y += self.rate_y
        if self.rate_x >= 0:  # right
            if self.pos_x + self.size > win_width:
                self.pos_x = win_width - self.size
        else:  # left
            if self.pos_x < 0:
                self.pos_x = 0
        if self.rate_y >= 0:  # down
            if self.pos_y + self.size > win_height:
                self.pos_y = win_height - self.size
        else:  # up
            if self.pos_y < 0:
                self.pos_y = 0


class Maenneltest:
    def __init__(self):
        self.ready = False
        self.players = dict()
        self.win_width = WIDTH
        self.win_height = HEIGHT

    def move_player(self, info, step_time, direction_x, direction_y):
        if isinstance(info, str):
            player = self.players.get(info)
        else:
            player = info
        if player:
            player.move(step_time, direction_x, direction_y, self.win_width, self.win_height)

    # def update_players(self):
    #     for _, player in self.players.items():
    #         self.move_player(player, player.rate_x, player.rate_y)

    def add_player(self, nickname):
        if self.players.get(nickname):
            return False
        x = randint(10, self.win_width - 50)
        y = randint(10, self.win_height - 50)
        self.players[nickname] = Player(nickname, x, y)
        return self.players[nickname]

    def delete_player(self, nickname):
        if self.players.pop(nickname):
            return True
        else:
            return False
