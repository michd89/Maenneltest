import pygame

WIDTH = 900
HEIGHT = 900
BACKGROUND_COLOR = (200, 200, 200)
pygame.font.init()
font_normal = pygame.font.SysFont("courier", 18, bold=True)
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Männeltest ihr Gusten")


def redraw_login_menu(host, nickname, entered_host, entered_name):
    pass


def redraw_game_screen(game):
    win.fill(BACKGROUND_COLOR)

    for nickname, player in game.players.items():
        pygame.draw.rect(win, player.color, (player.pos_x, player.pos_y, player.size, player.size), 0)
        name = font_normal.render(nickname, True, player.color)
        win.blit(name, (player.pos_x + player.size // 2 - name.get_width() // 2, player.pos_y - 18))

    pygame.display.update()
