# ui/question_editor.py

import tkinter as tk
from tkinter import ttk, messagebox
from asakk.report import add_question_with_recommendation, delete_question_by_id
from asakk.quiz import get_all_questions


class QuestionEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("АСАКК — Редактор вопросов")
        self.root.geometry("800x600")
        self.root.configure(bg="#f8f9fa")

        self.center_window()
        self.create_widgets()
        self.load_questions()  # Загружаем список вопросов сразу

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
            text="Добавление и удаление вопросов",
            font=("Arial", 14, "bold"),
            bg="#f8f9fa"
        )
        title_label.pack(pady=20)

        # --- Список вопросов ---
        list_frame = tk.Frame(self.root)
        list_frame.pack(padx=20, pady=5, fill="both", expand=True)

        tk.Label(list_frame, text="Существующие вопросы:", bg="#f8f9fa").pack(anchor="w")

        self.question_listbox = tk.Listbox(list_frame, height=8, width=100, font=("Arial", 10))
        self.question_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.question_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        self.question_listbox.config(yscrollcommand=scrollbar.set)

        # --- Форма добавления ---
        form_frame = tk.Frame(self.root, bg="#f8f9fa")
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Категория", bg="#f8f9fa").grid(row=0, column=0)

        category_combo = ttk.Combobox(
            form_frame,
            values=["Ценности", "Коммуникации", "Лидерство", "Инновации", "Работа в команде", "Работа и личная жизнь"],
            state="readonly",
            width=30
        )
        category_combo.set("Выберите категорию")
        category_combo.grid(row=0, column=1)
        self.category_combo = category_combo  # Сохраняем ссылку

        tk.Label(form_frame, text="Текст вопроса", bg="#f8f9fa").grid(row=1, column=0)
        self.entry_question = tk.Entry(form_frame, width=50)
        self.entry_question.grid(row=1, column=1)

        tk.Label(form_frame, text="Мероприятие по улучшению культуры", bg="#f8f9fa").grid(row=2, column=0)
        self.entry_event = tk.Entry(form_frame, width=50)
        self.entry_event.grid(row=2, column=1)

        tk.Button(
            form_frame,
            text="Добавить вопрос + мероприятие",
            command=self.add_question_and_event,
            width=30,
            bg="#007bff",
            fg="white"
        ).grid(row=3, columnspan=2, pady=10)

        # --- Форма удаления ---
        delete_frame = tk.Frame(self.root, bg="#f8f9fa")
        delete_frame.pack(pady=10)

        tk.Label(delete_frame, text="Введите ID вопроса для удаления", bg="#f8f9fa").pack()
        self.entry_delete_id = tk.Entry(delete_frame, width=10)
        self.entry_delete_id.pack(pady=5)

        tk.Button(
            delete_frame,
            text="Удалить вопрос",
            command=self.delete_question,
            width=30,
            bg="#dc3545",
            fg="white"
        ).pack(pady=5)

        # --- Кнопка выхода ---
        tk.Button(
            self.root,
            text="Назад",
            command=self.root.destroy,
            width=25,
            bg="#6c757d",
            fg="white"
        ).pack(pady=10)

    def load_questions(self):
        """Загружает список вопросов из базы данных"""
        self.question_listbox.delete(0, tk.END)
        questions = get_all_questions()

        if not questions:
            self.question_listbox.insert(tk.END, "Нет созданных вопросов.")
        else:
            for question in questions:
                self.question_listbox.insert(tk.END, f"ID: {question[0]} | Категория: {question[2]} | Вопрос: {question[1]}")

    def add_question_and_event(self):
        category = self.category_combo.get()  # Используем .get() у Combobox, а не StringVar
        question_text = self.entry_question.get().strip()
        event_text = self.entry_event.get().strip()

        print(f"[DEBUG] Добавление вопроса: Категория='{category}', Вопрос='{question_text}', Мероприятие='{event_text}'")

        if category == "" or category == "Выберите категорию":
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите корректную категорию.")
            return

        # Проверяем заполненность текстовых полей
        if not question_text or not event_text:
            messagebox.showwarning("Ошибка", "Все поля должны быть заполнены.")
            return

        # Пробуем добавить данные
        try:
            add_question_with_recommendation(category, question_text, event_text)
            messagebox.showinfo("Готово", "Вопрос и мероприятие успешно добавлены!")
            self.entry_question.delete(0, tk.END)
            self.entry_event.delete(0, tk.END)
            self.load_questions()  # Обновляем список
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить данные:\n{e}")

    def delete_question(self):
        qid = self.entry_delete_id.get().strip()
        if not qid.isdigit():
            messagebox.showwarning("Ошибка", "Введите корректный ID вопроса")
            return

        qid_int = int(qid)

        try:
            delete_question_by_id(qid_int)
            messagebox.showinfo("Готово", f"Вопрос с ID {qid_int} удален.")
            self.entry_delete_id.delete(0, tk.END)
            self.load_questions()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить вопрос:\n{e}")