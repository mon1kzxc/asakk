import tkinter as tk
from ui.gui import EmployeeApp
from ui.manager_gui import ManagerApp
from asakk.auth import authenticate

def main():
    login_root = tk.Tk()
    
    def on_login():
        from asakk.auth import authenticate
        user = authenticate(entry_user.get(), entry_key.get())
        if user:
            login_root.destroy()
            role = user[2]
            if role == "Employee":
                app_root = tk.Tk()
                EmployeeApp(app_root, user)
                app_root.mainloop()
            elif role == "Manager":
                app_root = tk.Tk()
                ManagerApp(app_root, user)
                app_root.mainloop()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или ключ SSH.")

    tk.Label(login_root, text="Логин").pack()
    entry_user = tk.Entry(login_root)
    entry_user.pack()

    tk.Label(login_root, text="SSH-ключ").pack()
    entry_key = tk.Entry(login_root, show="*")
    entry_key.pack()

    tk.Button(login_root, text="Войти", command=on_login).pack(pady=10)
    login_root.mainloop()

if __name__ == "__main__":
    main()