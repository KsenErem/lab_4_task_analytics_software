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
import datetime

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
        created_dt = datetime.datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        resolution_dt = datetime.datetime.strptime(resolution_date, '%Y-%m-%dT%H:%M:%S.%f%z')

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
        created_dt = datetime.datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        resolution_dt = datetime.datetime.strptime(resolution_date, '%Y-%m-%dT%H:%M:%S.%f%z')

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
                    change_time = datetime.datetime.strptime(change['created'], '%Y-%m-%dT%H:%M:%S.%f%z')

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
    today = datetime.datetime.today()
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
    today = datetime.datetime.today()
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

def get_issue_item_to_time(issue, field, to):
    time_list = []
    for history in issue['changelog']['histories']:
        for item in history['items']:
            if item['field'] == field and (item['toString'] == to or item['to'] == to):
                time_list.append(datetime.datetime.strptime(history['created'], '%Y-%m-%dT%H:%M:%S.%f%z'))
    return time_list

def get_resolved_time_for_assignee(issue, username):
    l_start = get_issue_item_to_time(issue, 'assignee', username)
    if l_start == []:
        time_start = datetime.datetime.strptime(issue['fields']['created'], '%Y-%m-%dT%H:%M:%S.%f%z')
    else:
        time_start = l_start[-1]

    l_stop = get_issue_item_to_time(issue, 'status', 'Resolved')
    if l_stop == []:
        time_stop = datetime.datetime.strptime(issue['fields']['resolutiondate'], '%Y-%m-%dT%H:%M:%S.%f%z')
    else:
        time_stop = l_stop[-1]

    time = time_stop - time_start

    return time.total_seconds() / 3600

def graf5(username):
    #username = 'nehanarkhede'
    list_5 = []
    payload = {'jql': 'project=KAFKA AND status=Closed AND NOT assignee=null', 'maxResults': '1000',
               'fields': 'assignee'}

    response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=payload)
    data = json.loads(response.text)
    for elem in data['issues']:
        assignee = elem['fields']['assignee']['key']
        list_5.append(assignee)

    counted_values = Counter(list_5)
    print(counted_values)

    ##################

    payload = {'jql': f'project=KAFKA AND status=Closed AND assignee={username}', 'maxResults': '1000',
               'expand': 'changelog',
               'fields': 'resolutiondate,created'}

    response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=payload)
    data = json.loads(response.text)

    times_list = []

    for elem in data['issues']:
        times_list.append(get_resolved_time_for_assignee(elem, username))

    plt.hist(times_list, bins=100, edgecolor='black', color='violet')

    plt.title(f'Гистограмма: пользователь {username}')
    plt.xlabel('Время решения (часы)')
    plt.ylabel('Количество задач')
    # Добавление сетки
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def graf6():
    list_x = ['Trivial', 'Minor', 'Major', 'Critical', 'Blocker']
    list_y = []
    for prio in list_x:
        payload = {'jql': f'project=KAFKA AND priority = {prio}', 'maxResults': '1', 'fields': 'priority'}
        response = requests.get('https://issues.apache.org/jira/rest/api/2/search', params=payload)
        data = json.loads(response.text)
        list_y.append(int(data['total']))


    plt.plot(list_y, linewidth=3.0, color='violet')
    plt.title(f'График количество задач по степени серьезности')
    plt.xlabel('Приоритет')
    plt.ylabel('Количество задач')
    x_list = [0, 1, 2, 3, 4]
    plt.grid(True)
    plt.yticks(list_y)
    plt.xticks(x_list, labels=list_x)
    plt.show()