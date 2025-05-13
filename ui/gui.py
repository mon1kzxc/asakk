import tkinter as tk
from tkinter import messagebox
from asakk.quiz import get_categories, get_questions_by_category
from ui.quiz_form import QuizFormApp

class EmployeeApp:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title("АСАКК — Прохождение опроса")

        tk.Label(root, text="Выберите категорию").pack(pady=10)

        self.category_var = tk.StringVar(value="Все категории")
        self.category_menu = tk.OptionMenu(root, self.category_var, *["Все категории"] + get_categories())
        self.category_menu.pack(pady=5)

        tk.Button(root, text="Начать опрос", command=self.start_quiz).pack(pady=10)

    def start_quiz(self):
        category = self.category_var.get()
        try:
            questions = get_questions_by_category(category)
            if not questions:
                messagebox.showerror("Ошибка", f"Нет вопросов для категории '{category}'")
                return

            self.root.destroy()
            quiz_root = tk.Tk()
            QuizFormApp(quiz_root, self.user, questions)
            quiz_root.mainloop()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить вопросы: {e}")
