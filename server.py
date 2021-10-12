import socket
import threading

from utils import recv_msg, send_msg, send_game


# Sub thread: Handles messages from certain client
def handling_client_thread_function(client):
    nickname = recv_msg(client)
    print('{nickname} ist dem Spiel beigetreten'.format(nickname=nickname))
    send_msg(client, 'OK')

    while True:
        try:
            message = recv_msg(client)

            if not message:  # Player left game
                break

            # compute message

            # Send game or msg
        except Exception as exc:
            # Remove and close client
            client.close()
            print('{nickname} hat das Spiel verlassen (exc)'.format(nickname=nickname))
            print(exc)
            break
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
