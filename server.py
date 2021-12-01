import socket as s
import threading
import time


CHAR_LIMIT = 512                             # The amount of bytes per msg allowed
PORT = 8823
SERVER_IP = '10.0.0.73'                      # the server's  ipv4 address, i think we need to use 24.108.220.166 for over the internet
ip_port = (SERVER_IP, PORT)                  # This is essentially: IP, PORT in one box for ease of use
MSG_FORMAT = 'UTF-8'             # Used when encoding and decoding msgs
DC_msg = "!DC"
CC_msg = "!CC"                               # This is used in checkconn(), it means check connection... i forgot what it meant already and i doubt we want to again
NU_msg = '!NEW_USR '
server = s.socket(s.AF_INET, s.SOCK_STREAM)  # This sets the socket to Ipv4 (AF_INET) and, I believe, UDP protocol
server.bind(ip_port)                         # Binds the socket to addr, making anything that hits port 9882 go to the socket. I think that's how it works
usr_dic = {}
usr = ''


# This function is to check if the client is till alive.
def client_alive(conn, addr):
    s.setdefaulttimeout(1)
    for c in usr_dic:
        conn.sendto(CC_msg.encode(MSG_FORMAT), c)
        try:
            conn.recv(CHAR_LIMIT).decode(MSG_FORMAT)
        except s.error as err:
            print(f'\n[SYSTEM] Client_alive error: {err}\n')
            usr_dic.pop(addr)
            print(usr_dic)
        s.setdefaulttimeout(None)


# This function handles the client/server connections
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")

    connected = True
    while connected:

        # I think this receives msgs that are the HEADER length only then decodes it using FORMAT
        global usr
        packet_length = conn.recv(CHAR_LIMIT).decode(MSG_FORMAT)
        if packet_length:
            packet_length = len(packet_length)
            packet = conn.recv(packet_length).decode(MSG_FORMAT)

            # This is for adding new users to the usr_dic list (list of all known users)
            if NU_msg in packet:
                print(f'\npacket = {packet}\n')
                # This trims the packet of useless data so it fits better into the dictionary, the name is all this is left
                usr = packet.replace(NU_msg, '')
                usr_dic[addr] = usr
                print(f"[SYSTEM] New User Added:{usr} {addr}")
                print(usr_dic.values())

            # If the package is !DC, close the connection
            if DC_msg in packet:
                connected = False
                # This removes the user from the usr_dic
                usr_dic.pop(addr)
                print(usr_dic)
                print(f"[SYSTEM] User [{usr}] Disconnected\n [ACTIVE CONNECTIONS] {threading.active_count() - 2}")

            # If the packet contains DC_msg or CC_msg dont print, if not, print it
            if packet != DC_msg and packet != CC_msg and packet != NU_msg:
                print(f"{usr_dic[addr]}: {packet}")

                #client_alive(conn, addr)
                time.sleep(1)

    conn.close()


def start():
    server.listen()
    print("[SERVER] Listening...")

    while True:

        # addr is the address associated with the connection, conn is a socket object used to send a recieve packets
        # from the associated address
        conn, addr = server.accept()

        # This creates a new thread using handle_client(), starts the thread and then prints out active connections - 1
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == '__main__':
    print("[SERVER] Starting...")
    start_server = threading.Thread(target=start())
    start_server.start()
