import tkinter as tk
from asakk.report import analyze_all_results

class ManagerApp:
    def __init__(self, root, user):
        self.root = root
        self.root.title("АСАКК — Менеджер")

        tk.Label(root, text="Панель менеджера").pack(pady=20)
        tk.Button(root, text="Показать общий отчет", command=self.show_report).pack(pady=10)

    def show_report(self):
        analyze_all_results()