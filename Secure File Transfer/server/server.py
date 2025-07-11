import socket
import os
from cryptography.fernet import Fernet

# Load the secret key
with open('secret.key', 'rb') as key_file:
    key = key_file.read()
cipher = Fernet(key)

# Server config
SERVER_HOST ='10.1.4.75' \
''
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

# Valid login credentials
VALID_USERNAME = "admin"
VALID_PASSWORD = "pass123"

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

while True:
    client_socket, address = server_socket.accept()
    print(f"[+] {address} connected.")

    # Step 1: Receive authentication credentials
    auth_data = client_socket.recv(BUFFER_SIZE).decode()
    username, password = auth_data.split(SEPARATOR)

    if username == VALID_USERNAME and password == VALID_PASSWORD:
        client_socket.send("AUTH_SUCCESS".encode())
        print("[+] Authentication successful.")
    else:
        client_socket.send("AUTH_FAIL".encode())
        print("[-] Authentication failed. Connection closed.")
        client_socket.close()
        continue

    # Step 2: Receive file info
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename_encrypted, filesize = received.split(SEPARATOR)
    filename = cipher.decrypt(filename_encrypted.encode()).decode()
    filesize = int(filesize)

    encrypted_data = b""
    while True:
        chunk = client_socket.recv(BUFFER_SIZE)
        if not chunk:
            break
        encrypted_data += chunk

    decrypted_data = cipher.decrypt(encrypted_data)

    with open(f"received_{filename}", "wb") as file:
        file.write(decrypted_data)

    client_socket.close()
    print(f"[+] File '{filename}' received and decrypted successfully.")
