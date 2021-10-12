import sys
import traceback

import pygame

from utils import connect_to_server, send


# TODO: Find solution for handling special characters and keys when executed as exe
# exe seems to use encoding for english keyboard layout
def handle_line_typing(event, text_in, max_len=None):
    allowed_symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-. '
    text_out = text_in
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_BACKSPACE]:
        text_out = text_out[:-1]
    else:
        try:
            ch = chr(event.key)
        except:
            ch = ''
        if pressed[pygame.K_RSHIFT] or pressed[pygame.K_LSHIFT]:
            ch = ch.upper()
        if pressed[pygame.K_KP_ENTER] or pressed[pygame.K_RETURN]:
            text_out += '\r'
        if not max_len or len(text_out) < max_len:
            if ch in allowed_symbols:
                text_out = text_out + ch
            if ch == '/':  # Catch '-' button input when executed as exe
                text_out = text_out + '-'
    return text_out


def main():
    client = None

    # Test data
    host = 'localhost'
    entered_host = True
    nickname = 'test'
    entered_name = True

    # Actual initial data
    # host = ''
    # entered_host = False
    # nickname = ''
    # entered_name = False

    logged_in = False
    game = None  # For suppressing warning
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)

        if entered_host and entered_name and not logged_in:
            client = connect_to_server(host, nickname)
            logged_in = True
            if client == 'NOPE':
                # Fehlermeldung etc.
                print('NOPE')
                pygame.quit()
                break
            if not client:
                # Fehlermeldung etc.
                print('No client')
                pygame.quit()
                break

        # Get current game state before handling user input
        if logged_in:
            try:
                game = send(client, 'get')
            except Exception as e:
                print("Couldn't get game")
                print(e)
                break

        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            # etc.

        # Graphics
        if run:
            # ...
            pass


def my_except_hook(exctype, value, tb):
    with open('exception.txt', 'w+') as file:
        for line in traceback.format_exception(exctype, value, tb):
            file.write(line)
    sys.__excepthook__(exctype, value, traceback)


if __name__ == '__main__':
    sys.excepthook = my_except_hook
    main()
