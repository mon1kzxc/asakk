import tkinter as tk
from tkinter import messagebox
from asakk.quiz import save_answers

class QuizFormApp:
    def __init__(self, root, user, questions):
        self.root = root
        self.root.title(f"Опрос — {questions[0][2] if questions else 'Без категории'}")

        self.questions = questions
        self.current_index = 0
        self.answers = {}
        self.user = user

        self.question_label = tk.Label(root, text="", wraplength=500, font=("Arial", 12))
        self.question_label.pack(pady=20)

        self.var = tk.IntVar(value=-1)
        self.radio_buttons = []

        for i in range(5):  # Шкала от 0 до 4
            rb = tk.Radiobutton(root, text=str(i), variable=self.var, value=i)
            rb.pack()
            self.radio_buttons.append(rb)

        self.next_button = tk.Button(root, text="Далее", command=self.next_question)
        self.next_button.pack(pady=20)

        self.show_current_question()

    def show_current_question(self):
        if self.current_index < len(self.questions):
            q_id, text, category = self.questions[self.current_index]
            self.question_label.config(text=f"{self.current_index + 1}. {text}")
            self.var.set(-1)
        else:
            self.finish_quiz()

    def next_question(self):
        selected = self.var.get()
        if selected == -1:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите оценку.")
            return

        q_id, _, _ = self.questions[self.current_index]
        self.answers[q_id] = selected
        self.current_index += 1

        if self.current_index < len(self.questions):
            self.show_current_question()
        else:
            save_answers(self.user[0], self.answers)
            messagebox.showinfo("Готово", "Опрос пройден!")
            self.root.quit()

    def finish_quiz(self):
        q_id, _, _ = self.questions[self.current_index]
        self.answers[q_id] = self.var.get()
        save_answers(self.user[0], self.answers)
        messagebox.showinfo("Готово", "Все ответы сохранены.")
        self.root.quit()