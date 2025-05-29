import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Импорты из report.py
from asakk.report import (
    analyze_all_results,
    analyze_category_data,
    score_distribution_by_category,
    pie_chart_by_category,
    generate_recommendations,
    export_to_csv,
    predict_culture,
    calculate_category_trend,
    analyze_survey_data,
    build_category_bar_chart
)


class ManagerApp:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title("АСАКК — Панель менеджера")
        self.root.geometry("650x500")
        self.root.configure(bg="#f8f9fa")

        self.center_window()
        self.create_widgets()

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 650
        window_height = 500
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="Менеджер: Анализ корпоративной культуры",
            font=("Arial", 16, "bold"),
            bg="#f8f9fa",
            fg="#343a40"
        )
        title_label.pack(pady=20)

        category_frame = tk.Frame(self.root, bg="#f8f9fa")
        category_frame.pack(pady=10)

        tk.Label(category_frame, text="Выберите категорию", font=("Arial", 12), bg="#f8f9fa").pack()

        self.category_var = tk.StringVar(value="Ценности")
        categories = ["Ценности", "Коммуникации", "Лидерство", "Инновации", "Работа в команде", "Работа и личная жизнь"]

        self.category_menu = ttk.Combobox(
            category_frame,
            textvariable=self.category_var,
            values=categories,
            state="readonly",
            width=30,
            font=("Arial", 12)
        )
        self.category_menu.pack(pady=5)

        button_frame = tk.Frame(self.root, bg="#f8f9fa")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="📊 Общий отчет", width=25,
                  command=lambda: self.show_matplotlib_window(analyze_all_results),
                  bg="#007bff", fg="white").pack(pady=5)

        tk.Button(button_frame, text="📈 Отчет по категории", width=25,
                  command=self.show_category_report,
                  bg="#28a745", fg="white").pack(pady=5)

        tk.Button(button_frame, text="📊 Распределение оценок", width=25,
                  command=self.show_score_distribution,
                  bg="#ffc107", fg="black").pack(pady=5)

        tk.Button(button_frame, text="Диаграмма оценок", width=25,
                  command=self.show_pie_chart,
                  bg="#17a2b8", fg="white").pack(pady=5)

        tk.Button(button_frame, text="📋 Рекомендации", width=25,
                  command=self.show_recommendations,
                  bg="#dc3545", fg="white").pack(pady=5)

        tk.Button(button_frame, text="🔮 Прогнозирование", width=25,
                  command=self.show_prediction,
                  bg="#6f42c1", fg="white").pack(pady=5)

        tk.Button(button_frame, text="📤 Экспорт CSV", width=25,
                  command=self.export_data,
                  bg="#6c757d", fg="white").pack(pady=5)

        tk.Button(button_frame, text="🚪 Выйти", width=25,
                  command=self.root.quit,
                  bg="#343a40", fg="white").pack(pady=5)

    def disable_main_window(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                continue
            try:
                widget.configure(state='disabled')
            except tk.TclError:
                pass

    def enable_main_window(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                continue
            try:
                widget.configure(state='normal')
            except tk.TclError:
                pass

    def show_matplotlib_window(self, plot_func):
        self.disable_main_window()
        fig = None
        try:
            fig = plot_func()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать график: {e}")
            self.enable_main_window()
            return
        if fig is None:
            self.enable_main_window()
            return

        graph_window = tk.Toplevel(self.root)
        graph_window.title("График")
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        graph_window.protocol("WM_DELETE_WINDOW", lambda: [graph_window.destroy(), self.enable_main_window()])

    def build_category_bar_chart(data, category):
        """Строит график по данным категории"""
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(data["questions"], data["scores"])
        ax.set_title(f"Оценки по категории: {category}")
        ax.set_xlabel("Вопросы")
        ax.set_ylabel("Оценка")
        plt.xticks(rotation=45, fontsize=8, ha='right')
        plt.tight_layout()
        return fig


    def show_category_report(self):
        self.disable_main_window()
        category = self.category_var.get()
        try:
            data = analyze_category_data(category)
            if not data:
                messagebox.showinfo("Нет данных", f"Нет результатов для категории '{category}'")
                self.enable_main_window()
                return

            fig = build_category_bar_chart(data, category)
            if fig:
                graph_window = tk.Toplevel(self.root)
                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                graph_window.protocol("WM_DELETE_WINDOW", lambda: [graph_window.destroy(), self.enable_main_window()])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать отчет: {e}")
            self.enable_main_window()

    def show_score_distribution(self):
        self.disable_main_window()
        category = self.category_var.get()
        try:
            fig = score_distribution_by_category(category)
            if fig:
                graph_window = tk.Toplevel(self.root)
                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                graph_window.protocol("WM_DELETE_WINDOW", lambda: [graph_window.destroy(), self.enable_main_window()])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать график: {e}")
            self.enable_main_window()

    def show_pie_chart(self):
        self.disable_main_window()
        category = self.category_var.get()
        try:
            fig = pie_chart_by_category(category)
            if fig:
                graph_window = tk.Toplevel(self.root)
                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                graph_window.protocol("WM_DELETE_WINDOW", lambda: [graph_window.destroy(), self.enable_main_window()])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать диаграмму: {e}")
            self.enable_main_window()

    def show_recommendations(self):
        self.disable_main_window()
        try:
            analysis = analyze_survey_data()
            recommendations = generate_recommendations()

            if not analysis and not recommendations:
                messagebox.showinfo("Нет данных", "Нет слабых мест для рекомендаций.")
                self.enable_main_window()
                return

            rec_window = tk.Toplevel(self.root)
            rec_window.title("Рекомендации по улучшению культуры")
            rec_window.geometry("800x600")
            rec_window.configure(bg="#ffffff")

            rec_text = tk.Text(rec_window, wrap=tk.WORD, height=30, width=100, bg="#f9f9f9", bd=2, relief="sunken")
            rec_text.pack(padx=10, pady=10)

            rec_text.insert(tk.END, "📊 Статистика по категориям:\n\n")

            for cat, data in analysis.items():
                rec_text.insert(tk.END, f"Категория: {cat}\n")
                rec_text.insert(tk.END, f"  Среднее: {data['mean']}\n")
                rec_text.insert(tk.END, f"  Стандартное отклонение: {data['std']}\n")
                rec_text.insert(tk.END, f"  Дисперсия: {data['var']}\n")
                rec_text.insert(tk.END, f"  Количество аномальных вопросов: {len(data['anomalies'])}\n\n")

                if data['anomalies']:
                    rec_text.insert(tk.END, "  🔍 Аномальные вопросы:\n")
                    for anomaly in data['anomalies']:
                        rec_text.insert(tk.END, f"    - {anomaly['question']} | Отклонение: {anomaly['deviation']}\n")
                    rec_text.insert(tk.END, "\n")

            rec_text.insert(tk.END, "📋 Рекомендации:\n\n")

            if not recommendations:
                rec_text.insert(tk.END, "  Нет слабых мест для рекомендаций.\n")
            else:
                for cat, events in recommendations.items():
                    rec_text.insert(tk.END, f"➡️ {cat}:\n")
                    for event in events:
                        rec_text.insert(tk.END, f"- {event}\n")
                    rec_text.insert(tk.END, "\n")

            rec_text.config(state=tk.DISABLED)

            tk.Button(rec_window, text="Закрыть",
                      command=lambda: [rec_window.destroy(), self.enable_main_window()],
                      width=20, bg="#343a40", fg="white").pack(pady=10)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить рекомендации: {e}")
            self.enable_main_window()

    def export_data(self):
        try:
            export_to_csv()
            messagebox.showinfo("Готово", "Данные успешно экспортированы в results.csv")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")

    def show_prediction(self):
        """Отображает прогнозирование изменений показателей с графиком тренда"""
        self.disable_main_window()
        category = self.category_var.get()

        try:
            # Получаем числовой прогноз
            prediction = predict_culture()
            if not prediction:
                messagebox.showinfo("Нет данных", "Нет исторических данных для прогнозирования.")
                self.enable_main_window()
                return

            # Получаем данные для графика по выбранной категории
            trend_data = calculate_category_trend(category)
            if trend_data is None:
                messagebox.showinfo("Нет данных", f"Недостаточно данных для категории '{category}'")
                self.enable_main_window()
                return

            # Создаём окно прогноза
            pred_window = tk.Toplevel(self.root)
            pred_window.title(f"Прогнозирование культуры — {category}")
            pred_window.geometry("900x600")
            pred_window.configure(bg="#ffffff")

            # Левая часть: текстовый прогноз
            text_frame = tk.Frame(pred_window, bg="#ffffff")
            text_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

            tk.Label(text_frame, text="📊 Прогноз на основе линейной регрессии", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=5)

            pred_text = tk.Text(text_frame, wrap=tk.WORD, height=20, width=40, bg="#f9f9f9", bd=2, relief="sunken")
            pred_text.pack(padx=5, pady=5)

            for cat, result in prediction.items():
                pred_text.insert(tk.END, f"{cat}:\n{result}\n\n")
            pred_text.config(state=tk.DISABLED)

            # Правая часть: график тренда
            graph_frame = tk.Frame(pred_window, bg="#ffffff")
            graph_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

            fig, ax = plt.subplots(figsize=(7, 4))
            x = list(range(len(trend_data["scores"])))
            ax.plot(x, trend_data["scores"], label="Оценки", marker='o', linestyle='')
            ax.plot(x, trend_data["trend"], color='red',
                    label=f'Тренд (y = {trend_data["slope"][0]:.2f}x + {trend_data["intercept"][0]:.2f})')
            ax.set_title(f"Тренд по категории: {category}")
            ax.set_xlabel("Порядковый номер ответа")
            ax.set_ylabel("Оценка")
            ax.legend()
            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Кнопка закрытия
            tk.Button(
                pred_window,
                text="Закрыть",
                command=lambda: [pred_window.destroy(), self.enable_main_window()],
                width=20,
                bg="#343a40",
                fg="white"
            ).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить прогноз: {e}")
            self.enable_main_window()