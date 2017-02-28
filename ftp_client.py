from socket import *
import os
import os.path
import errno
import traceback
import sys


# Global constants
USAGE = "usage: Python ftp hostname [username] [password]"

RECV_BUFFER = 1024
FTP_PORT = 2129

# Commands

CMD_QUIT = "QUIT"
CMD_BYE = "BYE"
CMD_EXIT = "EXIT"
CMD_HELP = "HELP"
CMD_LOGIN = "LOGIN"
CMD_LOGOUT = "LOGOUT"
CMD_LS = "LS"
CMD_PWD = "PWD"
CMD_DELETE = "DELETE"
CMD_MDELETE = "MDELETE"
CMD_PUT = "PUT"
CMD_SEND = "SEND"
CMD_GET = "GET"
CMD_RECV = "RECV"
CMD_USER = "USER"
CMD_CD = "CD"
CMD_CDUP = "CDUP"
CMD_MKDIR = "MKDIR"
CMD_RENAME = "RENAME"
CMD_RMDIR = "RMDIR"
CMD_ASCII = "ASCII"
CMD_IMAGE = "IMAGE"

# TODO

CMD_STOU = "STOU"
CMD_APPEND = "APPEND"
CMD_PORT = "PORT"
CMD_LCD = "LCD"


# The data port starts at high number (to avoid privileges port 1-1024)
# the ports ranges from MIN to MAX
DATA_PORT_MAX = 34999
DATA_PORT_MIN = 34500
# data back log for listening.
DATA_PORT_BACKLOG = 1

# global variables
# store the next_data_port use in a formula to obtain
# a port between DATA_POR_MIN and DATA_PORT_MAX
next_data_port = 1


# entry point main()
def main():

    hostname = "cnt4713.cs.fiu.edu"
    username = ""
    password = ""

    logged_on = False
    logon_ready = False
    print("FTP Client v1.0")

    if len(sys.argv) < 2:
        print(USAGE)
    if len(sys.argv) is 2:
        hostname = sys.argv[1]
    if len(sys.argv) is 4:
        username = sys.argv[2]
        password = sys.argv[3]
        logon_ready = True

    print("********************************************************************")
    print("**                        ACTIVE MODE ONLY                        **")
    print("********************************************************************")
    print("You will be connected to host:" + hostname)
    print("Type HELP for more information")
    print("Commands are NOT case sensitive\n")

    ftp_socket = ftp_connecthost(hostname)
    ftp_socket.send(str_msg_encode("NOOP \n"))

    # print(str_msg_decode(ftp_recv, True))

    if logon_ready:
        logged_on = login(username, password, ftp_socket)

    keep_running = True

    while keep_running:
        try:
            user_input = input("ftp> ")
            if user_input is None or user_input.strip() == '':
                continue
            tokens = user_input.split()
            cmd_msg, logged_on, ftp_socket = run_commands(tokens, logged_on, ftp_socket)
            if cmd_msg != "":
                print(cmd_msg)
        except OSError as e:
            print("Socket error:", e)
            str_error = str(e)
            if str_error.find("[Errno 32]") >= 0:
                sys.exit()

    try:
        ftp_socket.close()
        print("Thank you for using FTP 1.0")
    except OSError as e:
        print("Socket error:", e)
    sys.exit()


def run_commands(username, password, tokens, logged_on, ftp_socket, hostname):

    cmd = tokens[0].upper()

    if cmd == CMD_QUIT or cmd == CMD_BYE or cmd == CMD_EXIT:
        quit_ftp(logged_on, ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == "!":
        sys.exit()
        return "", logged_on, ftp_socket

    if cmd == CMD_HELP or cmd == "?":
        help_ftp()
        return "", logged_on, ftp_socket

    if cmd == CMD_PWD:
        pwd_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_CD:
        cd_ftp(tokens, ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_CDUP:
        cdup_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_MKDIR:
        mkdir_ftp(tokens, ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_RMDIR:
        rmdir_ftp(tokens, ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_STOU:
        stou_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_RENAME:
        rename_ftp(tokens, ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_ASCII:
        ascii_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_IMAGE:
        image_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_APPEND:
        data_socket = ftp_new_dataport(ftp_socket)
        if data_socket is not None:
            get_ftp(tokens, ftp_socket, data_socket)
            return "", logged_on, ftp_socket
        else:
            return "[GET] Failed to get data port. Try again.", logged_on, ftp_socket

    if cmd == CMD_LS:
        data_socket = ftp_new_dataport(ftp_socket)
        if data_socket is not None:
            ls_ftp(tokens, ftp_socket, data_socket)
            return "", logged_on, ftp_socket
        else:
            return "[LS] Failed to get data port. Try again.", logged_on, ftp_socket

    if cmd == CMD_LOGIN or cmd == CMD_USER:
        logged_on = user_ftp(username, password, tokens, ftp_socket, hostname)
        return "", logged_on, ftp_socket

    if cmd == CMD_LOGOUT:
        logged_on, ftp_socket = logout(logged_on, ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_DELETE:
        delete_ftp(tokens, ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_MDELETE:
        mdelete_ftp(tokens, ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_PUT or cmd == CMD_SEND:
        data_socket = ftp_new_dataport(ftp_socket)
        if data_socket is not None:
            put_ftp(tokens, ftp_socket, data_socket)
            return "", logged_on, ftp_socket
        else:
            return "[PUT] Failed to get data port. Try again.", logged_on, ftp_socket

    if cmd == CMD_GET or cmd == CMD_RECV:
        # FTP must create a channel to received data before
        # executing get.
        # also makes sure that data_socket is valid
        # in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if data_socket is not None:
            get_ftp(tokens, ftp_socket, data_socket)
            return "", logged_on, ftp_socket
        else:
            return "[GET] Failed to get data port. Try again.", logged_on, ftp_socket

    return "Unknown command", logged_on, ftp_socket


def str_msg_encode(str_value):

    msg = str_value.encode()
    return msg


def str_msg_decode(msg, print_strip=False):

    str_value = msg.decode()
    if print_strip:
        str_value.strip('\n')
    return str_value


def ftp_connecthost(hostname):

    ftp_socket = socket(AF_INET, SOCK_STREAM)
    ftp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    ftp_socket.connect((hostname, FTP_PORT))

    print("Connected to " + hostname)

    return ftp_socket


def ftp_new_dataport(ftp_socket):

    global next_data_port
    data_port = next_data_port
    host = gethostname()
    host_address = gethostbyname(host)
    next_data_port = next_data_port + 1
    data_port = (DATA_PORT_MIN + data_port) % DATA_PORT_MAX

    data_socket = socket(AF_INET, SOCK_STREAM)
    # reuse port
    data_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    data_socket.bind((host_address, data_port))
    data_socket.listen(DATA_PORT_BACKLOG)

    # the port requires the following
    # PORT IP PORT
    # however, it must be transmitted like this.
    # PORT 192,168,1,2,17,24
    # where the first four octet are the ip and the last two form a port number.
    host_address_split = host_address.split('.')
    high_data_port = str(data_port // 256)  # get high part
    low_data_port = str(data_port % 256)  # similar to data_port << 8 (left shift)
    port_argument_list = host_address_split + [high_data_port, low_data_port]
    port_arguments = ','.join(port_argument_list)
    cmd_port_send = CMD_PORT + ' ' + port_arguments + "\r\n"

    try:
        ftp_socket.send(str_msg_encode(cmd_port_send))
    except socket.timeout:
        print("Socket timeout. Port may have been used recently. wait and try again!")
        return None
    except socket.error:
        print("Socket error. Try again")
        return None

    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))

    return data_socket


def pwd_ftp(ftp_socket):

    ftp_socket.send(str_msg_encode("PWD\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout(str_msg_decode(msg, True))


def cd_ftp(tokens, ftp_socket):

    if len(tokens) is 1:
        remote_directory = input("(remote-directory) ")
    else:
        remote_directory = tokens[1]

    ftp_socket.send(str_msg_encode("CWD " + remote_directory + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))


def cdup_ftp(ftp_socket):
    ftp_socket.send(str_msg_encode("CDUP\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))


def mkdir_ftp(tokens, ftp_socket):

    if len(tokens) is 1:
        directory_name = input("(directory-name) ")
    else:
        directory_name = tokens[1]

    ftp_socket.send(str_msg_encode("MKD " + directory_name + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)

    response = str_msg_decode(msg)
    tokens = response.split()

    if tokens[0] == "501":
        print("usage: mkdir directory-name")
    else:
        sys.stdout.write(str_msg_decode(msg, True))


def rmdir_ftp(tokens, ftp_socket):

    if len(tokens) is 1:
        directory_name = input("(directory-name) ")
    else:
        directory_name = tokens[1]

    ftp_socket.send(str_msg_encode("RMD " + directory_name + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)

    response = str_msg_decode(msg)
    tokens = response.split()

    if tokens[0] == "501":
        print("usage: rmdir directory-name")
    else:
        sys.stdout.write(str_msg_decode(msg, True))


def ascii_ftp(ftp_socket):

    ftp_socket.send(str_msg_encode("TYPE A\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))


def image_ftp(ftp_socket):

    ftp_socket.send(str_msg_encode("TYPE I\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))


def stou_ftp(ftp_socket):
    ftp_socket.send("STOU\n".encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))


def rename_ftp(tokens, ftp_socket):

    if len(tokens) is 1:
        from_name = input("(from-name) ")

        if from_name is "":
            print("rename from-name to-name")
            return

        to_name = input("(to-name) ")

        if to_name is "":
            print("rename from-name to-name")
            return

    elif len(tokens) is 2:
        from_name = tokens[1]

        if from_name is "":
            print("rename from-name to-name")
            return

        to_name = input("(to-name) ")

        if to_name is "":
            print("rename from-name to-name")
            return

    elif len(tokens) is 3:
        from_name = tokens[1]
        to_name = tokens[2]
    else:
        from_name = tokens[1]
        to_name = tokens[2]

    ftp_socket.send(str_msg_encode("RNFR " + from_name + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))

    ftp_socket.send(str_msg_encode("RNTO " + to_name + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)

    tokens = str_msg_decode(msg).split()

    if tokens[0] == "503":
        return
    else:
        sys.stdout.write(str_msg_decode(msg, True))


def get_ftp(tokens, ftp_socket, data_socket):

    if len(tokens) is 1:
        remote_file = input("(remote-file) ")
    elif len(tokens) is 2:
        remote_file = tokens[1]
        local_file = input("(local-file) ")
    elif len(tokens) is 3:
        remote_file = tokens[1]
        local_file = tokens[2]
    else:
        remote_file = tokens[1]
        local_file = tokens[2]

    ftp_socket.send(str_msg_encode("RETR " + remote_file + "\n"))

    msg = ftp_socket.recv(RECV_BUFFER)
    str_value = str_msg_decode(msg)
    tokens = str_value.split()
    if tokens[0] != "150":
        print("Unable to retrieve file. Check that file exists (ls) or that you have permissions")
        return

    print(str_msg_decode(msg, True))

    data_connection, data_host = data_socket.accept()
    file_bin = open(local_file, "wb")  # read and binary modes

    size_recv = 0
    while True:
        data = data_connection.recv(RECV_BUFFER)

        if not data or data == '' or len(data) <= 0:
            file_bin.close()
            break
        else:
            file_bin.write(data)
            size_recv += len(data)

    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    print(str_msg_decode(msg, True))


def put_ftp(tokens, ftp_socket, data_socket):

    if len(tokens) is 1:
        local_file = input("(local-file) ")
        remote_file = input("(remote-file) ")
    elif len(tokens) is 2:
        local_file = tokens[1]
        remote_file = local_file
    else:
        local_file = tokens[1]
        remote_file = tokens[2]

    if os.path.isfile(local_file) is False:
        print("local: " + local_file + " remote: " + remote_file)
        print("local: " + local_file + ": No such file or directory")
        return

    ftp_socket.send(str_msg_encode("STOR " + remote_file + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))

    data_connection, data_host = data_socket.accept()
    file_bin = open(remote_file, "rb")  # read and binary modes

    size_sent = 0
    while True:

        data = file_bin.read(RECV_BUFFER)
        if not data or data == '' or len(data) <= 0:
            file_bin.close()
            break
        else:
            data_connection.send(data)
            size_sent += len(data)

    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))


def ls_ftp(tokens, ftp_socket, data_socket):

    if len(tokens) > 1:
        ftp_socket.send(str_msg_encode("LIST " + tokens[1] + "\n"))
    else:
        ftp_socket.send(str_msg_encode("LIST\n"))

    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))

    data_connection, data_host = data_socket.accept()

    msg = data_connection.recv(RECV_BUFFER)
    while len(msg) > 0:
        sys.stdout.write(str_msg_decode(msg, True))
        msg = data_connection.recv(RECV_BUFFER)

    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))


def delete_ftp(tokens, ftp_socket):

    if len(tokens) is 1:
        remote_file = input("(remote-file) ")

    else:
        remote_file = tokens[1]

    ftp_socket.send(str_msg_encode("DELE " + remote_file + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)

    response = str_msg_decode(msg)
    tokens = response.split()

    if tokens[0] == "501":
        print("usage: delete remote-file")
    else:
        print(str_msg_decode(msg, True))


def mdelete_ftp(tokens, ftp_socket):

    if len(tokens) is 1:
        remote_files = input("(remote-files) ")
        tokens = remote_files.split(" ")

    for remote_file in tokens:
        if remote_file.upper() != CMD_MDELETE:
            confirmDelete = input("mdelete " + remote_file + "? ")

            if confirmDelete.upper() != "NO":
                ftp_socket.send(str_msg_encode("DELE " + remote_file + "\n"))
                msg = ftp_socket.recv(RECV_BUFFER)
                sys.stdout.write(str_msg_decode(msg, True))


def logout(lin, ftp_socket):

    if ftp_socket is None:
        # print("Your connection was already terminated.")
        return False, ftp_socket

    # if lin is False:
    #     print("You are not logged in. Logout command will be sent anyways")

    # print("Attempting to logged out")
    msg = ""
    try:
        ftp_socket.send(str_msg_encode("QUIT\n"))
        msg = ftp_socket.recv(RECV_BUFFER)
    except socket.error:
        print("Problems logging out. Try logout again. Do not login if you haven't logged out!")
        return False
    sys.stdout.write(str_msg_decode(msg, True))
    ftp_socket = None
    return False, ftp_socket  # it should only be true if logged in and not able to logout


def quit_ftp(lin, ftp_socket):

    # print("Quitting...")
    logged_on, ftp_socket = logout(lin, ftp_socket)
    # print("Thank you for using FTP")
    try:
        if ftp_socket is not None:
            ftp_socket.close()
    except socket.error:
        print("Socket was not able to be close. It may have been closed already")
    sys.exit()


# def exclamation_ftp():
#     sys.exit()


def relogin(username, password, logged_on, tokens, hostname, ftp_socket):

    if len(tokens) < 3:
        # print("LOGIN requires 2 arguments. LOGIN [username] [password]")
        # print("You will be prompted for username and password now")
        username = input("Username: ")
        password = input("Password: ")
    else:
        username = tokens[1]
        password = tokens[2]

    if ftp_socket is None:
        ftp_socket = ftp_connecthost(hostname)
        ftp_recv = ftp_socket.recv(RECV_BUFFER)
        print(ftp_recv.strip('\n'))

    logged_on = login(username, password, ftp_socket)
    return username, password, logged_on, ftp_socket


def user_ftp(username, password, tokens, ftp_socket, hostname):
    if ftp_socket is None:
        ftp_socket = ftp_connecthost(hostname)
        msg = ftp_socket.recv(RECV_BUFFER)
        print(str_msg_decode(msg, True))

    if len(tokens) is 1:
        username = input("(username) ")
        password = ""
    elif len(tokens) is 2:
        username = tokens[1]
        password = ""
    elif len(tokens) is 3:
        username = tokens[1]
        password = tokens[2]
    else:
        print("Third argument is not supported.")
        return;

    ftp_socket.send(str_msg_encode("USER " + username + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(str_msg_decode(msg, True))

    if password is "":
        password = input("Password: ")

    ftp_socket.send(str_msg_encode("PASS " + password + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(str_msg_decode(msg, True))

    str_value = str_msg_decode(msg, False)
    tokens = str_value.split()

    if len(tokens) > 0 and tokens[0] != "230":
        print("Login failed.")
        # TODO: close connection after first failed attempt
        return False
    else:
        return True


def login(username, password, ftp_socket):

    if username is None or username.strip() is "":
        print("Username is blank. Try again")
        return False

    print("Attempting to login user " + username)

    ftp_socket.send(str_msg_encode("USER " + username + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(str_msg_decode(msg, True))

    ftp_socket.send(str_msg_encode("PASS " + password + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(str_msg_decode(msg, True))

    str_value = str_msg_decode(msg, False)
    tokens = str_value.split()

    if len(tokens) > 0 and tokens[0] != "230":
        print("Not able to login. Please check your username or password. Try again!")
        return False
    else:
        return True


def help_ftp():
    print("FTP Help")
    print("Commands are not case sensitive")
    print("")
    print("COMMAND\t\t Description")
    print(CMD_QUIT + "\t\t Exits ftp and attempts to logout")
    print(CMD_LOGIN + "\t\t Login. It expects username and password. LOGIN [username] [password]")
    print(CMD_LOGOUT + "\t\t Logout from ftp but not client")
    print(CMD_LS + "\t\t prints out remote directory content")
    print(CMD_PWD + "\t\t prints current (remote) working directory")
    print(CMD_GET + "\t\t gets remote file. GET remote_file [name_in_local_system]")
    print(CMD_PUT + "\t\t sends local file. PUT local_file [name_in_remote_system]")
    print(CMD_DELETE + "\t\t deletes remote file. DELETE [remote_file]")
    print(CMD_USER + "\t\t Send this command to begin the login process. USER [username]")
    print(CMD_CDUP + "\t\t Makes the parent of the current directory be the current directory.")
    print(CMD_HELP + "\t\t prints help FTP Client")

# Calls main function.
main()
