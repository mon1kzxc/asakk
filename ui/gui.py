import tkinter as tk
from tkinter import messagebox
from asakk.quiz import get_categories, get_questions_by_categories  # Предполагается, что такая функция есть
from ui.quiz_form import QuizFormApp


class EmployeeApp:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title("АСАКК — Прохождение опроса")
        self.root.geometry("500x400")
        self.root.configure(bg="#f8f9fa")

        self.quiz_in_progress = False  # ✅ Флаг активности квиза

        self.center_window_on_parent(self.root)

        # Заголовок
        title_label = tk.Label(
            root,
            text="Выберите категории для прохождения опроса",
            font=("Arial", 14, "bold"),
            bg="#f8f9fa",
            fg="#343a40"
        )
        title_label.pack(pady=20)

        # Выбор категорий
        self.category_vars = {}  # Хранит переменные для чекбоксов
        category_frame = tk.Frame(root, bg="#f8f9fa")
        category_frame.pack(pady=10)

        tk.Label(category_frame, text="Категории", font=("Arial", 12), bg="#f8f9fa").pack()

        categories = get_categories()
        for category in categories:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(category_frame, text=category, variable=var, bg="#f8f9fa")
            chk.pack(anchor='w', padx=20)
            self.category_vars[category] = var

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

    def center_window_on_parent(self, window):
        """Центрирует дочернее окно относительно главного"""
        window.update_idletasks()
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def start_quiz(self):
        if self.quiz_in_progress:  # ✅ Проверяем, идёт ли уже квиз
            messagebox.showinfo("Внимание", "Опрос уже запущен.")
            return

        selected_categories = [cat for cat, var in self.category_vars.items() if var.get()]
        if not selected_categories:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы одну категорию.")
            return

        try:
            questions = get_questions_by_categories(selected_categories)  # Должна поддерживать список категорий
            if not questions:
                messagebox.showerror("Ошибка", "Не найдено вопросов по выбранным категориям.")
                return

            self.quiz_in_progress = True  # ✅ Устанавливаем флаг

            # Скрываем главное окно вместо его уничтожения
            self.root.withdraw()

            quiz_window = tk.Toplevel(self.root)
            quiz_window.title("Прохождение опроса")
            quiz_window.geometry("600x400")
            self.center_window_on_parent(quiz_window)

            QuizFormApp(quiz_window, self.user, questions, on_complete=self.return_to_menu).run()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить вопросы: {e}")

    def return_to_menu(self):
        """Вызывается после завершения опроса"""
        self.quiz_in_progress = False  # ✅ Сбрасываем флаг
        self.root.deiconify()  # Показываем главное окно

        # Сброс всех чекбоксов
        for var in self.category_vars.values():
            var.set(False)