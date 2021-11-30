import time
import sys
import threading
import socket as s
import tkinter as tk

server_ip = ''

ip = str(input('Input server IP: '))
if ip == 'n':
    server_ip = '10.0.0.73'  # the server's  ipv4 address, i think we need to use 24.108.220.166 for over the internet


char_limit = 512                             # The amount of bytes per msg allowed
port = 8823
addr = (server_ip, port)                     # This is essentially: IP, PORT in one box for ease of use
msg_format = 'UTF-8'                         # Used when encoding and decoding msgs
run = True                                   # This was originally None, idk why it was but i changed it to True due to it being used in a while loop. I'm leaving this comment just in case, you're (possibly) welcome future me.
NU_msg = '!NEW_USR '
DC_msg = "!DC"
CC_msg = "!CC"                               # This is used in checkconn(), it means check connection... i forgot what it meant already and i doubt we want to again
client = s.socket(s.AF_INET, s.SOCK_STREAM)  # This sets the socket to Ipv4 (AF_INET) and - I believe - UDP protocol
user_list = []
global name


def send(packet):
    packet = packet.encode(msg_format)
    packet_length = len(packet)
    send_length = str(packet_length).encode(msg_format)
    send_length += b' ' * (char_limit - len(send_length))
    client.send(send_length)
    client.send(packet)


# This is used in the thread to wait for a msg from the server and update the GUI if needed
def msg_recv():
    row = 1
    while run:
        packet = client.recv(char_limit).decode(msg_format)
        if NU_msg in packet:
            new_user = packet.replace(NU_msg, '')
            user_list.insert(row, new_user)
            row += 1

        elif packet == CC_msg or packet == 'msg rcvd':
            continue

        else:
            chat_log.insert('end', packet + '\n')

        test = 'msg rcvd'
        if packet == test:
            print(packet)


# This is used to send msgs that the user inputs into the txt_entry method
def send_msg_btn():
    user_input = entry_output.get()
    global run
    if user_input != DC_msg:
        send(entry_output.get())
        chat_log.insert('end', name + user_input + '\n')
        txt_entry.delete(0, 'end')
    else:
        run = False
        send(entry_output.get())
        client.close()
        root.destroy()


# This is used to send the user's name to the server
def send_name():
    name = user_name.get()
    user_list.insert(0, name)
    connected_usrs.insert(0, name)
    name = NU_msg + name
    send(name)
    name_root.destroy()


"""""
This is where the GUI code will go ↓
"""""

root = tk.Tk()
root.geometry('664x632')
root.title('Jank Message App V2.0')
root.resizable(False, False)

# This is for when the program is first booted, it asks for users to input a name that all other users will be able to see
name_root = tk.Toplevel()
name_root.geometry('12x64')
name_root.grab_set()
name_root.attributes('-topmost', True)
label = tk.Label(name_root, text='Input Username:')
label.pack(side='top')
user_name = tk.StringVar()
input_name = tk.Entry(name_root, textvariable=user_name)
input_name.pack()

# This creates a button object for name_root() window so the user can send their chosen username to the server
send_name = tk.Button(name_root, text='Send', command=send_name)
send_name.pack(side='bottom')

# Create a container where the chat history and text entry field will go
chat_frame = tk.Frame(root, bg='red')
chat_frame.pack_propagate(0)
chat_frame.pack(fill='both', side='left', expand='True')

# Create a a Text() object to display messages from other users
chat_log = tk.Text(chat_frame, height='36')
chat_log.pack(side='top', fill='x')

# Text entry field for users to input their msgs
txt_frame = tk.Frame(chat_frame, bg='blue')
txt_frame.pack(side='bottom', padx=15, pady=4)
entry_output = tk.StringVar()
txt_entry = tk.Entry(txt_frame, textvariable=entry_output)
txt_entry.pack()

# A button to send the data in txt_entry
send_button = tk.Button(txt_frame, text='Send', command=send_msg_btn)
send_button.pack()

# Where connected users will be displayed
user_frame = tk.Frame(root, width='224', bg='blue')
user_frame.pack_propagate(0)
user_frame.pack(fill='both', side='right')

# The List of users
connected_usrs = tk.Listbox(user_frame)
connected_usrs.pack(fill='both', expand='True')


if __name__ == "__main__":

    try:
        client.connect(addr)

    except s.error as err:
        print(f'[SYSTEM] Connection failed: {err}')
        time.sleep(4)
        sys.exit()

    else:
        print('[SYSTEM] Server found. Ready to send')
        print("[SYSTEM] Starting Client thread.")
        client_thread = threading.Thread(target=msg_recv)  # This sets up the thread to be started
        client_thread.start()  # This starts the thread
        root.mainloop()
