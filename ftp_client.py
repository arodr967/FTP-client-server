# FTP Client
# Contributed by L.A.A.M.
# ********************************************************************************
# **                   **
# ** References                                                                 **
# ** http://www.slacksite.com/other/ftp.html#active                             **
# ** https://www.ietf.org/rfc/rfc959.txt                                        **
# ** Computer-Networking Top-Down Approach 6th Edition by Kurose and Ross       **
# ** computer ftp client                                                        **
# **                                                                            **
# ** Tested with inet.cis.fiu.edu  -- FIXED Port 21                             **
# ** Commands are not case sensitive                                            **
# **                                                                            **
# ** Built for Python 2.7.x. FTP Client Active Mode Only                        **
# ** Usage: Python ftp.py hostname [username] [password]                        **
# ** username and password are optional when invoking ftp.py                    **
# ** if not supplied, use command LOGIN                                         **
# ** Inside of ftp client, you can type HELP for more information               **
# ********************************************************************************

# import necessary packages.
import os
import os.path
import sys
from socket import *

# Global constants
USAGE = "usage: Python ftp hostname [username] [password]"

RECV_BUFFER = 1024
FTP_PORT = 21

# TODO: Server Commands

# Commands
# TODO: Remove the server commands and add the client commands
CMD_QUIT = "QUIT"
CMD_HELP = "HELP"
CMD_LOGIN = "LOGIN"
CMD_LOGOUT = "LOGOUT"
CMD_LS = "LS"
CMD_PWD = "PWD"
CMD_PORT = "PORT"
CMD_DELETE = "DELETE"
CMD_PUT = "PUT"
CMD_GET = "GET"
CMD_USER = "USER"
CMD_PASS = "PASS"
CMD_CWD = "CWD"
CMD_CDUP = "CDUP"
CMD_MKD = "MKD"
CMD_STOU = "STOU"
CMD_RNFR = "RNFR"
CMD_RNTO = "RNTO"
CMD_RMD = "RMD"
CMD_NOOP = "NOOP"
CMD_TYPE = "TYPE"

# TODO: Implement commands

# CMD_PORT = "PORT"
CMD_STOR = "STOR"
CMD_RETR = "RETR"
CMD_APPE = "APPE"


CMD_ABOR = "ABOR"  # (Only required if doing multi-threading ftp client for extra credit)


# The data port starts at high number (to avoid privileges port 1-1024)
# the ports ranges from MIN to MAX
DATA_PORT_MAX = 61000
DATA_PORT_MIN = 60020
# data back log for listening.
DATA_PORT_BACKLOG = 1

# global variables
# store the next_data_port use in a formula to obtain
# a port between DATA_POR_MIN and DATA_PORT_MAX
next_data_port = 1


# entry point main()
def main():
    hostname = "cnt4713.cis.fiu.edu"
    username = ""
    password = ""

    logged_on = False
    logon_ready = False
    print("FTP Client v1.0")
    if len(sys.argv) < 2:
        print(USAGE)
    if len(sys.argv) == 2:
        hostname = sys.argv[1]
    if len(sys.argv) == 4:
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
    ftp_code = ftp_recv[:3]
    #
    # note that in the program there are many .strip('\n')
    # this is to avoid an extra line from the message
    # received from the ftp server.
    # an alternative is to use sys.stdout.write
    msg = ftp_recv.decode()
    print(msg.strip('\n'))

    # sys.stdout.write(ftp_recv)

    # this is the only time that login is called
    # without relogin
    # otherwise, relogin must be called, which included prompts
    # for username
    #
    if (logon_ready):
        logged_on = login(username, password, ftp_socket)

    keep_running = True

    while keep_running:
        rinput = input("FTP>> ")
        tokens = rinput.split()
        # just in case a user types lowercase
        # the command (for example login is converted to LOGIN)
        cmd = tokens[0].upper()
        if cmd == CMD_USER:
            username, ftp_socket \
                = user_ftp(username, tokens, ftp_socket, hostname)

        if cmd == CMD_PASS:
            password, logged_on, ftp_socket \
                = pass_ftp(password, tokens, ftp_socket, hostname, logged_on)

        if cmd == CMD_QUIT:
            quit_ftp(logged_on, ftp_socket)

        if cmd == CMD_HELP:
            help_ftp()

        if cmd == CMD_PWD:
            pwd_ftp(ftp_socket)

        if cmd == CMD_CWD:
            cwd_ftp(tokens, ftp_socket)

        if cmd == CMD_CDUP:
            cdup_ftp(ftp_socket)

        if cmd == CMD_MKD:
            mkd_ftp(tokens, ftp_socket)

        if cmd == CMD_RMD:
            rmd_ftp(tokens, ftp_socket)

        if cmd == CMD_STOU:
            stou_ftp(ftp_socket)

        if cmd == CMD_RNFR:
            rnfr_ftp(tokens, ftp_socket)

        if cmd == CMD_RNTO:
            rnto_ftp(tokens, ftp_socket)

        if cmd == CMD_NOOP:
            noop_ftp(ftp_socket)

        if cmd == CMD_TYPE:
            type_ftp(tokens, ftp_socket)

        if cmd == CMD_LS:
            # FTP must create a channel to received data before
            # executing ls.
            # also makes sure that data_socket is valid
            # in other words, not None
            data_socket = ftp_new_dataport(ftp_socket)
            if data_socket is not None:
                ls_ftp(tokens, ftp_socket, data_socket)
            else:
                print("[LS] Failed to get data port. Try again.")

        if cmd == CMD_STOR:
            # FTP must create a channel to received data before
            # executing stor.
            # also makes sure that data_socket is valid
            # in other words, not None
            data_socket = ftp_new_dataport(ftp_socket)
            if data_socket is not None:
                stor_ftp(tokens, ftp_socket)
            else:
                print("[STOR] Failed to get data port. Try again.")

        if cmd == CMD_LOGIN:
            username, password, logged_on, ftp_socket \
                = relogin(username, password, logged_on, tokens, hostname, ftp_socket)

        if cmd == CMD_LOGOUT:
            logged_on, ftp_socket = logout(logged_on, ftp_socket)

        if cmd == CMD_DELETE:
            delete_ftp(tokens, ftp_socket)

        if cmd == CMD_PUT:
            # FTP must create a channel to received data before
            # executing put.
            # also makes sure that data_socket is valid
            # in other words, not None
            data_socket = ftp_new_dataport(ftp_socket)
            if data_socket is not None:
                put_ftp(tokens, ftp_socket, data_socket)
            else:
                print("[PUT] Failed to get data port. Try again.")

        if cmd == CMD_GET:
            # FTP must create a channel to received data before
            # executing get.
            # also makes sure that data_socket is valid
            # in other words, not None
            data_socket = ftp_new_dataport(ftp_socket)
            if data_socket is not None:
                get_ftp(tokens, ftp_socket, data_socket)
            else:
                print("[GET] Failed to get data port. Try again.")

    # print ftp_recv
    ftp_socket.close()
    print("Thank you for using FTP 1.0")
    sys.exit()


def ftp_connecthost(hostname):
    ftp_socket = socket(AF_INET, SOCK_STREAM)
    # to reuse socket faster. It has very little consequence for ftp client.
    ftp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    ftp_socket.connect((hostname, FTP_PORT))

    return ftp_socket


def ftp_new_dataport(ftp_socket):
    global next_data_port
    dport = next_data_port
    host = gethostname()
    host_address = gethostbyname(host)
    next_data_port = next_data_port + 1  # for next next
    dport = (DATA_PORT_MIN + dport) % DATA_PORT_MAX

    print("Preparing Data Port: " + host + " " + host_address + " " + str(dport))
    data_socket = socket(AF_INET, SOCK_STREAM)
    # reuse port
    data_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    data_socket.bind((host_address, dport))
    data_socket.listen(DATA_PORT_BACKLOG)

    # the port requires the following
    # PORT IP PORT
    # however, it must be transmitted like this.
    # PORT 192,168,1,2,17,24
    # where the first four octet are the ip and the last two form a port number.
    host_address_split = host_address.split('.')
    high_dport = str(dport // 256)  # get high part
    low_dport = str(dport % 256)  # similar to dport << 8 (left shift)
    port_argument_list = host_address_split + [high_dport, low_dport]
    port_arguments = ','.join(port_argument_list)
    print(CMD_PORT + ' ' + port_arguments)

    try:
        ftp_socket.send((CMD_PORT + ' ' + port_arguments + '\r\n').encode())
    except socket.timeout:
        print("Socket timeout. Port may have been used recently. wait and try again!")
        return None
    except socket.error:
        print("Socket error. Try again")
        return None
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))
    return data_socket


def noop_ftp(ftp_socket):
    ftp_socket.send("NOOP\n".encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))


def pwd_ftp(ftp_socket):
    ftp_socket.send("PWD\n".encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))


def cwd_ftp(tokens, ftp_socket):

    if len(tokens) < 2:
        print("CWD requires 1 argument. CWD [remote-directory]")
        remote_directory = input("Remote directory: ")
    else:
        remote_directory = tokens[1]

    ftp_socket.send(("CWD " + remote_directory + "\n").encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))


def cdup_ftp(ftp_socket):
    ftp_socket.send("CDUP\n".encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))


def mkd_ftp(tokens, ftp_socket):

    if len(tokens) < 2:
        print("MKD requires 1 argument. MKD [remote-directory]")
        remote_directory = input("Remote directory: ")
    else:
        remote_directory = tokens[1]

    ftp_socket.send(("MKD " + remote_directory + "\n").encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))


def rmd_ftp(tokens, ftp_socket):

    if len(tokens) < 2:
        print("RMD requires 1 argument. RMD [remote-directory]")
        remote_directory = input("Remote directory: ")
    else:
        remote_directory = tokens[1]

    ftp_socket.send(("RMD " + remote_directory + "\n").encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))


def type_ftp(tokens, ftp_socket):

    TYPE_ASCII = "A"
    TYPE_IMAGE = "I"

    if len(tokens) < 2:
        print("TYPE requires at least 1 argument. TYPE [type-character]")
        type_character = input("Type character: ").upper()
    else:
        type_character = tokens[1].upper()

    if type_character == TYPE_ASCII:

        SECOND_TYPE_NON_PRINT = "N"
        SECOND_TYPE_TELNET = "T"
        SECOND_TYPE_ASA = "C"

        if len(tokens) == 3:
            second_type_character = tokens[2].upper()

            if second_type_character == SECOND_TYPE_NON_PRINT:

                ftp_socket.send(("TYPE " + TYPE_ASCII + " " + SECOND_TYPE_NON_PRINT + "\n").encode())
                msg = (ftp_socket.recv(RECV_BUFFER)).decode()
                print(msg.strip('\n'))

            elif second_type_character == SECOND_TYPE_TELNET:

                ftp_socket.send(("TYPE " + TYPE_ASCII + " " + SECOND_TYPE_TELNET + "\n").encode())
                msg = (ftp_socket.recv(RECV_BUFFER)).decode()
                print(msg.strip('\n'))

            elif second_type_character == SECOND_TYPE_ASA:

                ftp_socket.send(("TYPE " + TYPE_ASCII + " " + SECOND_TYPE_ASA + "\n").encode())
                msg = (ftp_socket.recv(RECV_BUFFER)).decode()
                print(msg.strip('\n'))

            else:
                print(second_type_character + " second-type-character is not supported for type-character " + TYPE_ASCII)

        # This is the default if second-type-character is omitted.
        else:
            ftp_socket.send(("TYPE " + TYPE_ASCII + " " + SECOND_TYPE_NON_PRINT + "\n").encode())
            msg = (ftp_socket.recv(RECV_BUFFER)).decode()
            print(msg.strip('\n'))

    elif type_character == TYPE_IMAGE:

        ftp_socket.send(("TYPE " + TYPE_IMAGE + "\n").encode())
        msg = (ftp_socket.recv(RECV_BUFFER)).decode()
        print(msg.strip('\n'))

    else:
        print(type_character + " type-character is not supported.")


def stou_ftp(ftp_socket):
    ftp_socket.send("STOU\n".encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))


def rnfr_ftp(tokens, ftp_socket):

    if len(tokens) < 2:
        print("RNFR requires 1 argument. RNFR [from-filename]")
        from_filename = input("From filename: ")
    else:
        from_filename = tokens[1]

    ftp_socket.send(("RNFR " + from_filename + "\n").encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()

    print(msg.strip('\n'))


def rnto_ftp(tokens, ftp_socket):

    if len(tokens) < 2:
        print("RNTO requires 1 argument. RNTO [to-filename]")
        to_filename = input("To filename: ")
    else:
        to_filename = tokens[1]

    ftp_socket.send(("RNTO " + to_filename + "\n").encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    tokens = msg.split()

    if tokens[0] == "503":
        print("You need to specify which file you want to rename. Use the RNFR [from-filename] command first.")

    print(msg.strip('\n'))


def get_ftp(tokens, ftp_socket, data_socket):
    if len(tokens) < 2:
        print("get [filename]. Please specify filename")
        return

    remote_filename = tokens[1]
    if len(tokens) == 3:
        filename = tokens[2]
    else:
        filename = remote_filename

    ftp_socket.send(("RETR " + remote_filename + "\n").encode())

    print("Attempting to write file. Remote: " + remote_filename + " - Local:" + filename)

    msg = ftp_socket.recv(RECV_BUFFER).decode()
    tokens = msg.split()
    if tokens[0] != "150":
        print("Unable to retrieve file. Check that file exists (ls) or that you have permissions")
        return

    print(msg.strip('\n'))

    data_connection, data_host = data_socket.accept()
    file_bin = open(filename, "wb")  # read and binary modes

    size_recv = 0
    sys.stdout.write("|")
    while True:
        sys.stdout.write("*")
        data = data_connection.recv(RECV_BUFFER)

        if not data or data == '' or len(data) <= 0:
            file_bin.close()
            break
        else:
            file_bin.write(data)
            size_recv += len(data)

    sys.stdout.write("|")
    sys.stdout.write("\n")

    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER).decode()
    print(msg.strip('\n'))


def put_ftp(tokens, ftp_socket, data_socket):
    if len(tokens) < 2:
        print("put [filename]. Please specify filename")
        return

    local_filename = tokens[1]
    if len(tokens) == 3:
        filename = tokens[2]
    else:
        filename = local_filename

    if os.path.isfile(local_filename) == False:
        print("Filename does not exist on this client. Filename: " + filename + " -- Check file name and path")
        return
    filestat = os.stat(local_filename)
    filesize = filestat.st_size

    ftp_socket.send(("STOR " + filename + "\n").encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))

    print("Attempting to send file. Local: " + local_filename + " - Remote:" + filename + " - Size:" + str(filesize))

    data_connection, data_host = data_socket.accept()
    file_bin = open(filename, "rb")  # read and binary modes

    size_sent = 0
    # use write so it doesn't produce a new line (like print)
    sys.stdout.write("|")
    while True:
        sys.stdout.write("*")
        data = file_bin.read(RECV_BUFFER)
        if not data or data == '' or len(data) <= 0:
            file_bin.close()
            break
        else:
            data_connection.send(data)
            size_sent += len(data)

    sys.stdout.write("|")
    sys.stdout.write("\n")

    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER).decode()
    print(msg.strip('\n'))


def ls_ftp(tokens, ftp_socket, data_socket):
    if len(tokens) > 1:
        ftp_socket.send(("LIST " + tokens[1] + "\n").encode())
    else:
        ftp_socket.send("LIST\n".encode())

    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))

    data_connection, data_host = data_socket.accept()

    msg = data_connection.recv(RECV_BUFFER).decode()
    while len(msg) > 0:
        print(msg.strip('\n'))
        msg = data_connection.recv(RECV_BUFFER)

    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER).decode()
    print(msg.strip('\n'))


def stor_ftp(tokens, ftp_socket):
    if len(tokens) < 2:
        print("STOR requires 1 argument. STOR [remote-filename]")
        remote_filename = input("Remote filename: ")
    else:
        remote_filename = tokens[1]

    ftp_socket.send(("STOR " + remote_filename + "\n").encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))


def delete_ftp(tokens, ftp_socket):
    if len(tokens) < 2:
        print("You must specify a file to delete")
    else:
        print("Attempting to delete " + tokens[1])
        ftp_socket.send(("DELE " + tokens[1] + "\n").encode())

    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))


def logout(lin, ftp_socket):
    if ftp_socket is None:
        print("Your connection was already terminated.")
        return False, ftp_socket

    if lin == False:
        print("You are not logged in. Logout command will be send anyways")

    print("Attempting to logged out")
    msg = ""
    try:
        ftp_socket.send("QUIT\n".encode())
        msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    except socket.error:
        print("Problems logging out. Try logout again. Do not login if you haven't logged out!")
        return False
    print(msg.strip('\n'))
    ftp_socket = None
    return False, ftp_socket  # it should only be true if logged in and not able to logout


def quit_ftp(lin, ftp_socket):
    print("Quitting...")
    logged_on, ftp_socket = logout(lin, ftp_socket)
    print("Thank you for using FTP")
    try:
        if ftp_socket is not None:
            ftp_socket.close()
    except socket.error:
        print("Socket was not able to be close. It may have been closed already")
    sys.exit()


def relogin(username, password, logged_on, tokens, hostname, ftp_socket):
    if len(tokens) < 3:
        print("LOGIN requires 2 arguments. LOGIN [username] [password]")
        print("You will be prompted for username and password now")
        username = input("Username: ")
        password = input("Password: ")
    else:
        username = tokens[1]
        password = tokens[2]

    if ftp_socket is None:
        ftp_socket = ftp_connecthost(hostname)
        ftp_recv = ftp_socket.recv(RECV_BUFFER).decode()
        print(ftp_recv.strip('\n'))

    logged_on = login(username, password, ftp_socket)
    return username, password, logged_on, ftp_socket


def user_ftp(username, tokens, ftp_socket, hostname):
    print("Beginning login process \n")

    if ftp_socket is None:
        ftp_socket = ftp_connecthost(hostname)
        ftp_recv = ftp_socket.recv(RECV_BUFFER).decode()
        print(ftp_recv.strip('\n'))

    if len(tokens) < 2:
        print("USER requires 1 argument. USER [username]")
        print("You will be prompted for username now")
        username = input("User: ")
    else:
        username = tokens[1]

    ftp_socket.send(("USER " + username + "\n").encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))

    return username, ftp_socket


def pass_ftp(password, tokens, ftp_socket, hostname, logged_on):
    print("Continuing login process \n")

    if len(tokens) < 2:
        print("PASS requires 1 argument. PASS [password]")
        print("You will be prompted for password now")
        password = input("Password: ")
    else:
        password = tokens[1]

    ftp_socket.send(("PASS " + password + "\n").encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    tokens = msg.split()
    print(msg.strip('\n'))

    if ftp_socket is None:
        ftp_socket = ftp_connecthost(hostname)
        ftp_recv = ftp_socket.recv(RECV_BUFFER).decode()
        print(ftp_recv.strip('\n'))

    if len(tokens) > 0 and tokens[0] != "230":
        print("Not able to login. Please check your username or password. Try again!")
        logged_on = False
    else:
        logged_on = True

    return password, logged_on, ftp_socket


def login(user, passw, ftp_socket):
    if user == None or user.strip() == "":
        print("Username is blank. Try again")
        return False;

    print("Attempting to login user " + user)
    # send command user
    ftp_socket.send(("USER " + user + "\n").encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    print(msg.strip('\n'))
    ftp_socket.send(("PASS " + passw + "\n").encode())
    msg = (ftp_socket.recv(RECV_BUFFER)).decode()
    tokens = msg.split()
    print(msg.strip('\n'))
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
    print(CMD_NOOP + "\t\t Does nothing except return a response.")
    print(CMD_LOGIN + "\t\t Login. It expects username and password. LOGIN [username] [password]")
    print(CMD_LOGOUT + "\t\t Logout from ftp but not client")
    print(CMD_LS + "\t\t prints out remote directory content")
    print(CMD_PWD + "\t\t prints current (remote) working directory")
    print(CMD_GET + "\t\t gets remote file. GET remote_file [name_in_local_system]")
    print(CMD_PUT + "\t\t sends local file. PUT local_file [name_in_remote_system]")
    print(CMD_DELETE + "\t\t deletes remote file. DELETE [remote_file]")
    print(CMD_USER + "\t\t Send this command to begin the login process. USER [username]")
    print(CMD_PASS + "\t\t After sending the USER command,"
                     " send this command to complete the login process. PASS [password]")
    print(CMD_CWD + "\t\t Makes the given directory be the current directory on the remote host. CWD [remote-directory]")
    print(CMD_CDUP + "\t\t Makes the parent of the current directory be the current directory.")
    print(CMD_MKD + "\t\t Creates the named directory on the remote host. MKD [remote-directory]")
    print(CMD_RMD + "\t\t Deletes the named directory on the remote host. RMD [remote-directory]")
    print(CMD_STOU + "\t\t Begins transmission of a file to the remote site;"
                     " the remote filename will be unique in the current directory.")
    print(CMD_RNFR + "\t\t Used when renaming a file. Specify the file to be renamed;"
                     " follow it with an RNTO command to specify the new name for the file."
                     " RNFR [from-filename]")
    print(CMD_RNTO + "\t\t Used when renaming a file. After sending an RNFR command to specify the file to rename,"
                     " send this command to specify the new name for the file. RNTO [to-filename]")
    print(CMD_TYPE + "\t\t Sets the type of file to be transferred. "
                     "ASCII and Image only supported. Second-type-character is optional. "
                     "TYPE [type-character] [second-type-character]")
    print(CMD_HELP + "\t\t prints help FTP Client")

# Calls main function.
main()
