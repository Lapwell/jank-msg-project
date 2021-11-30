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
user_dic = {'Test': "User"}
usr = ''


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
            packet_length = int(packet_length)
            packet = conn.recv(packet_length).decode(MSG_FORMAT)

            if NU_msg in packet:
                print(f'\npacket = {packet}\n')
                usr = packet.replace(NU_msg, '')
                user_dic[addr] = usr
                print("[SYSTEM] New User Added:", f"{usr}", f"{addr}")
                usr_name_data = user_dic.values()
                print(usr_name_data)

            # If the package is !DC, close the connection
            if DC_msg in packet:
                connected = False
                del user_dic[addr]
                print(f"[SYSTEM] User [{user_dic[addr]}] Disconnected\n [ACTIVE CONNECTIONS] {threading.active_count() - 2}")

            # If the packet contains !DC don't print, if not, print it
            if packet != DC_msg:
                print(f"{user_dic[addr]}: {packet}")
                conn.send(CC_msg.encode(MSG_FORMAT))
                test = 'msg rcvd'
                conn.send(test.encode(MSG_FORMAT))
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
