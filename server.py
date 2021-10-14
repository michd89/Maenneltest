import socket
import threading

from maenneltest import Maenneltest
from utils import recv_msg, send_msg, send_game

game = Maenneltest()


# Sub thread: Handles messages from certain client
def handling_client_thread_function(client):
    nickname = recv_msg(client)
    if game.add_player(nickname):
        print('{nickname} ist dem Spiel beigetreten'.format(nickname=nickname))
        send_msg(client, 'OK')
    else:
        print('{nickname} gibts schon'.format(nickname=nickname))
        send_msg(client, 'NOPE')
        client.close()
        return

    while True:
        try:
            message = recv_msg(client)

            if not message:  # Player left game
                break

            if message.startswith('get'):
                send_game(client, game)
            if message.startswith('move'):
                msg_list = message.split()
                acc_y = msg_list.pop()
                acc_x = msg_list.pop()
                _ = msg_list.pop(0)  # 'move'
                nickname = ' '.join(msg_list)
                game.move_player(nickname, acc_x, acc_y)

        except Exception as exc:
            # Remove and close client
            client.close()
            game.delete_player(nickname)
            print('{nickname} hat das Spiel verlassen (exc)'.format(nickname=nickname))
            print(exc)
            break
    game.delete_player(nickname)
    print('{nickname} hat das Spiel verlassen (normal)'.format(nickname=nickname))


# Main thread: Receiving / Listening function
def receive():
    host = '0.0.0.0'
    port = 50000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print('Server horcht auf {host}:{port} ...'.format(host=host, port=port))

    while True:
        # Accept connection
        client, address = server.accept()
        print("Verbunden mit {}".format(str(address)))

        # Start handling thread for client
        thread = threading.Thread(target=handling_client_thread_function, args=([client]))
        thread.start()


if __name__ == '__main__':
    receive()
