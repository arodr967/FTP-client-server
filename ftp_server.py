from socket import *
import threading
import time
import sys
import traceback
import errno
import os


# Global Variables & Constants

thread_list = []
RECV_BUFFER = 1024
current_directory = os.path.abspath(".")

# Commands

CMD_USER = "USER"
CMD_PASS = "PASS"
CMD_CWD = "CWD"
CMD_CDUP = "CDUP"
CMD_RETR = "RETR"
CMD_STOR = "STOR"
CMD_STOU = "STOU"
CMD_APPE = "APPE"
CMD_TYPE = "TYPE"
CMD_RNFR = "RNFR"
CMD_RNTO = "RNTO"
CMD_DELE = "DELE"
CMD_RMD = "RMD"
CMD_MKD = "MKD"
CMD_PWD = "PWD"
CMD_LIST = "LIST"
CMD_NOOP = "NOOP"
CMD_PORT = "PORT"
CMD_QUIT = "QUIT"


def server_thread(connection_socket, address):

    try:
        print("Thread Server Entering Now...")
        print(address)
        local_thread = threading.local()

        while True:

            print("TID = ", threading.current_thread())

            msg = str_msg_decode(connection_socket.recv(RECV_BUFFER))

            if msg[0:4] == CMD_QUIT:
                quit_ftp(connection_socket, local_thread)
            elif msg[0:4] == CMD_USER:
                user_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_PASS:
                pass_ftp(connection_socket, local_thread, msg)
            elif msg[0:3] == CMD_CWD:
                cwd_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_CDUP:
                cdup_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_RETR:
                retr_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_STOR:
                stor_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_STOU:
                stou_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_APPE:
                appe_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_TYPE:
                type_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_RNFR:
                rnfr_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_RNTO:
                rnto_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_DELE:
                dele_ftp(connection_socket, local_thread, msg)
            elif msg[0:3] == CMD_RMD:
                rmd_ftp(connection_socket, local_thread, msg)
            elif msg[0:3] == CMD_MKD:
                mkd_ftp(connection_socket, local_thread, msg)
            elif msg[0:3] == CMD_PWD:
                pwd_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_LIST:
                list_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_NOOP:
                noop_ftp(connection_socket, local_thread)
            elif msg[0:4] == CMD_PORT:
                port_ftp(connection_socket, local_thread, msg)
            else:
                local_thread = ("You said what? " + msg)
                print(local_thread)
                connection_socket.send(str_msg_encode(local_thread))
    except OSError as e:
        # A socket error
        print("Socket error:", e)


def quit_ftp(connection_socket, local_thread):
    local_thread = "221 Goodbye.\r\n"
    connection_socket.send(str_msg_encode(local_thread))
    connection_socket.close()


def user_ftp(connection_socket, local_thread, msg):
    local_thread = "331 Password required for " + msg[4:-1] + "\r\n"
    connection_socket.send(str_msg_encode(local_thread))


def pass_ftp(connection_socket, local_thread, msg):
    # TODO: if user is part of the user
    local_thread = "230 Anonymous access granted, restrictions apply\r\n"
    connection_socket.send(str_msg_encode(local_thread))


def cwd_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def cdup_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def retr_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def stor_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def stou_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def appe_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def type_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def rnfr_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def rnto_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def dele_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def rmd_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def mkd_ftp(connection_socket, local_thread, msg):
    new_directory = msg[4:-1]
    new_path = os.path.join(current_directory, new_directory)
    os.mkdir(new_path)
    if not os.path.isdir(new_path):
        local_thread = "257 /" + new_directory + " - Directory successfully created\r\n"
        connection_socket.send(str_msg_encode(local_thread))
    else:
        local_thread = ""


def pwd_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def list_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def noop_ftp(connection_socket, local_thread):
    local_thread = "200 OK.\r\n"
    connection_socket.send(str_msg_encode(local_thread))


def port_ftp(connection_socket, local_thread, msg):
    connection_socket.send(str_msg_encode(local_thread))


def join_all_threads():
    global thread_list
    for t in thread_list:
        t.join()


def str_msg_encode(str_value):

    msg = str_value.encode()
    return msg


def str_msg_decode(msg, print_strip=False):

    str_value = msg.decode()
    if print_strip:
        str_value.strip('\n')
    return str_value


def main():
    try:
        global thread_list

        server_port = 2129
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.bind(('', server_port))
        server_socket.listen(15)
        print('The server is ready to receive...')

        while True:
            connection_socket, address = server_socket.accept()
            t = threading.Thread(target=server_thread, args=(connection_socket, address))
            t.start()
            thread_list.append(t)
            print("Thread started")
            print("Waiting for another connection")
    except KeyboardInterrupt:
        print("Keyboard Interrupt. Time to say goodbye!!!")
        join_all_threads()

    print("The end")
    sys.exit(0)

if __name__ == "__main__":
    main()
