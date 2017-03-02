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
base_directory = os.path.abspath(".")

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

    global current_directory
    global base_directory

    try:
        print("Thread Server Entering Now...")
        print(address)
        local_thread = threading.local()

        while True:

            print("Current Directory: " + current_directory)
            print("Base Directory: " + base_directory)
            print("TID = ", threading.current_thread())

            msg = str_msg_decode(connection_socket.recv(RECV_BUFFER))

            print("Received command: " + msg)

            if msg[0:4] == CMD_QUIT:
                quit_ftp(connection_socket, local_thread)
            elif msg[0:4] == CMD_USER:
                user_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_PASS:
                pass_ftp(connection_socket, local_thread, msg)
            elif msg[0:3] == CMD_CWD:
                cwd_ftp(connection_socket, local_thread, msg)
            elif msg[0:4] == CMD_CDUP:
                cdup_ftp(connection_socket, local_thread)
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
                pwd_ftp(connection_socket, local_thread)
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


# Change Working Directory (CWD)
def cwd_ftp(connection_socket, local_thread, msg):
    global current_directory
    global base_directory

    directory = msg[4:-1]

    if directory == "/":
        current_directory = base_directory
        local_thread = "250 CWD command successful\r\n"
    elif directory[0] == '/':
        path = os.path.join(base_directory, directory[1:])

        if os.path.exists(path):
            current_directory = path
            local_thread = "250 CWD command successful\r\n"
        else:
            local_thread = "550 " + directory[1:] + ": No such file or directory\r\n"
    else:
        path = os.path.join(current_directory, directory)

        if os.path.exists(path):
            current_directory = path
            local_thread = "250 CWD command successful\r\n"
        else:
            local_thread = "550 " + directory + ": No such file or directory\r\n"

    connection_socket.send(str_msg_encode(local_thread))


# Go back 1 directory
def cdup_ftp(connection_socket, local_thread):
    global current_directory
    global base_directory

    if not os.path.samefile(current_directory, base_directory):
        current_directory = os.path.abspath(os.path.join(current_directory, ".."))

    local_thread = "250 CDUP command successful\r\n"
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


# ReMove Directory (RMD)
def rmd_ftp(connection_socket, local_thread, msg):
    global current_directory

    remove_directory = msg[4:-1]
    path = os.path.join(current_directory, remove_directory)

    if remove_directory == "":
        local_thread = "501 Syntax error in parameters or arguments.\r\n"
    elif os.path.exists(path):
        os.rmdir(path)
        local_thread = "250 RMD command successful\r\n"
    else:
        local_thread = "550 " + remove_directory + ": No such file or directory\r\n"

    connection_socket.send(str_msg_encode(local_thread))


# MaKe Directory (MKD)
def mkd_ftp(connection_socket, local_thread, msg):
    global current_directory

    new_directory = msg[4:-1]
    path = os.path.join(current_directory, new_directory);

    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        for dirpath, dirnames, files in os.walk("./" + new_directory):
            if files != [] or dirnames != []:
                local_thread = "550 " + new_directory + ": Directory not empty\r\n"
                connection_socket.send(str_msg_encode(local_thread))
                return

    local_thread = "257 /" + new_directory + " - Directory successfully created\r\n"
    connection_socket.send(str_msg_encode(local_thread))


# Print Working Directory (PWD)
def pwd_ftp(connection_socket, local_thread):
    global current_directory
    global base_directory

    directory = os.path.relpath(current_directory, base_directory)

    if directory == ".":
        directory = ""

    local_thread = "257 /" + directory + " is the current directory\r\n"
    connection_socket.send(str_msg_encode(local_thread))


def list_ftp(connection_socket, local_thread, msg):
    local_thread = "150 Opening ASCII mode data connection for file list"
    connection_socket.send(str_msg_encode(local_thread))

    # TODO: print list

    local_thread = "226 Transfer complete"
    connection_socket.send(str_msg_encode(local_thread))


def noop_ftp(connection_socket, local_thread):
    local_thread = "200 NOOP command successful.\r\n"
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
