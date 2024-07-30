import socket
import tkinter as tk
from tkinter import messagebox

def send_command():
    host = '127.0.0.1'
    port = 12345
    command = 'cd %USERPROFILE%\\Desktop\\FuCubemc-Automatic && git pull https://github.com/Barinfo/FuCubeMC-Automatic.git main'

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        client_socket.sendall(command.encode())

        output = client_socket.recv(4096).decode()
        print(f"Command output:\n{output}")

        client_socket.close()

        messagebox.showinfo("Success", "已完成同步")
    except Exception as e:
        messagebox.showerror("Error", f"同步失败: {e}")

# 创建主窗口
root = tk.Tk()
root.title("同步工具")

# 创建一个按钮
sync_button = tk.Button(root, text="同步", command=send_command)
sync_button.pack(pady=20)

# 运行主循环
root.mainloop()
