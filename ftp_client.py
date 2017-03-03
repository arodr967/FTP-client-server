from socket import *
import os
import os.path
import errno
import traceback
import sys


# Global constants
USAGE = "usage: Python ftp hostname [username] [password]"

RECV_BUFFER = 1024

# My Port
FTP_PORT = 2129
# FTP_PORT = 21

# Commands

CMD_QUIT = "QUIT"
CMD_BYE = "BYE"
CMD_EXIT = "EXIT"
CMD_HELP = "HELP"
CMD_LOGIN = "LOGIN"
CMD_LOGOUT = "LOGOUT"
CMD_LS = "LS"
CMD_DIR = "DIR"
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
CMD_BINARY = "BINARY"
CMD_SUNIQUE = "SUNIQUE"
CMD_PORT = "PORT"
CMD_DISCONNECT = "DISCONNECT"
CMD_CLOSE = "CLOSE"
CMD_NOOP = "NOOP"
CMD_LCD = "LCD"

# TODO

CMD_OPEN = "OPEN"
CMD_FTP = "FTP"
CMD_APPEND = "APPEND"
CMD_RHELP = "RHELP"
CMD_TYPE = "TYPE"
CMD_VERBOSE = "VERBOSE"
CMD_DEBUG = "DEBUG"
CMD_LLS = "LLS"
CMD_LPWD = "LPWD"
CMD_USAGE = "USAGE"

# The data port starts at high number (to avoid privileges port 1-1024)
# the ports ranges from MIN to MAX
# My data ports
DATA_PORT_MAX = 34999
DATA_PORT_MIN = 34500

# DATA_PORT_MAX = 61000
# DATA_PORT_MIN = 60020

# data back log for listening.
DATA_PORT_BACKLOG = 1

# global variables
# store the next_data_port use in a formula to obtain
# a port between DATA_POR_MIN and DATA_PORT_MAX
next_data_port = 1

hostname = "cnt4713.cs.fiu.edu"
username = ""
password = ""
sunique = False
current_directory = os.path.abspath(".")
base_directory = os.path.abspath("/")
type = "A"


# entry point main()
def main():

    global username
    global password
    global hostname

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
    ftp_recv = ftp_socket.recv(RECV_BUFFER)
    print(str_msg_decode(ftp_recv))

    if logon_ready:
        logged_on = login(username, password, ftp_socket)

    keep_running = True

    while keep_running:
        try:
            user_input = input("ftp> ")

            if user_input is None or user_input.strip() == "":
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
    except OSError as e:
        print("Socket error:", e)
    sys.exit()


def run_commands(tokens, logged_on, ftp_socket):

    global username
    global password
    global hostname

    cmd = tokens[0].upper()

    if cmd == CMD_QUIT or cmd == CMD_BYE or cmd == CMD_EXIT:
        quit_ftp(logged_on, ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == "!":
        ftp_socket.close()
        sys.exit()
        return "", logged_on, ftp_socket

    if cmd == CMD_HELP or cmd == "?":
        help_ftp()
        return "", logged_on, ftp_socket

    if cmd == CMD_RHELP:
        rhelp_ftp()
        return "", logged_on, ftp_socket

    if cmd == CMD_NOOP:
        noop_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_PWD:
        pwd_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_CD:
        cd_ftp(tokens, ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_LCD:
        lcd_ftp(tokens)
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

    if cmd == CMD_SUNIQUE:
        sunique_ftp()
        return "", logged_on, ftp_socket

    if cmd == CMD_RENAME:
        rename_ftp(tokens, ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_ASCII:
        ascii_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_IMAGE or cmd == CMD_BINARY:
        image_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if cmd == CMD_APPEND:
        data_socket = ftp_new_dataport(ftp_socket)
        if data_socket is not None:
            get_ftp(tokens, ftp_socket, data_socket)
            return "", logged_on, ftp_socket
        else:
            return "[GET] Failed to get data port. Try again.", logged_on, ftp_socket

    if cmd == CMD_LS or cmd == CMD_DIR:
        data_socket = ftp_new_dataport(ftp_socket)
        if data_socket is not None:
            ls_ftp(tokens, ftp_socket, data_socket)
            return "", logged_on, ftp_socket
        else:
            return "[LS] Failed to get data port. Try again.", logged_on, ftp_socket

    if cmd == CMD_LOGIN or cmd == CMD_USER:
        logged_on = user_ftp(username, password, tokens, ftp_socket, hostname)
        return "", logged_on, ftp_socket

    if cmd == CMD_LOGOUT or cmd == CMD_CLOSE or cmd == CMD_DISCONNECT:
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


def noop_ftp(ftp_socket):

    ftp_socket.send(str_msg_encode("NOOP\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))


def pwd_ftp(ftp_socket):

    ftp_socket.send(str_msg_encode("PWD\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    sys.stdout.write(str_msg_decode(msg, True))


def lcd_ftp(tokens):
    global current_directory
    global base_directory

    if len(tokens) is 2:
        local_directory = tokens[1]
    else:
        local_directory = ""

    if local_directory == "":
        print("Local directory now " + current_directory)
        return

    if local_directory == "/":
        current_directory = base_directory
        print("Local directory now " + current_directory)
    elif local_directory[0] == "/":
        path = os.path.join(base_directory, local_directory[1:])

        if os.path.exists(path):
            current_directory = path
            print("Local directory now " + current_directory)
        else:
            print("local: " + local_directory[1:] + ": No such file or directory")
    else:
        path = os.path.join(current_directory, local_directory)

        if os.path.exists(path):
            current_directory = path
            print("Local directory now " + current_directory)
        else:
            print("local: " + local_directory + ": No such file or directory")


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


def sunique_ftp():

    global sunique
    sunique = not sunique

    if sunique:
        print("Store unique on.")
    else:
        print("Story unique off.")


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

    global sunique

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

    if not sunique:
        ftp_socket.send(str_msg_encode("STOR " + remote_file + "\n"))
    else:
        ftp_socket.send(str_msg_encode("STOU " + remote_file + "\n"))

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

        if remote_file is "":
            print("usage: delete remote-file")
            return
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


def logout(logged_on, ftp_socket):

    if ftp_socket is None or logged_on is False:
        print("Not connected.")
        return False, ftp_socket

    try:
        ftp_socket.send(str_msg_encode("QUIT\n"))
        msg = ftp_socket.recv(RECV_BUFFER)
        sys.stdout.write(str_msg_decode(msg, True))
        ftp_socket = None
    except socket.error:
        print("Error logging out. Try logout again. Do not login if you haven't logged out!")
        return False

    return False, ftp_socket


def quit_ftp(logged_on, ftp_socket):

    logged_on, ftp_socket = logout(logged_on, ftp_socket)

    try:
        if ftp_socket is not None:
            ftp_socket.close()
    except socket.error:
        print("Socket was not able to be close. It may have been closed already")
    sys.exit()


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
        return

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
        return False
    else:
        return True


def login(username, password, ftp_socket):

    global hostname

    if username is None or username.strip() is "":
        username = input("Name (" + hostname + "): ")

    ftp_socket.send(str_msg_encode("USER " + username + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(str_msg_decode(msg, True))

    if password is None or password.strip() is "":
        password = input("Password: ")

    ftp_socket.send(str_msg_encode("PASS " + password + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(str_msg_decode(msg, True))

    str_value = str_msg_decode(msg, False)
    tokens = str_value.split()

    if len(tokens) > 0 and tokens[0] != "230":
        print("Login failed.")
        return False
    else:
        return True


def help_ftp():
    # TODO: Accept 1 argument which which will give a brief description of selected command.

    print("Commands may be abbreviated.  Commands are:\n\n"
          "!		dir		    mdelete \n"
          "?		disconnect	mdir    \n"
          "exit		put         type    \n"
          "append	mkdir		pwd     \n"
          "ascii	get			quit    \n"
          "sunique  binary      recv    \n"
          "bye		help        debug   \n"
          "cd		image		rhelp   \n"
          "cdup		rename		user    \n"
          "close	open		verbose \n"
          "lcd		rmdir		delete  \n"
          "ls                           \n")


def rhelp_ftp():
    # TODO: Accept 1 argument which which will give a brief description of selected command.

    print("214-The following commands are recognized (* =>'s unimplemented):\n"
          "214-CWD     XCWD*   CDUP    XCUP*   SMNT*   QUIT    PORT    PASV*)\n"
          "214-EPRT*   EPSV*   ALLO*   RNFR    RNTO    DELE    MDTM*   RMD\n"
          "214-XRMD*   MKD     XMKD*   PWD     XPWD*   SIZE*   SYST*   HELP\n"
          "214-NOOP    FEAT*   OPTS*   AUTH*   CCC*    CONF*   ENC*    MIC*\n"
          "214-PBSZ*   PROT*   TYPE    STRU*   MODE*   RETR    STOR    STOU\n"
          "214-APPE    REST*   ABOR*   USER    PASS    ACCT*   REIN*   LIST\n"
          "214-NLST*   STAT*   SITE*   MLSD*   MLST*\n"
          "214 Direct comments to arodr967@fiu.edu")

# Calls main function.
main()
