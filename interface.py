import graf
import tkinter as tk

def reports():
    root = tk.Tk()
    root.title("Аналитические отчеты")

    # Добавляем фразу над кнопками
    label_title = tk.Label(root, text="Программное обеспечение для построения аналитических отчетов", font=("Arial", 14))
    label_title.pack(pady=20)

    # Функции-обработчики для кнопок
    def on_button_graf1():
        graf.graf1()

    def on_button_graf2():
        graf.graf2()

    def on_button_graf3():
        graf.graf3()

    def on_button_graf4():
        graf.graf4()

    def on_button_graf5():
        arg = entry_graf5.get()
        graf.graf5(arg)

    def on_button_graf6():
        graf.graf6()

    # Функция для создания кнопок с округлыми углами
    def create_round_button(parent, text, command, x1, y1, x2, y2, radius=20):
        button = tk.Canvas(parent, width=x2 - x1, height=y2 - y1, bg="#C8A2C8", bd=0, highlightthickness=0,
                           relief="flat")
        button.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, extent=90, fill="#C8A2C8",
                          outline="#C8A2C8")
        button.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, extent=90, fill="#C8A2C8",
                          outline="#C8A2C8")
        button.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, extent=90, fill="#C8A2C8",
                          outline="#C8A2C8")
        button.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, extent=90, fill="#C8A2C8",
                          outline="#C8A2C8")
        button.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill="#C8A2C8", outline="#C8A2C8")
        button.create_rectangle(x1, y1 + radius, x2, y2 - radius, fill="#C8A2C8", outline="#C8A2C8")

        # Добавляем текст
        button.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, fill="black", font=("Arial", 12))

        button.bind("<Button-1>", lambda event: command())  # Привязка события нажатия кнопки
        return button

    # Функция для добавления черной линии
    def create_line(parent, y_position):
        canvas = tk.Canvas(parent, width=200, height=2, bg="black", bd=0, highlightthickness=0)
        canvas.place(x=20, y=y_position)

    # Создание кнопок с округлыми углами

    entry_graf1_label = tk.Label(root, text="Отчет 1: Гистограмма времени нахождения задач в открытом состоянии", font=("Arial", 10))
    entry_graf1_label.pack(pady=5)
    create_line(root, 70)

    button_graf1 = create_round_button(root, "graf1", on_button_graf1, 20, 60, 180, 100)
    button_graf1.pack(pady=10)


    entry_graf2_label = tk.Label(root, text="Отчет 2: Гистограмма времени распределения задач в зависимости от состояния задачи", font=("Arial", 10))
    entry_graf2_label.pack(pady=5)

    button_graf2 = create_round_button(root, "graf2", on_button_graf2, 20, 110, 180, 150)
    button_graf2.pack(pady=10)
    create_line(root, 160)

    entry_graf3_label = tk.Label(root, text="Отчет 3: График, показывающий количество заведенных и закрытых задач в день", font=("Arial", 10))
    entry_graf3_label.pack(pady=5)

    button_graf3 = create_round_button(root, "graf3", on_button_graf3, 20, 160, 180, 200)
    button_graf3.pack(pady=10)
    create_line(root, 250)

    entry_graf4_label = tk.Label(root, text="Отчет 4: График, показывающий общее количество задач для пользователей, в которых он указан как исполнитель и репортер", font=("Arial", 10))
    entry_graf4_label.pack(pady=5)

    button_graf4 = create_round_button(root, "graf4", on_button_graf4, 20, 210, 180, 250)
    button_graf4.pack(pady=10)
    create_line(root, 340)

    entry_graf5_label = tk.Label(root, text="Отчет 5: Гистограмма, отражающая время, которое потратил пользователь на ее выполнение", font=("Arial", 10))
    entry_graf5_label.pack(pady=5)

    # Создаем поле для ввода значения для graf5
    entry_graf5_label = tk.Label(root, text="Введите имя пользователя:")
    entry_graf5_label.pack(pady=5)

    entry_graf5 = tk.Entry(root)
    entry_graf5.pack(pady=5)

    button_graf5 = create_round_button(root, "graf5", on_button_graf5, 20, 260, 180, 300)
    button_graf5.pack(pady=10)
    create_line(root, 430)

    entry_graf6_label = tk.Label(root, text="Отчет 6: График, выражающий количество задач по степени серьезности", font=("Arial", 10))
    entry_graf6_label.pack(pady=5)

    button_graf6 = create_round_button(root, "graf6", on_button_graf6, 20, 310, 180, 350)
    button_graf6.pack(pady=10)
    create_line(root, 580)

    # Запуск основного цикла
    root.mainloop()
