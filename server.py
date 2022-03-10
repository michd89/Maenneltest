import socket

from maenneltest import Maenneltest
from utils import recv_msg, send_msg, send_game


def run_server():
    host = '0.0.0.0'
    port = 50000

    game = Maenneltest()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind((host, port))
    print('Server horcht auf {host}:{port} ...'.format(host=host, port=port))

    # Process incoming packages
    while True:
        try:
            message, addr = recv_msg(server_sock)

            if message.startswith('JOIN'):
                nickname = message.split(' ', 1)[1]
                if game.add_player(nickname):
                    print('{nickname} ist dem Spiel beigetreten'.format(nickname=nickname))
                    send_msg(server_sock, addr, 'OK')
                else:
                    print('{nickname} gibts schon'.format(nickname=nickname))
                    send_msg(server_sock, addr, 'NOPE')
            elif message.startswith('GET'):
                send_game(server_sock, addr, game)
            elif message.startswith('MOVE'):
                msg_list = message.split()
                acc_y = msg_list.pop()
                acc_x = msg_list.pop()
                msg_list.pop(0)  # 'move'
                nickname = ' '.join(msg_list)
                game.move_player(nickname, acc_x, acc_y)
        except socket.error:  # Nothing received
            pass


if __name__ == '__main__':
    run_server()
