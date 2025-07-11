import socket
import os
from cryptography.fernet import Fernet
from tqdm import tqdm
import getpass

# Load secret key
with open('secret.key', 'rb') as key_file:
    key = key_file.read()
cipher = Fernet(key)

# Config
SERVER_HOST = '10.1.4.58'  # ← Replace with server’s IP
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

# File to send
filename = "sample_file.txt"
filesize = os.path.getsize(filename)

# Create socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

# Step 1: Ask user to enter credentials
username = input("Enter username: ")
password = getpass.getpass("Enter password: ")

# Step 2: Send credentials
client_socket.send(f"{username}{SEPARATOR}{password}".encode())

# Step 3: Wait for auth response
auth_response = client_socket.recv(BUFFER_SIZE).decode()
if auth_response != "AUTH_SUCCESS":
    print("[-] Authentication failed. Exiting.")
    client_socket.close()
    exit()

print("[+] Authentication successful.")

# Step 4: Encrypt and send filename and size
filename_encrypted = cipher.encrypt(filename.encode()).decode()
client_socket.send(f"{filename_encrypted}{SEPARATOR}{filesize}".encode())

# Step 5: Encrypt and send file content with progress bar
with open(filename, "rb") as file:
    progress = tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    while True:
        bytes_read = file.read(BUFFER_SIZE)
        if not bytes_read:
            break
        encrypted_data = cipher.encrypt(bytes_read)
        client_socket.send(encrypted_data)
        progress.update(len(bytes_read))

client_socket.close()
print(f"[+] File '{filename}' encrypted and sent successfully.")
