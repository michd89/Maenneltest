import datetime
import pickle
import socket
import time

ENCODING = 'utf-8'
RECV_SIZE = 4096

PORT = 50000


UPDATE_TIME = 100  # in ms
UPDATE_TIMEDELTA = datetime.timedelta(milliseconds=UPDATE_TIME)

DATE_FORMAT = '%Y%d%m%H%M%S%f'


def str_to_datetime(date_string):
    return datetime.datetime.strptime(date_string, DATE_FORMAT)


def datetime_to_str(date_time):
    return datetime.datetime.strftime(date_time, DATE_FORMAT)


def send_msg(sock, addr, msg, blocking=False, sim_latency=None):
    sock.setblocking(blocking)
    if sim_latency:  # https://stackoverflow.com/a/62456696
        time.sleep(sim_latency)
    sock.sendto(msg.encode(ENCODING), addr)


def recv_msg(sock, blocking=False, sim_latency=None):
    try:
        sock.setblocking(blocking)
        if sim_latency:  # https://stackoverflow.com/a/62456696
            time.sleep(sim_latency)
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


def join_game(addr, nickname):
    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_sock.connect(addr)
        send_msg(client_sock, addr, 'JOIN ' + nickname)
        msg, addr = recv_msg(client_sock, blocking=True)
        print('Response from server: {addr} {msg}'.format(addr=addr, msg=msg))
        if msg.startswith('OK'):
            return client_sock, msg.split()[1]
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
