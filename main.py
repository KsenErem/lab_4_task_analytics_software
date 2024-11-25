from jira import JIRA
import requests
import json
import numpy as np
import requests
from datetime import datetime
import matplotlib.pyplot as plt
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




def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

graf1()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
