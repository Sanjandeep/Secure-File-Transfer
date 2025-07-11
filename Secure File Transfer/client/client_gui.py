import socket
import os
from tkinter import Tk, Label, Button, filedialog, messagebox, simpledialog
from cryptography.fernet import Fernet
from tqdm import tqdm

# Load secret key
with open('secret.key', 'rb') as key_file:
    key = key_file.read()
cipher = Fernet(key)

# Configuration
SERVER_HOST = '192.168.109.158'  
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

class FileTransferClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Secure File Transfer Client")

        self.label = Label(master, text="Select a file to send securely")
        self.label.pack(pady=10)

        self.select_button = Button(master, text="Select File", command=self.select_file)
        self.select_button.pack(pady=5)

    def select_file(self):
        filepath = filedialog.askopenfilename()
        if not filepath:
            return

        username = simpledialog.askstring("Authentication", "Enter username:")
        password = simpledialog.askstring("Authentication", "Enter password:", show='*')

        if not username or not password:
            messagebox.showerror("Error", "Username and password are required.")
            return

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, SERVER_PORT))

            # Step 1: Send credentials
            client_socket.send(f"{username}{SEPARATOR}{password}".encode())
            auth_response = client_socket.recv(BUFFER_SIZE).decode()
            if auth_response != "AUTH_SUCCESS":
                messagebox.showerror("Authentication Failed", "Invalid credentials.")
                client_socket.close()
                return

            # Step 2: Encrypt entire file
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            with open(filepath, "rb") as file:
                file_data = file.read()
                encrypted_data = cipher.encrypt(file_data)

            # Step 3: Send file metadata
            filename_encrypted = cipher.encrypt(filename.encode()).decode()
            client_socket.send(f"{filename_encrypted}{SEPARATOR}{len(encrypted_data)}".encode())

            # Step 4: Send encrypted file with progress
            progress = tqdm(total=len(encrypted_data), desc=f"Sending {filename}", unit="B", unit_scale=True)
            client_socket.sendall(encrypted_data)
            progress.update(len(encrypted_data))

            client_socket.close()
            messagebox.showinfo("Success", f"File '{filename}' sent successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = Tk()
    app = FileTransferClient(root)
    root.mainloop()
