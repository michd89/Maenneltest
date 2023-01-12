import pygame

from utils.global_values import WIDTH, HEIGHT

BACKGROUND_COLOR = (200, 200, 200)
BLACK = (0, 0, 0)
pygame.font.init()
font_normal = pygame.font.SysFont("courier", 18, bold=False)
font_bold = pygame.font.SysFont("courier", 18, bold=True)
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Männeltest ihr Gusten")


def redraw_login_menu(host, name, entered_host, entered_name, login_state='OK'):
    win.fill(BACKGROUND_COLOR)

    message = 'Hostname oder IP (leer = localhost): {host}'.format(host=host)
    if not entered_host and not entered_name:
        host = font_bold.render(message, True, BLACK)
    else:
        host = font_normal.render(message, True, BLACK)

    message = 'Name eingeben: {name}'.format(name=name)
    if entered_host and not entered_name:
        name = font_bold.render(message, True, BLACK)
    else:
        name = font_normal.render(message, True, BLACK)

    win.blit(host, (30, 250))
    win.blit(name, (30, 280))

    if entered_host and entered_name:
        fertig = font_bold.render('Verbinde...', True, BLACK)
        win.blit(fertig, (100, 400))

    if login_state == 'ERROR':
        error_text = font_bold.render('Fehler beim Verbinden!', True, BLACK)
        win.blit(error_text, (100, 450))
    if login_state == 'NAME_TAKEN':
        error_text = font_bold.render('Name schon vergeben!', True, BLACK)
        win.blit(error_text, (100, 450))

    pygame.display.update()

    if login_state != 'OK':
        pygame.time.delay(3000)


def redraw_game_screen(game):
    win.fill(BACKGROUND_COLOR)

    for nickname, player in game.players.items():
        pygame.draw.rect(win, player.color, (player.pos_x, player.pos_y, player.size, player.size), 0)
        name = font_bold.render(nickname, True, player.color)
        win.blit(name, (player.pos_x + player.size // 2 - name.get_width() // 2, player.pos_y - 20))

    pygame.display.update()
