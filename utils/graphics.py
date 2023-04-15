import pygame

from utils.global_values import WIDTH, HEIGHT

BACKGROUND_COLOR = (200, 200, 200)
BLACK = (0, 0, 0)
pygame.font.init()
font_normal = pygame.font.SysFont("courier", 18, bold=False)
font_bold = pygame.font.SysFont("courier", 18, bold=True)
# win = pygame.display.set_mode((WIDTH, HEIGHT))
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED, vsync=1)
pygame.display.set_caption("Männeltest ihr Gusten")
surfaces = dict()


def redraw_login_menu(host, name, menu_state):
    win.fill(BACKGROUND_COLOR)

    message = 'Hostname oder IP (leer = localhost): {host}'.format(host=host)
    if menu_state == 'ENTER_HOST':
        host = font_bold.render(message, True, BLACK)
    else:
        host = font_normal.render(message, True, BLACK)

    message = 'Name eingeben: {name}'.format(name=name)
    if menu_state == 'ENTER_NAME':
        name = font_bold.render(message, True, BLACK)
    else:
        name = font_normal.render(message, True, BLACK)

    win.blit(host, (30, 250))
    win.blit(name, (30, 280))

    if menu_state == 'CONNECTING':
        conn_text = font_bold.render('Verbinde...', True, BLACK)
        win.blit(conn_text, (100, 400))

    if menu_state == 'ERROR':
        error_text = font_bold.render('Fehler beim Verbinden!', True, BLACK)
        win.blit(error_text, (100, 450))
    if menu_state == 'NAME_TAKEN':
        error_text = font_bold.render('Name schon vergeben!', True, BLACK)
        win.blit(error_text, (100, 450))

    pygame.display.update()


def redraw_game_screen(game):
    win.fill(BACKGROUND_COLOR)

    # Remove players who left
    players_left = []
    for surface_name in surfaces.keys():
        found = False
        for player_name, _ in game.players.items():
            if surface_name == player_name:
                found = True
        if not found:
            players_left.append(surface_name)
    for player in players_left:
        del surfaces[player]

    for nickname, player in game.players.items():
        # Add new players who joined
        if nickname not in surfaces.keys():
            surfaces[nickname] = pygame.Surface((player.size, player.size))
            surfaces[nickname].fill(BLACK)
        rect = surfaces[nickname].get_rect()
        x = int(round(player.pos_x))
        y = int(round(player.pos_y))
        rect.x = x
        rect.y = y

        # pygame.draw.rect(win, player.color, (x, y, player.size, player.size), 0)
        win.blit(surfaces[nickname], rect)

        name = font_bold.render(nickname, True, player.color)
        win.blit(name, (x + player.size // 2 - name.get_width() // 2, y - 20))

    pygame.display.update()
