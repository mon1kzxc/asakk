import logging
import tkinter as tk
from tkinter import messagebox
from asakk.auth import get_all_users, add_user_to_db, delete_user_from_db
from asakk.quiz import add_question_with_recommendation
from asakk.report import add_recommendation_to_db 
from ui.question_editor import QuestionEditorApp

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("asakk.log", encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.propagate = False


class AdminApp:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title("АСАКК — Панель администратора")
        self.root.geometry("800x600")
        self.root.configure(bg="#f8f9fa")

        self.center_window()
        self.create_widgets()

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 600
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="Администратор: Управление пользователями",
            font=("Arial", 14, "bold"),
            bg="#f8f9fa"
        )
        title_label.pack(pady=20)

        # --- Форма добавления пользователя ---
        user_frame = tk.LabelFrame(self.root, text="Управление пользователями", bg="#ffffff", padx=10, pady=10)
        user_frame.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(user_frame, text="Имя пользователя", bg="#ffffff").grid(row=0, column=0)
        self.entry_username = tk.Entry(user_frame, width=30)
        self.entry_username.grid(row=0, column=1)

        tk.Label(user_frame, text="SSH-ключ", bg="#ffffff").grid(row=1, column=0)
        self.entry_ssh_key = tk.Entry(user_frame, show="*", width=30)
        self.entry_ssh_key.grid(row=1, column=1)

        tk.Label(user_frame, text="Роль", bg="#ffffff").grid(row=2, column=0)
        self.role_var = tk.StringVar(value="Employee")
        roles = ["Employee", "Manager", "Admin"]
        role_menu = tk.OptionMenu(user_frame, self.role_var, *roles)
        role_menu.grid(row=2, column=1)

        tk.Button(
            user_frame,
            text="Добавить пользователя",
            command=self.add_user,
            width=25,
            bg="#28a745",
            fg="white"
        ).grid(row=3, columnspan=2, pady=5)

        tk.Button(
            user_frame,
            text="Удалить пользователя",
            command=self.delete_selected,
            width=25,
            bg="#dc3545",
            fg="white"
        ).grid(row=4, columnspan=2, pady=5)

        # Список пользователей
        self.user_listbox = tk.Listbox(user_frame, height=10, width=70)
        self.user_listbox.grid(row=5, columnspan=2, pady=10)
        self.load_users()

        # --- Кнопка открытия редактора вопросов ---
        question_button = tk.Button(
            self.root,
            text="Добавление вопросов и мероприятий",
            command=self.open_question_editor,
            width=30,
            bg="#007bff",
            fg="white"
        )
        question_button.pack(pady=10)

        # --- Выход из админки ---
        exit_button = tk.Button(
            self.root,
            text="Выйти",
            command=self.root.destroy,
            width=25,
            bg="#6c757d",
            fg="white"
        )
        exit_button.pack(pady=10)

    def load_users(self):
        from asakk.auth import get_all_users
        self.user_listbox.delete(0, tk.END)
        users = get_all_users()
        for user in users:
            self.user_listbox.insert(tk.END, f"ID: {user[0]} | Имя: {user[1]} | Роль: {user[2]}")

    def add_user(self):
        username = self.entry_username.get().strip()
        ssh_key = self.entry_ssh_key.get().strip()
        role = self.role_var.get().strip()

        if not username or not ssh_key:
            messagebox.showwarning("Ошибка", "Заполните имя и SSH-ключ.")
            return

        try:
            add_user_to_db(username, ssh_key, role)
            messagebox.showinfo("Готово", "Пользователь успешно добавлен!")
            self.entry_username.delete(0, tk.END)
            self.entry_ssh_key.delete(0, tk.END)
            self.load_users()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя:\n{e}")

    def delete_selected(self):
        selected = self.user_listbox.curselection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пользователя")
            return

        item = self.user_listbox.get(selected[0])
    
        print(f"[DEBUG] Выбран элемент: '{item}'")  # ← Отладка
        print(f"[DEBUG] Разделение по | : {item.split('|')}")

        try:
        # Парсим ID правильно
            id_str = item.split('|')[0]  # Получаем "ID: 5"
            user_id = int(id_str.split(':')[1].strip())  # Теперь безопасное извлечение
            print(f"[DEBUG] Удаляемый ID: {user_id}")

            from asakk.auth import delete_user_from_db
            success = delete_user_from_db(user_id)

            if success:
                messagebox.showinfo("Готово", "Пользователь удален!")
                self.load_users()
            else:
                raise Exception("Не удалось удалить пользователя (нет результата)")
        except IndexError:
            logger.error("Ошибка разбора строки пользователя")
            messagebox.showerror("Ошибка", "Не удалось определить ID пользователя")
        except ValueError:
            logger.error("Ошибка преобразования ID")
            messagebox.showerror("Ошибка", "Неверный формат ID")
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя: {e}", exc_info=True)
            messagebox.showerror("Ошибка", f"Не удалось удалить пользователя:\n{e}")


    def open_question_editor(self):
        editor_root = tk.Tk()
        QuestionEditorApp(editor_root)
        editor_root.mainloop()

    