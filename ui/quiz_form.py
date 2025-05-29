import tkinter as tk
from tkinter import messagebox
from asakk.report import save_answers


class QuizFormApp:
    def __init__(self, root, user, questions, on_complete=None):
        self.root = root
        self.user = user
        self.questions = questions
        self.answers = {}
        self.current_index = 0
        self.on_complete = on_complete  # Функция, которая вызывается после завершения
        self.root.title(f"Опрос — {questions[0][2] if len(questions) > 0 else 'Без категории'}")
        self.root.geometry("600x400")

        # Вопрос
        self.question_label = tk.Label(
            root,
            text=self.get_current_question_text(),
            wraplength=500,
            justify="center",
            font=("Arial", 12)
        )
        self.question_label.pack(pady=20)

        # Шкала от 0 до 4
        self.var = tk.IntVar(value=-1)
        self.radio_buttons = []

        for i in range(5):  # 0–4
            rb = tk.Radiobutton(root, text=str(i), variable=self.var, value=i)
            rb.pack()
            self.radio_buttons.append(rb)

        # Кнопка "Далее"
        self.next_button = tk.Button(root, text="Далее", command=self.next_question)
        self.next_button.pack(pady=20)

    def get_current_question_text(self):
        return self.questions[self.current_index][1]

    def next_question(self):
        selected = self.var.get()
        if selected == -1:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите оценку.")
            return

        q_id = self.questions[self.current_index][0]
        self.answers[q_id] = selected
        self.current_index += 1

        if self.current_index < len(self.questions):
            self.question_label.config(text=self.get_current_question())
            self.var.set(-1)
        else:
            self.finish_quiz()

    def finish_quiz(self):
        try:
            save_answers(self.user[0], self.answers)
            messagebox.showinfo("Готово", "Ваш опрос пройден!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
        finally:
            # Вызываем callback, если он передан
            if self.on_complete:
                self.on_complete()
            self.root.destroy()  # Закрываем окно квиза
            messagebox.showinfo("Завершение", "Спасибо за участие в опросе!")

    def get_current_question(self):
        return self.questions[self.current_index][1]

    def run(self):
        self.root.mainloop()