import tkinter as tk
from asakk.auth import authenticate

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("АСАКК — Авторизация")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        self.center_window()

        tk.Label(root, text="Авторизация в системе", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=15)

        tk.Label(root, text="Логин", bg="#f0f0f0").pack()
        self.entry_user = tk.Entry(root, width=30)
        self.entry_user.pack(pady=5)

        tk.Label(root, text="SSH-ключ", bg="#f0f0f0").pack()
        self.entry_key = tk.Entry(root, show="*", width=30)
        self.entry_key.pack(pady=5)

        tk.Button(root, text="Войти", width=25, command=self.login, bg="#3b8d99", fg="white").pack(pady=10)

    def login(self):
        username = self.entry_user.get()
        key = self.entry_key.get()
        user = authenticate(username, key)

        if user:
            self.root.destroy()
            role = user[2]
            app_root = tk.Tk()

            if role == "Employee":
                from ui.gui import EmployeeApp
                EmployeeApp(app_root, user)
                app_root.mainloop()
            elif role == "Manager":
                from ui.manager_gui import ManagerApp
                ManagerApp(app_root, user)
                app_root.mainloop()
            elif role == "Admin":
                from ui.admin_gui import AdminApp
                AdminApp(app_root, user)
                app_root.mainloop()
        else:
            from tkinter import messagebox
            messagebox.showerror("Ошибка", "Неверный логин или ключ SSH.")

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 400
        window_height = 300
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")