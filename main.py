from jira import JIRA
import requests
import json
import numpy as np
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
from collections import Counter

def graf1():
    # Подключение к API JIRA
    url = 'https://issues.apache.org/jira/rest/api/2/search'
    payload = {
        'jql': 'project=KAFKA AND status=Closed ORDER BY createdDate',
        'maxResults': '1000',
        'expand': 'changelog',
        'fields': 'created,resolutiondate'
    }

    # Получение данных из JIRA
    response = requests.get(url, params=payload)
    data = json.loads(response.text)

    # Список для хранения времени нахождения задач в открытом состоянии
    open_durations = []

    # Обработка полученных задач
    for issue in data['issues']:
        created_date = issue['fields']['created'] #время открытия задачи
        resolution_date = issue['fields']['resolutiondate'] #время решения задачи

        # Преобразование строковых дат в объекты datetime
        created_dt = datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        resolution_dt = datetime.strptime(resolution_date, '%Y-%m-%dT%H:%M:%S.%f%z')

        # Вычисляем продолжительность в открытом состоянии (в днях)
        open_duration = (resolution_dt - created_dt).total_seconds() / (60 * 60 * 24)  # время в днях
        open_durations.append(open_duration)

    # Строим гистограмму
    plt.figure(figsize=(10, 6))
    plt.hist(open_durations, bins=20, edgecolor='black', color='violet')

    # Настроим оси и заголовок
    plt.title('Гистограмма времени нахождения задач в открытом состоянии')
    plt.xlabel('Время в открытом состоянии (дни)')
    plt.ylabel('Количество задач')

    # Показываем гистограмму
    plt.show()

def graf2():
    # Подключение к API JIRA
    url = 'https://issues.apache.org/jira/rest/api/2/search'
    payload = {
        'jql': 'project=KAFKA AND status=Closed ORDER BY createdDate',
        'maxResults': '1000',
        'expand': 'changelog',
        'fields': 'created,resolutiondate'
    }

    # Получение данных из JIRA
    response = requests.get(url, params=payload)
    data = json.loads(response.text)

    # Словарь для хранения времени нахождения задач в различных состояниях
    state_durations = {}

    # Обработка полученных задач
    for issue in data['issues']:
        created_date = issue['fields']['created']
        resolution_date = issue['fields']['resolutiondate']

        # Преобразование строковых дат в объекты datetime
        created_dt = datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        resolution_dt = datetime.strptime(resolution_date, '%Y-%m-%dT%H:%M:%S.%f%z')

        # Журнал изменений (состояния)
        changelog = issue['changelog']['histories']

        # Для каждой задачи считаем время в каждом состоянии
        last_status_time = created_dt  # Начальное время - это время создания задачи
        last_status = None  # Состояние задачи до перехода в следующее состояние

        for change in changelog:
            for item in change['items']:
                if item['field'] == 'status':  # Когда меняется статус
                    from_status = item['fromString']
                    to_status = item['toString']
                    change_time = datetime.strptime(change['created'], '%Y-%m-%dT%H:%M:%S.%f%z')

                    # Если задача меняет статус
                    if to_status not in state_durations:
                        state_durations[to_status] = []

                    # Если задача меняет статус, то добавляем время в данном состоянии
                    if last_status is not None:
                        state_durations[last_status].append(
                            (change_time - last_status_time).total_seconds() / (60 * 60 * 24))  # в днях

                    # Обновляем время последнего статуса
                    last_status_time = change_time
                    last_status = to_status

        # Записываем время в состояние "Closed", если задача была закрыта
        if 'Closed' not in state_durations:
            state_durations['Closed'] = []

        # Для времени в состоянии "Closed" учитываем разницу между временем разрешения задачи и последним временем изменения
        time_in_state = (resolution_dt - last_status_time).total_seconds() / (60 * 60 * 24)  # в днях
        if time_in_state > 0:  # Если время больше 0, добавляем
            state_durations['Closed'].append(time_in_state)

    # Построение диаграмм для каждого состояния
    for state, durations in state_durations.items():
        plt.figure(figsize=(10, 6))
        plt.hist(durations, bins=20, edgecolor='black', color='violet')  # Лиловый цвет для гистограммы
        plt.title(f'Распределение времени задач в состоянии "{state}"')
        plt.xlabel('Время в состоянии (дни)')
        plt.ylabel('Количество задач')

        # Настроим шаг по оси X (если нужно, чтобы метки были через определенные интервалы)
        plt.xticks(range(0, int(max(durations)) + 1, 50))  # Устанавливаем шаг по оси X равным 1 дню

        plt.show()


def graf3():
    # Конфигурация
    JIRA_URL = 'https://issues.apache.org/jira/rest/api/2/search'
    PROJECT_KEY = 'KAFKA'  # Название проекта

    # Получаем текущую дату и дату два месяца назад
    today = datetime.today()
    two_months_ago = today - timedelta(days=60)

    # Форматируем даты в нужный формат (YYYY-MM-DD)
    today_str = today.strftime('%Y-%m-%d')
    two_months_ago_str = two_months_ago.strftime('%Y-%m-%d')

    # Параметры для запроса задач (фильтрация по датам)
    payload = {
        'jql': f'project={PROJECT_KEY} AND created >= "{two_months_ago_str}" AND created <= "{today_str}" ORDER BY createdDate',
        'maxResults': '1000',
        'expand': 'changelog',
        'fields': 'created,resolutiondate'
    }

    # Функция для извлечения задач из JIRA
    def get_issues():
        response = requests.get(JIRA_URL, params=payload)
        if response.status_code == 200:
            return response.json()['issues']
        else:
            print(f"Ошибка при запросе данных из JIRA: {response.status_code}")
            return []

    # Извлечение задач
    issues = get_issues()

    # Словарь для хранения данных по дням
    tasks_data = defaultdict(lambda: {'opened': 0, 'closed': 0})

    # Обработка каждой задачи
    for issue in issues:
        created_date = issue['fields']['created'][:10]  # Дата создания задачи
        resolution_date = issue['fields'].get('resolutiondate', None)  # Дата закрытия задачи

        # Увеличиваем счетчик открытых задач
        tasks_data[created_date]['opened'] += 1

        # Если задача закрыта (есть resolutiondate), увеличиваем счетчик закрытых задач
        if resolution_date:
            resolution_date = resolution_date[:10]  # Берем только дату (без времени)
            tasks_data[resolution_date]['closed'] += 1

    # Подготовка данных для построения графика
    dates = sorted(tasks_data.keys())
    opened_tasks = [tasks_data[date]['opened'] for date in dates]
    closed_tasks = [tasks_data[date]['closed'] for date in dates]

    # Накопительные итоги
    opened_cumulative = pd.Series(opened_tasks).cumsum()
    closed_cumulative = pd.Series(closed_tasks).cumsum()

    # Построение графика
    plt.figure(figsize=(12, 6))

    # График для количества открытых и закрытых задач
    plt.plot(dates, opened_tasks, label='Открытые задачи', color='blue')
    plt.plot(dates, closed_tasks, label='Закрытые задачи', color='red')

    # График для накопительного итога
    plt.plot(dates, opened_cumulative, label='Накопительный итог по открытым задачам', color='blue', linestyle='--')
    plt.plot(dates, closed_cumulative, label='Накопительный итог по закрытым задачам', color='red', linestyle='--')

    # Оформление графика
    plt.title('Количество открытых и закрытых задач в проекте KAFKA (за последние 2 месяца)')
    plt.xlabel('Дата')
    plt.ylabel('Количество задач')

    # Установка шага для меток по оси X (например, 1 неделя)
    plt.xticks(pd.to_datetime(dates)[::7].strftime('%Y-%m-%d'), rotation=45)  # Показать каждую неделю

    # Добавление сетки и легенды
    plt.grid(True)
    plt.legend()

    # Подгонка графика для отображения
    plt.tight_layout()

    # Показать график
    plt.show()

def graf3_1():
    # Конфигурация
    JIRA_URL = 'https://issues.apache.org/jira/rest/api/2/search'
    PROJECT_KEY = 'KAFKA'  # Название проекта

    # Получаем текущую дату и дату два месяца назад
    today = datetime.today()
    two_months_ago = today - timedelta(days=60)

    # Форматируем даты в нужный формат (YYYY-MM-DD)
    today_str = today.strftime('%Y-%m-%d')
    two_months_ago_str = two_months_ago.strftime('%Y-%m-%d')

    # Параметры для запроса задач (фильтрация по датам)
    payload = {
        'jql': f'project={PROJECT_KEY} AND created >= "{two_months_ago_str}" AND created <= "{today_str}" ORDER BY createdDate',
        'maxResults': '1000',
        'expand': 'changelog',
        'fields': 'created,resolutiondate'
    }

    # Функция для извлечения задач из JIRA
    def get_issues():
        response = requests.get(JIRA_URL, params=payload)
        if response.status_code == 200:
            return response.json()['issues']
        else:
            print(f"Ошибка при запросе данных из JIRA: {response.status_code}")
            return []

    # Извлечение задач
    issues = get_issues()

    # Словарь для хранения данных по дням
    tasks_data = defaultdict(lambda: {'opened': 0, 'closed': 0})

    # Обработка каждой задачи
    for issue in issues:
        created_date = issue['fields']['created'][:10]  # Дата создания задачи
        resolution_date = issue['fields'].get('resolutiondate', None)  # Дата закрытия задачи

        # Увеличиваем счетчик открытых задач
        tasks_data[created_date]['opened'] += 1

        # Если задача закрыта (есть resolutiondate), увеличиваем счетчик закрытых задач
        if resolution_date:
            resolution_date = resolution_date[:10]  # Берем только дату (без времени)
            tasks_data[resolution_date]['closed'] += 1

    # Подготовка данных для построения графика
    dates = sorted(tasks_data.keys())
    opened_tasks = [tasks_data[date]['opened'] for date in dates]
    closed_tasks = [tasks_data[date]['closed'] for date in dates]

    # Построение графика
    plt.figure(figsize=(12, 6))

    # График для количества открытых и закрытых задач
    plt.plot(dates, opened_tasks, label='Открытые задачи', color='blue', marker='o')
    plt.plot(dates, closed_tasks, label='Закрытые задачи', color='red', marker='o')

    # Оформление графика
    plt.title('Количество открытых и закрытых задач в проекте KAFKA (за последние 2 месяца)')
    plt.xlabel('Дата')
    plt.ylabel('Количество задач')

    # Установка шага для меток по оси X (например, 1 неделя)
    plt.xticks(pd.to_datetime(dates)[::7].strftime('%Y-%m-%d'), rotation=45)  # Показать каждую неделю

    # Добавление сетки и легенды
    plt.grid(True)
    plt.legend()

    # Подгонка графика для отображения
    plt.tight_layout()

    # Показать график
    plt.show()

def graf4():
    # Конфигурация
    JIRA_URL = 'https://issues.apache.org/jira/rest/api/2/search'
    PROJECT_KEY = 'KAFKA'  # Название проекта

    # Параметры для запроса задач
    payload = {
        'jql': f'project={PROJECT_KEY} ORDER BY createdDate',
        'maxResults': '1000',  # Мы получаем максимум 1000 задач
        'fields': 'assignee,reporter'
    }

    # Функция для извлечения задач из JIRA
    def get_issues():
        response = requests.get(JIRA_URL, params=payload)
        if response.status_code == 200:
            return response.json()['issues']
        else:
            print(f"Ошибка при запросе данных из JIRA: {response.status_code}")
            return []

    # Извлечение задач
    issues = get_issues()

    # Словарь для подсчета задач для каждого пользователя
    user_task_count = defaultdict(int)

    # Обработка каждой задачи
    for issue in issues:
        assignee = issue['fields'].get('assignee', None)  # Исполнитель
        reporter = issue['fields'].get('reporter', None)  # Репортер

        if assignee:
            assignee_name = assignee['displayName']
            user_task_count[assignee_name] += 1  # Увеличиваем счетчик для исполнителя

        if reporter:
            reporter_name = reporter['displayName']
            user_task_count[reporter_name] += 1  # Увеличиваем счетчик для репортера

    # Сортировка пользователей по количеству задач (от большего к меньшему)
    sorted_users = sorted(user_task_count.items(), key=lambda x: x[1], reverse=True)

    # Выбираем топ 30 пользователей
    top_30_users = sorted_users[:30]

    # Подготовка данных для графика
    users = [user[0] for user in top_30_users]
    task_counts = [user[1] for user in top_30_users]

    # Построение графика
    plt.figure(figsize=(12, 8))
    plt.barh(users, task_counts, color='violet')

    # Оформление графика
    plt.title('Топ-30 пользователей с максимальным количеством задач в проекте KAFKA')
    plt.xlabel('Количество задач')
    plt.ylabel('Имя пользователя')

    # Добавление сетки
    plt.grid(True)

    # Подгонка графика для отображения
    plt.tight_layout()

    # Показать график
    plt.show()

def graf5():
    # Конфигурация
    JIRA_URL = 'https://issues.apache.org/jira/rest/api/2/search'
    PROJECT_KEY = 'KAFKA'  # Название проекта

    # Параметры для запроса задач (только закрытые задачи)
    payload = {
        'jql': f'project={PROJECT_KEY} AND status=Closed ORDER BY createdDate',
        'maxResults': '1000',  # Мы получаем максимум 1000 задач
        'fields': 'worklog'  # Включаем worklog, чтобы получить залогированное время
    }

    # Функция для извлечения задач из JIRA
    def get_issues():
        response = requests.get(JIRA_URL, params=payload)
        if response.status_code == 200:
            return response.json()['issues']
        else:
            print(f"Ошибка при запросе данных из JIRA: {response.status_code}")
            return []

    # Извлечение задач
    issues = get_issues()

    # Проверяем, сколько задач получено и содержат ли они worklog
    print(f"Найдено {len(issues)} задач в проекте {PROJECT_KEY}.")
    if len(issues) > 0:
        print("Пример одной задачи:", issues[0])

    # Словарь для подсчета количества задач по времени
    time_data = defaultdict(int)

    # Обработка каждой задачи
    for issue in issues:
        worklog = issue['fields'].get('worklog', None)  # Залогированное время

        # Проверим, если в задаче есть worklog
        if worklog and 'worklogs' in worklog:
            total_time_spent = 0
            # Пройдем по всем worklog и суммируем время
            for log in worklog['worklogs']:
                time_spent_seconds = log['timeSpentSeconds']  # Время в секундах
                total_time_spent += time_spent_seconds  # Суммируем время для задачи

            if total_time_spent > 0:
                # Увеличиваем счетчик задач для этого времени
                time_data[total_time_spent] += 1
        else:
            print(f"Задача {issue['key']} не имеет worklog.")

    # Проверяем, что данные накоплены
    print(f"Найдено {len(time_data)} различных временных значений для задач.")

    # Если данных нет, сообщим пользователю
    if len(time_data) == 0:
        print("Нет данных о залогированном времени для задач.")
    else:
        # Преобразуем данные в список времени (в часах)
        time_in_hours = [time / 3600 for time in time_data.keys()]  # Переводим время из секунд в часы
        task_counts = [count for count in time_data.values()]

        # Построение гистограммы
        plt.figure(figsize=(12, 6))
        plt.hist(time_in_hours, bins=30, color='skyblue', edgecolor='black')

        # Оформление графика
        plt.title('Распределение времени, затраченного на выполнение задач в проекте KAFKA')
        plt.xlabel('Время (часы)')
        plt.ylabel('Количество задач')

        # Добавление сетки
        plt.grid(True)

        # Подгонка графика для отображения
        plt.tight_layout()

        # Показать график
        plt.show()


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

#graf1()
#graf2()
#graf3_1()
#graf4()
graf5()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
