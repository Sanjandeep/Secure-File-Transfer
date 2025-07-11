import socket
import os
import threading
from tkinter import Tk, Text, Scrollbar, Button, Label, END, RIGHT, Y, LEFT, BOTH
from cryptography.fernet import Fernet

# Load the secret key
with open('secret.key', 'rb') as key_file:
    key = key_file.read()
cipher = Fernet(key)

# Config
SERVER_HOST = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

VALID_USERNAME = "admin"
VALID_PASSWORD = "pass123"

class ServerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Secure File Transfer Server")
        self.master.geometry("600x400")

        Label(master, text="Server Log", font=("Arial", 14)).pack(pady=5)

        self.log_box = Text(master, wrap="word")
        self.scroll = Scrollbar(master, command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=self.scroll.set)

        self.scroll.pack(side=RIGHT, fill=Y)
        self.log_box.pack(side=LEFT, fill=BOTH, expand=True)

        Button(master, text="Start Server", command=self.start_server_thread).pack(pady=10)

    def log(self, message):
        self.log_box.insert(END, message + "\n")
        self.log_box.see(END)

    def start_server_thread(self):
        thread = threading.Thread(target=self.start_server, daemon=True)
        thread.start()

    def start_server(self):
        self.log(f"[*] Starting server on {SERVER_HOST}:{SERVER_PORT}")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(5)
        self.log("[*] Waiting for incoming connections...")

        while True:
            client_socket, address = server_socket.accept()
            self.log(f"[+] Connected from {address}")

            try:
                # Step 1: Auth
                auth_data = client_socket.recv(BUFFER_SIZE).decode()
                username, password = auth_data.split(SEPARATOR)
                if username != VALID_USERNAME or password != VALID_PASSWORD:
                    self.log("[-] Authentication failed.")
                    client_socket.send("AUTH_FAILED".encode())
                    client_socket.close()
                    continue
                client_socket.send("AUTH_SUCCESS".encode())
                self.log(f"[+] Authenticated user: {username}")

                # Step 2: Metadata
                received = client_socket.recv(BUFFER_SIZE).decode()
                filename_encrypted, encrypted_size = received.split(SEPARATOR)
                filename = cipher.decrypt(filename_encrypted.encode()).decode()
                encrypted_size = int(encrypted_size)
                self.log(f"[+] Receiving file: {filename} ({encrypted_size} bytes encrypted)")

                # Step 3: Receive file
                encrypted_data = b""
                while len(encrypted_data) < encrypted_size:
                    chunk = client_socket.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    encrypted_data += chunk

                self.log(f"[+] Received {len(encrypted_data)} bytes.")

                # Step 4: Decrypt and save
                try:
                    decrypted_data = cipher.decrypt(encrypted_data)
                    saved_path = f"received_{filename}"
                    with open(saved_path, "wb") as f:
                        f.write(decrypted_data)
                    self.log(f"[+] File saved as {saved_path}")
                except Exception as e:
                    self.log(f"[-] Decryption failed: {e}")

            except Exception as e:
                self.log(f"[-] Error: {str(e)}")

            client_socket.close()


if __name__ == "__main__":
    root = Tk()
    app = ServerGUI(root)
    root.mainloop()
