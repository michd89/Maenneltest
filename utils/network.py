import datetime
import pickle
import socket

ENCODING = 'utf-8'
RECV_SIZE = 4096

PORT = 50000

UPDATE_TIME = 100  # in ms
UPDATE_TIMEDELTA = datetime.timedelta(milliseconds=UPDATE_TIME)
PING_TIME = 2000  # in ms
PING_TIMEDELTA = datetime.timedelta(milliseconds=PING_TIME)

DATE_FORMAT = '%Y%d%m%H%M%S%f'


def str_to_datetime(date_string):
    return datetime.datetime.strptime(date_string, DATE_FORMAT)


def datetime_to_str(date_time):
    return datetime.datetime.strftime(date_time, DATE_FORMAT)


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


# Send message to server and receive game
def send(sock, addr, data):
    try:
        get = data.startswith('GET')
        send_msg(sock, addr, data, blocking=get)
        if get:
            return recv_game(sock)
    except socket.error as e:
        print(e)
