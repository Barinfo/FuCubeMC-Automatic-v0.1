import socket
import select
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

def send_command(progress_var, button, status_label):
    host = 's1.ultrasnd.cn'
    port = 7481
    command = 'C:/Users/Administrator/Desktop/pull.bat'

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        client_socket.sendall(command.encode())

        status_label.config(text="同步中...")
        button.config(state=tk.DISABLED)

        for i in range(81):
            root.update_idletasks()
            progress_var.set(i)
            root.update()

            ready_to_read, _, _ = select.select([client_socket], [], [], 0.1)
            if ready_to_read:
                output = client_socket.recv(4096).decode()
                break

            root.after(max(10, i * 5))

        if not output:
            output = client_socket.recv(4096).decode()

        #print(f"Command output:\n{output}")

        client_socket.close()

        progress_var.set(100)
        button.config(state=tk.NORMAL)

        status_label.config(text="同步完成")

        messagebox.showinfo("Success", f"已完成同步")
    except Exception as e:
        messagebox.showerror("Error", f"同步失败: {e}")

# 创建主窗口
root = tk.Tk()
root.title("同步工具")
root.geometry("400x180")  # 调整窗口大小以适应更宽的进度条

# 创建进度条
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, expand=True)  # 修改这里让进度条充满窗口宽度

# 创建状态标签
status_label = tk.Label(root, text="", font=("Helvetica", 10))
status_label.pack()

# 创建一个按钮
sync_button = tk.Button(root, text="同步", command=lambda: send_command(progress_var, sync_button, status_label), width=20, height=2)
sync_button.pack(pady=20)

# 运行主循环
root.mainloop()