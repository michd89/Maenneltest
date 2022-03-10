import pickle
import socket

ENCODING = 'utf-8'
RECV_SIZE = 4096


def send_msg(sock, addr, msg, blocking=False):
    sock.setblocking(blocking)
    sock.sendto(msg.encode(ENCODING), addr)


def recv_msg(sock, blocking=False):
    try:
        sock.setblocking(blocking)
        msg, addr = sock.recvfrom(RECV_SIZE)
        msg = msg.decode(ENCODING)
        return msg, addr
    except socket.error:  # Nothing received
        raise socket.error


def send_game(sock, addr, game, blocking=False):
    sock.setblocking(blocking)
    sock.sendto(pickle.dumps(game), addr)


def recv_game(sock, blocking=True):
    try:
        sock.setblocking(blocking)
        msg, _ = sock.recvfrom(RECV_SIZE)
        game = pickle.loads(msg)
        return game
    except socket.error:  # Nothing received
        raise socket.error


def join_game(addr, nick):
    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_sock.connect(addr)
        send_msg(client_sock, addr, 'JOIN ' + nick)
        msg, addr = recv_msg(client_sock, blocking=True)
        print('Antwort vom Server: {addr} msg'.format(addr=addr, msg=msg))
        if msg == 'OK':
            return client_sock
        if msg == 'NOPE':
            return 'NOPE'
    except:
        return None


# Send message to server and receive game
def send(sock, addr, data):
    try:
        get = data.startswith('GET')
        send_msg(sock, addr, data, blocking=get)
        if get:
            return recv_game(sock)
    except socket.error as e:
        print(e)
