from socket import *
import threading
import time
import sys
import traceback
import errno
import os
import subprocess
import string
import random


# Global Variables & Constants

thread_list = []
RECV_BUFFER = 1024

config_path = os.path.abspath("server/conf")
print(config_path)

with open(config_path + "/sys.cfg", "r") as config_file:
    data = config_file.read().split("\n")

FTP_ROOT = data[0].split(" ")[1]
USER_DATA_PATH = data[1].split(" ")[1]
USER_DATA_FILE = data[2].split(" ")[1]
FTP_MODE = data[3].split(" ")[1]
DATA_PORT_FTP_SERVER = int(data[6].split(" ")[1])
FTP_LOG_PATH = data[9].split(" ")[1]
FTP_LOG_FILE = data[10].split(" ")[1]
SERVICE_PORT = int(data[11].split(" ")[1])

config_file.close()

USER_TYPE_ADMIN = "ADMIN"
USER_TYPE_USER = "USER"
USER_TYPE_NOTALLOWED = "NOTALLOWED"
USER_TYPE_LOCKED = "LOCKED"

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
        local_thread.response = response_msg("220 FTP Server v1.0")
        local_thread.current_directory = ""
        local_thread.base_directory = ""
        local_thread.rename_from_path = ""
        local_thread.rename_from_file = ""
        local_thread.set_type = "I"
        local_thread.current_user = ""
        local_thread.user_type = ""
        local_thread.logged_on = False
        local_thread.data_socket = None

        connection_socket.send(str_msg_encode(local_thread.response))

        while True:

            print("TID = ", threading.current_thread())
            print("Current Directory: " + local_thread.current_directory)
            print("Base Directory: " + local_thread.base_directory)
            print("Current user: " + local_thread.current_user)
            print("Type: " + local_thread.set_type)
            print("Logged on? " + str(local_thread.logged_on))

            cmd = str_msg_decode(connection_socket.recv(RECV_BUFFER))

            print("Received command: " + cmd)

            if cmd[0:4] == CMD_QUIT:
                quit_ftp(connection_socket, local_thread)
            elif cmd[0:4] == CMD_USER:
                user_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:4] == CMD_PASS:
                pass_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:3] == CMD_CWD:
                cwd_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:4] == CMD_CDUP:
                cdup_ftp(connection_socket, local_thread)
            elif cmd[0:4] == CMD_RETR:
                retr_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:4] == CMD_STOR:
                stor_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:4] == CMD_STOU:
                stou_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:4] == CMD_APPE:
                appe_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:4] == CMD_TYPE:
                type_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:4] == CMD_RNFR:
                rnfr_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:4] == CMD_RNTO:
                rnto_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:4] == CMD_DELE:
                dele_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:3] == CMD_RMD:
                rmd_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:3] == CMD_MKD:
                mkd_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:3] == CMD_PWD:
                pwd_ftp(connection_socket, local_thread)
            elif cmd[0:4] == CMD_LIST:
                list_ftp(connection_socket, local_thread, cmd)
            elif cmd[0:4] == CMD_NOOP:
                noop_ftp(connection_socket, local_thread)
            elif cmd[0:4] == CMD_PORT:
                port_ftp(connection_socket, local_thread, cmd)
            else:
                local_thread = ("You said what? " + cmd)
                print(local_thread.response)
                connection_socket.send(str_msg_encode(response_msg(local_thread.response)))
    except OSError as e:
        print("Socket error:", e)


# QUIT (QUIT)
def quit_ftp(connection_socket, local_thread):
    local_thread.response = response_msg("221 Goodbye.")
    connection_socket.send(str_msg_encode(local_thread.response))
    connection_socket.close()


# USERname (USER)
def user_ftp(connection_socket, local_thread, cmd):
    local_thread.current_user = cmd[5:-1]
    local_thread.response = response_msg("331 Password required for " + local_thread.current_user)
    connection_socket.send(str_msg_encode(local_thread.response))


# PASSword (PASS)
def pass_ftp(connection_socket, local_thread, cmd):
    global USER_DATA_PATH
    global USER_DATA_FILE

    user_data_path = os.path.abspath(USER_DATA_PATH)

    with open(user_data_path + USER_DATA_FILE, "r") as user_data_file:
        user_data = user_data_file.read().split("\n")

    for user in user_data:
        if local_thread.current_user == user.split(" ")[0]:
            print("Found user " + local_thread.current_user)

            if cmd[5:-1] == user.split(" ")[1]:
                local_thread.user_type = user.split(" ")[2].upper()

                if local_thread.user_type == USER_TYPE_ADMIN:
                    print("Admin type")
                    local_thread.base_directory = os.path.abspath(FTP_ROOT)
                    local_thread.current_directory = os.path.abspath(FTP_ROOT + "/" + local_thread.current_user)
                    local_thread.logged_on = True
                    local_thread.response = "230 Admin access granted"
                    break

                elif local_thread.user_type == USER_TYPE_USER:
                    print("User type")
                    local_thread.base_directory = os.path.abspath(FTP_ROOT + "/" + local_thread.current_user)
                    local_thread.current_directory = os.path.abspath(FTP_ROOT + "/" + local_thread.current_user)
                    local_thread.logged_on = True
                    local_thread.response = "230 User access granted, restrictions apply"
                    break

                elif local_thread.user_type == USER_TYPE_NOTALLOWED:
                    print("You're not allowed here.")
                    local_thread.logged_on = False
                    local_thread.response = "530 " + local_thread.current_user + " is not allowed."
                    break

                elif local_thread.user_type == USER_TYPE_LOCKED:
                    print("You're locked, try again later.")
                    local_thread.logged_on = False
                    local_thread.response = "530 " + local_thread.current_user + " is locked out."
                    break

                else:
                    print("Setting unknown type to " + USER_TYPE_NOTALLOWED)
                    local_thread.user_type = USER_TYPE_NOTALLOWED
                    local_thread.logged_on = False
                    local_thread.response = "530 " + local_thread.current_user + " is not allowed."
                    break

            else:
                print("Wrong password for user " + local_thread.current_user)
                local_thread.logged_on = False
                local_thread.response = "530 Login incorrect."
                break

        else:
            print("Did not find user " + local_thread.current_user)
            local_thread.logged_on = False
            local_thread.response = "530 Login incorrect."

    user_data_file.close()
    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# Change Working Directory (CWD)
def cwd_ftp(connection_socket, local_thread, cmd):

    if local_thread.logged_on:
        directory = cmd[4:-1]

        if directory == "/":
            local_thread.current_directory = local_thread.base_directory
            local_thread.response = "250 CWD command successful"
        elif directory[0] == '/':
            path = os.path.join(local_thread.base_directory, directory[1:])

            if os.path.exists(path):
                local_thread.current_directory = path
                local_thread.response = "250 CWD command successful"
            else:
                local_thread.response = "550 " + directory[1:] + ": No such file or directory"
        else:
            path = os.path.join(local_thread.current_directory, directory)

            if os.path.exists(path):
                local_thread.current_directory = path
                local_thread.response = "250 CWD command successful"
            else:
                local_thread.response = "550 " + directory + ": No such file or directory"

    else:
        local_thread.response = "530 Please login with USER and PASS"

    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# Go back 1 directory
def cdup_ftp(connection_socket, local_thread):

    if local_thread.logged_on:
        if not os.path.samefile(local_thread.current_directory, local_thread.base_directory):
            local_thread.current_directory = os.path.abspath(os.path.join(local_thread.current_directory, ".."))

        local_thread.response = "250 CDUP command successful"
    else:
        local_thread.response = "530 Please login with USER and PASS"

    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# RETRieve (RETR)
def retr_ftp(connection_socket, local_thread, cmd):

    file = cmd.split()[1]
    path = os.path.join(local_thread.current_directory, file)

    if os.path.isdir(path):
        local_thread.response = "550 " + file + ": Not a regular file"
        connection_socket.send(str_msg_encode(response_msg(local_thread.response)))
    elif os.path.exists(path):
        local_thread.response = "150 Opening " + get_type(local_thread.set_type) + " mode data connection for " + file
        connection_socket.send(str_msg_encode(response_msg(local_thread.response)))

        open_file = open(path, get_file_mode(local_thread, "r"))

        while True:
            file_data = open_file.read(RECV_BUFFER)

            if isinstance(file_data, str):
                file_data = str_msg_encode(file_data)

            if len(file_data) < RECV_BUFFER:
                local_thread.data_socket.send(file_data)
                open_file.close()
                break
            local_thread.data_socket.send(file_data)

        local_thread.response = "226 Transfer complete"
        connection_socket.send(str_msg_encode(response_msg(local_thread.response)))
    else:
        local_thread.response = "550 " + file + ": No such file or directory"
        connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


def get_file_mode(local_thread, mode):
    if local_thread.set_type == "A":
        return mode
    else:
        return mode + "b"


# STORe (STOR)
def stor_ftp(connection_socket, local_thread, cmd):

    file = cmd.split()[1]
    path = os.path.join(local_thread.current_directory, file)

    local_thread.response = "150 Opening " + get_type(local_thread.set_type) + " mode data connection for " + file
    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))

    open_file = open(path, get_file_mode(local_thread, "w"))

    while True:
        file_data = local_thread.data_socket.recv(RECV_BUFFER)

        if local_thread.set_type == "A":
            file_data = str_msg_decode(file_data)

        if len(file_data) < RECV_BUFFER:
            open_file.write(file_data)
            open_file.close()
            break
        open_file.write(file_data)

    local_thread.response = "226 Transfer complete"
    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# STOre Unique (STOU)
def stou_ftp(connection_socket, local_thread, cmd):

    file = "ftp"
    counter = 6
    while counter > 0:
        file += random.choice(string.ascii_letters + string.digits)
        counter -= 1

    path = os.path.join(local_thread.current_directory, file)

    local_thread.response = "150 FILE: " + file
    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))

    open_file = open(path, get_file_mode(local_thread, "w"))

    while True:
        file_data = local_thread.data_socket.recv(RECV_BUFFER)

        if local_thread.set_type == "A":
            file_data = str_msg_decode(file_data)

        if len(file_data) < RECV_BUFFER:
            open_file.write(file_data)
            open_file.close()
            break
        open_file.write(file_data)

    local_thread.response = "226 Transfer complete"
    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# APPEnd (APPE)
def appe_ftp(connection_socket, local_thread, cmd):

    file = cmd.split()[1]
    path = os.path.join(local_thread.current_directory, file)

    local_thread.response = "150 Opening " + get_type(local_thread.set_type) + " mode data connection for " + file
    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))

    open_file = open(path, get_file_mode(local_thread, "a"))

    while True:
        file_data = local_thread.data_socket.recv(RECV_BUFFER)

        if local_thread.set_type == "A":
            file_data = str_msg_decode(file_data)

        if len(file_data) < RECV_BUFFER:
            open_file.write(file_data)
            open_file.close()
            break
        open_file.write(file_data)

    local_thread.response = "226 Transfer complete"
    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


def type_ftp(connection_socket, local_thread, cmd):
    local_thread.set_type = cmd[5]
    local_thread.response = "200 Type set to " + local_thread.set_type
    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# ReName FRom (RNFR)
def rnfr_ftp(connection_socket, local_thread, cmd):

    local_thread.rename_from_file = cmd[5:-1]
    local_thread.rename_from_path = os.path.join(local_thread.current_directory, cmd[5:-1])

    if local_thread.logged_on:
        if os.path.exists(local_thread.rename_from_path):
            local_thread.response = "350 File or directory exists, ready for destination name"
        else:
            local_thread.response = "550 " + local_thread.rename_from_file + ": No such file or directory"
    else:
        local_thread.response = "530 Please login with USER and PASS"

    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# ReName TO (RNTO)
def rnto_ftp(connection_socket, local_thread, cmd):

    if local_thread.logged_on:
        if os.path.exists(local_thread.rename_from_path):
            rename_to = os.path.join(local_thread.current_directory, cmd[5:-1])
            os.rename(local_thread.rename_from_path, rename_to)
            local_thread.response = "250 Rename successful"
    else:
        local_thread.response = "530 Please login with USER and PASS"

    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# DELEt file (DELE)
def dele_ftp(connection_socket, local_thread, cmd):

    if local_thread.logged_on:
        file = cmd[5:-1]
        path = os.path.join(local_thread.current_directory, file)

        if os.path.isdir(path):
            local_thread.response = "550 " + file + ": Is a directory"
        elif os.path.exists(path):
            os.remove(path)
            local_thread.response = "250 DELE command successful"
        else:
            local_thread.response = "550 " + file + ": No such file or directory"
    else:
        local_thread.response = "530 Please login with USER and PASS"

    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# ReMove Directory (RMD)
def rmd_ftp(connection_socket, local_thread, cmd):

    if local_thread.logged_on:
        remove_directory = cmd[4:-1]
        path = os.path.join(local_thread.current_directory, remove_directory)

        if remove_directory == "":
            local_thread.response = "501 Syntax error in parameters or arguments."
        elif os.path.exists(path):
            if directory_is_empty(path):
                os.rmdir(path)
                local_thread.response = "250 RMD command successful"
            else:
                local_thread.response = "550 " + remove_directory + ": Directory not empty"

        else:
            local_thread.response = "550 " + remove_directory + ": No such file or directory"

    else:
        local_thread.response = "530 Please login with USER and PASS"

    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# MaKe Directory (MKD)
def mkd_ftp(connection_socket, local_thread, cmd):

    if local_thread.logged_on:
        new_directory = cmd[4:-1]
        path = os.path.join(local_thread.current_directory, new_directory)

        if not os.path.isdir(path):
            os.mkdir(path)
        else:
            if directory_is_empty(path):
                local_thread.response = "257 /" + new_directory + " - Directory successfully created"
            else:
                local_thread.response = "550 " + new_directory + ": Directory not empty"
    else:
        local_thread.response = "530 Please login with USER and PASS"

    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# Print Working Directory (PWD)
def pwd_ftp(connection_socket, local_thread):

    if local_thread.logged_on:
        directory = os.path.relpath(local_thread.current_directory, local_thread.base_directory)

        if directory == ".":
            directory = ""

        local_thread.response = "257 /" + directory + " is the current directory"
    else:
        local_thread.response = "530 Please login with USER and PASS"

    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# LIST (LIST)
def list_ftp(connection_socket, local_thread, cmd):

    local_thread.response = "150 Opening ASCII mode data connection for file list"
    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))

    directory = cmd[5:-1]
    if directory != "":
        path = os.path.join(local_thread.current_directory, directory)
        if os.path.exists(path):
            directory_list(path, local_thread)
        else:
            local_thread.data_socket.send(str_msg_encode(response_msg("450 " + directory + ": No such file or directory")))
            return

    directory_list(local_thread.current_directory, local_thread)
    local_thread.response = "226 Transfer complete"
    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# NOOP (NOOP)
def noop_ftp(connection_socket, local_thread):
    local_thread.response = "200 NOOP command successful"
    connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


# PORT (PORT)
def port_ftp(connection_socket, local_thread, cmd):

    if local_thread.logged_on:
        cmd = cmd.split(" ")
        address = cmd[1].split(",")
        ip = address[0] + "." + address[1] + "." + address[2] + "." + address[3]
        port = (int(address[4]) * 256) + int(address[5])

        local_thread.data_socket = socket(AF_INET, SOCK_STREAM)
        local_thread.data_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        local_thread.data_socket.connect((ip, port))

        local_thread.response = "200 PORT command successful"
        connection_socket.send(str_msg_encode(response_msg(local_thread.response)))
    else:
        local_thread.response = "530 Please login with USER and PASS"
        connection_socket.send(str_msg_encode(response_msg(local_thread.response)))


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


def response_msg(msg):
    return msg + "\r\n"


def directory_is_empty(path):
    if os.listdir(path) == []:
        return True
    else:
        return False


def get_type(type):
    if type == "A":
        return "ASCII"
    elif type == "I":
        return "BINARY"
    else:
        return ""


def directory_list(path, local_thread):
    for item in os.listdir(path):
        local_thread.data_socket.send(str_msg_encode(response_msg(item)))


def main():
    try:
        global thread_list

        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.bind(('', DATA_PORT_FTP_SERVER))
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
