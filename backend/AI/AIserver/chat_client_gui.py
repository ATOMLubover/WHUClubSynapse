import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import json
import threading

class AIChatClient:
    def __init__(self, master):
        self.master = master
        master.title("AI聊天客户端")
        master.geometry("800x600")

        # 配置行和列的权重，使其能够根据窗口大小调整
        master.grid_rowconfigure(0, weight=0) # IP/Port
        master.grid_rowconfigure(1, weight=1) # Chat display
        master.grid_rowconfigure(2, weight=0) # Message input
        master.grid_columnconfigure(0, weight=1)

        # 服务器地址配置
        self.server_frame = tk.Frame(master)
        self.server_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.server_frame.columnconfigure(1, weight=1) # Make URL entry expand

        tk.Label(self.server_frame, text="服务器URL:").grid(row=0, column=0, sticky="w")
        self.url_entry = tk.Entry(self.server_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, sticky="ew", columnspan=3)
        self.url_entry.insert(0, "https://fa82-125-220-159-5.ngrok-free.app") # 默认ngrok URL

        # 聊天显示区域
        self.chat_display = scrolledtext.ScrolledText(master, wrap=tk.WORD, state='disabled', font=("Arial", 10))
        self.chat_display.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # 消息输入区域
        self.message_frame = tk.Frame(master)
        self.message_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.message_frame.columnconfigure(0, weight=1) # Make message entry expand

        self.message_entry = tk.Entry(self.message_frame, font=("Arial", 10))
        self.message_entry.grid(row=0, column=0, padx=5, sticky="ew")
        self.message_entry.bind("<Return>", self.send_message_event) # 绑定回车键

        self.send_button = tk.Button(self.message_frame, text="发送", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=5)

    def log_message(self, sender, message, color="black"):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: ", color)
        self.chat_display.tag_add(sender, self.chat_display.index(tk.END) + f"-{len(sender) + 2}c", tk.END)
        self.chat_display.tag_config(sender, foreground=color)
        self.chat_display.insert(tk.END, f"{message}\n")
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END) # 自动滚动到底部

    def send_message_event(self, event):
        self.send_message()

    def send_message(self):
        user_message = self.message_entry.get().strip()
        if not user_message:
            return

        self.log_message("你", user_message, "blue")
        self.message_entry.delete(0, tk.END)

        server_url = self.url_entry.get().strip()

        if not server_url:
            messagebox.showerror("错误", "请输入服务器URL。")
            self.log_message("系统", "发送失败：未提供服务器URL。", "red")
            return

        # 在新线程中发送请求，防止GUI卡顿
        threading.Thread(target=self._send_request_thread, args=(server_url, user_message)).start()

    def _send_request_thread(self, url, message):
        # 拼接完整的聊天接口URL，使用更通用的 /chat 接口
        full_url = f"{url}/chat"
        headers = {"Content-Type": "application/json"}
        payload = {
            "messages": [{"role": "user", "content": message}],
            "model": "Qwen/Qwen3-8B-AWQ", # 根据服务器实际模型修改
            "stream": False # 客户端目前不处理流式响应，设置为False
        }

        try:
            self.log_message("系统", "正在连接AI服务器...", "gray")
            response = requests.post(full_url, headers=headers, json=payload, timeout=60) # 设置超时
            response.raise_for_status() # 检查HTTP错误

            result = response.json()
            ai_response_content = result.get("response", "AI未返回有效内容。")
            ai_model = result.get("model", "未知模型")

            self.log_message("AI助手", ai_response_content, "green")
            self.log_message("系统", f"（模型: {ai_model}）", "gray")

        except requests.exceptions.Timeout:
            self.log_message("系统", "连接超时，AI服务器可能没有响应。", "red")
            messagebox.showerror("连接错误", "连接AI服务器超时。请检查服务器是否正在运行，并且URL是否正确。")
        except requests.exceptions.ConnectionError:
            self.log_message("系统", "无法连接到AI服务器，请检查URL。", "red")
            messagebox.showerror("连接错误", "无法连接到AI服务器。请检查服务器URL是否正确，并确保服务器已启动。")
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_json = e.response.json()
                error_detail = error_json.get("detail", e.response.text)
            except json.JSONDecodeError:
                error_detail = e.response.text
            self.log_message("系统", f"AI服务器返回错误: {e.response.status_code} - {error_detail}", "red")
            messagebox.showerror("服务器错误", f"AI服务器返回错误: {e.response.status_code}\n{error_detail}")
        except json.JSONDecodeError:
            self.log_message("系统", "AI服务器返回的响应不是有效的JSON。", "red")
            messagebox.showerror("数据错误", "AI服务器返回的响应格式错误。")
        except Exception as e:
            self.log_message("系统", f"发生未知错误: {e}", "red")
            messagebox.showerror("错误", f"发生未知错误: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    client = AIChatClient(root)
    root.mainloop() 