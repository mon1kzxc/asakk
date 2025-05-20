import tkinter as tk
from tkinter import messagebox
from asakk.quiz import get_categories, get_questions_by_category
from ui.quiz_form import QuizFormApp


class EmployeeApp:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title("АСАКК — Прохождение опроса")
        self.root.geometry("500x400")
        self.root.configure(bg="#f8f9fa")

        self.center_window()

        # Заголовок
        title_label = tk.Label(
            root,
            text="Выберите категорию для прохождения опроса",
            font=("Arial", 14, "bold"),
            bg="#f8f9fa",
            fg="#343a40"
        )
        title_label.pack(pady=20)

        # Выбор категории
        self.category_var = tk.StringVar(value="Все категории")
        category_frame = tk.Frame(root, bg="#f8f9fa")
        category_frame.pack(pady=10)

        tk.Label(category_frame, text="Категория", font=("Arial", 12), bg="#f8f9fa").pack()
        self.category_menu = tk.OptionMenu(category_frame, self.category_var, *["Все категории"] + get_categories())
        self.category_menu.config(width=25, bg="#007bff", fg="white")
        self.category_menu.pack(pady=5)

        # Кнопка начала опроса
        start_button = tk.Button(
            category_frame,
            text="Начать опрос",
            command=self.start_quiz,
            width=25,
            bg="#28a745",
            fg="white"
        )
        start_button.pack(pady=10)

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 500
        window_height = 400
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def start_quiz(self):
        category = self.category_var.get()
        try:
            questions = get_questions_by_category(category)
            if not questions:
                messagebox.showerror("Ошибка", f"Нет вопросов в категории '{category}'")
                return

            self.root.destroy()
            quiz_root = tk.Tk()
            QuizFormApp(quiz_root, self.user, questions).run()
            quiz_root.mainloop()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить вопросы: {e}")