import unittest
from unittest.mock import patch, MagicMock
import json
import datetime
import requests
import matplotlib.pyplot as plt
from graf import graf1, graf2, graf3, graf4, graf6, graf5, get_resolved_time_for_assignee


class TestGraf1(unittest.TestCase):

    @patch('requests.get')
    @patch('matplotlib.pyplot.show')
    def test_graf1(self, mock_show, mock_get):
        # Подготовим фиктивный ответ от JIRA
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'issues': [
                {
                    'fields': {
                        'created': '2024-01-01T00:00:00.000+0000',
                        'resolutiondate': '2024-01-05T00:00:00.000+0000'
                    }
                },
                {
                    'fields': {
                        'created': '2024-02-01T00:00:00.000+0000',
                        'resolutiondate': '2024-02-03T00:00:00.000+0000'
                    }
                }
            ]
        })

        # Настроим мок для requests.get
        mock_get.return_value = mock_response

        # Запускаем тестируемую функцию
        graf1()

        # Проверка, что requests.get был вызван с нужным URL и параметрами
        mock_get.assert_called_once_with(
            'https://issues.apache.org/jira/rest/api/2/search',
            params={
                'jql': 'project=KAFKA AND status=Closed ORDER BY createdDate',
                'maxResults': '1000',
                'expand': 'changelog',
                'fields': 'created,resolutiondate'
            }
        )

        # Проверка, что plt.show() был вызван для отображения графика
        mock_show.assert_called_once()

        # Можно проверить расчет продолжительности задач (для дополнительной уверенности)
        # Мы ожидаем, что продолжительность задач будет [4, 2], так как:
        # - Первая задача была открыта 4 дня.
        # - Вторая задача была открыта 2 дня.
        # Поскольку гистограмма строится на основе этих данных, мы проверим, что она формируется правильно.
        # Проверим, что matplotlib был вызван для построения гистограммы
        # Мы не можем точно проверить содержимое гистограммы, но можем проверить, что был вызов метода `hist`
        with patch.object(plt, 'hist') as mock_hist:
            graf1()
            mock_hist.assert_called()


class TestGraf2(unittest.TestCase):

    @patch('requests.get')  # Мокаем вызов requests.get
    @patch('matplotlib.pyplot.show')  # Мокаем отображение графиков
    def test_graf2(self, mock_show, mock_get):
        # Мокаем ответ от API JIRA
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'issues': [
                {
                    'fields': {
                        'created': '2023-12-01T12:00:00.000+0000',
                        'resolutiondate': '2023-12-05T12:00:00.000+0000'
                    },
                    'changelog': {
                        'histories': [
                            {
                                'created': '2023-12-02T12:00:00.000+0000',
                                'items': [
                                    {'field': 'status', 'fromString': 'Open', 'toString': 'In Progress'}
                                ]
                            },
                            {
                                'created': '2023-12-04T12:00:00.000+0000',
                                'items': [
                                    {'field': 'status', 'fromString': 'In Progress', 'toString': 'Closed'}
                                ]
                            }
                        ]
                    }
                }
            ]
        })

        # Настроим мок для метода requests.get, чтобы он возвращал наш mock_response
        mock_get.return_value = mock_response

        # Вызовем функцию graf2
        graf2()

        # Проверим, что запрос к API был выполнен правильно
        mock_get.assert_called_once_with(
            'https://issues.apache.org/jira/rest/api/2/search',
            params={
                'jql': 'project=KAFKA AND status=Closed ORDER BY createdDate',
                'maxResults': '1000',
                'expand': 'changelog',
                'fields': 'created,resolutiondate'
            }
        )

        # Проверим, что метод show был вызван, чтобы отображать гистограмму
        mock_show.assert_called()

        # Дополнительно можно проверять данные, которые передаются в гистограмму,
        # для этого можно мокаить plt.hist и проверять его вызовы, если это необходимо

class TestGraf3(unittest.TestCase):

    @patch('requests.get')  # Мокаем запрос к API JIRA
    @patch('matplotlib.pyplot.show')  # Мокаем отображение графиков
    def test_graf3(self, mock_show, mock_get):
        # Мокаем ответ от API JIRA
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'issues': [
                {
                    'fields': {
                        'created': '2023-10-01T12:00:00.000+0000',
                        'resolutiondate': '2023-10-05T12:00:00.000+0000'
                    }
                },
                {
                    'fields': {
                        'created': '2023-10-02T12:00:00.000+0000',
                        'resolutiondate': '2023-10-06T12:00:00.000+0000'
                    }
                },
                {
                    'fields': {
                        'created': '2023-10-03T12:00:00.000+0000',
                        'resolutiondate': None  # Эта задача не закрыта
                    }
                }
            ]
        }

        # Настроим мок для метода requests.get, чтобы он возвращал наш mock_response
        mock_get.return_value = mock_response

        # Вызовем функцию graf3
        graf3()

        # Проверим, что запрос к API был выполнен правильно
        mock_get.assert_called_once_with(
            'https://issues.apache.org/jira/rest/api/2/search',
            params={
                'jql': 'project=KAFKA AND created >= "2023-10-01" AND created <= "2023-12-01" ORDER BY createdDate',
                'maxResults': '1000',
                'expand': 'changelog',
                'fields': 'created,resolutiondate'
            }
        )

        # Проверим, что метод show был вызван, чтобы отображать график
        mock_show.assert_called()

        # Можно дополнительно проверять правильность данных в графиках, например, проверив, что были использованы нужные данные для построения графика.
        # Например, проверим, что в данных для построения графика есть дата и количество задач.
        # Для этого можно замокать plt.plot и проверить, что он был вызван с правильными данными.

        # Мокаем plt.plot, чтобы проверять вызовы
        with patch('matplotlib.pyplot.plot') as mock_plot:
            graf3()  # Запускаем снова, чтобы проверить вызовы plot

            # Проверим, что plt.plot был вызван несколько раз, так как график строится для разных линий
            self.assertGreater(mock_plot.call_count, 0)

            # Проверим, что в графике есть данные по задачам
            for call in mock_plot.call_args_list:
                args, _ = call
                # Проверяем, что данные для оси X (dates) и Y (opened_tasks, closed_tasks) были переданы в правильном формате
                self.assertTrue(isinstance(args[0], list))  # Должны быть списки для дат и задач

class TestGraf4(unittest.TestCase):

    @patch('requests.get')  # Мокаем запрос к API JIRA
    @patch('matplotlib.pyplot.show')  # Мокаем отображение графиков
    def test_graf4(self, mock_show, mock_get):
        # Мокаем ответ от API JIRA
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'issues': [
                {
                    'fields': {
                        'assignee': {'displayName': 'User1'},
                        'reporter': {'displayName': 'Reporter1'}
                    }
                },
                {
                    'fields': {
                        'assignee': {'displayName': 'User2'},
                        'reporter': {'displayName': 'Reporter2'}
                    }
                },
                {
                    'fields': {
                        'assignee': {'displayName': 'User1'},
                        'reporter': {'displayName': 'Reporter1'}
                    }
                },
                {
                    'fields': {
                        'assignee': {'displayName': 'User3'},
                        'reporter': {'displayName': 'Reporter3'}
                    }
                },
                {
                    'fields': {
                        'assignee': {'displayName': 'User2'},
                        'reporter': {'displayName': 'Reporter2'}
                    }
                }
            ]
        }

        # Настроим мок для метода requests.get, чтобы он возвращал наш mock_response
        mock_get.return_value = mock_response

        # Вызовем функцию graf4
        graf4()

        # Проверим, что запрос к API был выполнен правильно
        mock_get.assert_called_once_with(
            'https://issues.apache.org/jira/rest/api/2/search',
            params={
                'jql': 'project=KAFKA ORDER BY createdDate',
                'maxResults': '1000',
                'fields': 'assignee,reporter'
            }
        )

        # Проверим, что метод show был вызван, чтобы отображать график
        mock_show.assert_called()

        # Мокаем plt.barh, чтобы проверять, что данные передаются правильно
        with patch('matplotlib.pyplot.barh') as mock_barh:
            graf4()  # Запускаем функцию снова для проверки вызова barh

            # Проверим, что plt.barh был вызван
            mock_barh.assert_called()

            # Получаем данные, передаваемые в barh
            args, kwargs = mock_barh.call_args
            users = args[0]  # Список пользователей
            task_counts = args[1]  # Список количеств задач

            # Проверим, что пользователи и их задачи соответствуют ожиданиям
            self.assertEqual(users, ['User1', 'User2', 'User3'])  # Топ-3 пользователя
            self.assertEqual(task_counts, [2, 2, 1])  # Количество задач для каждого пользователя

class TestGraf5(unittest.TestCase):

    @patch('requests.get')  # Мокаем requests.get для API запросов
    @patch('matplotlib.pyplot.show')  # Мокаем отображение графика
    def test_graf5(self, mock_show, mock_get):
        # Мокирование ответа для первого запроса (получение всех задач)
        mock_response_1 = MagicMock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {
            'issues': [
                {'fields': {'assignee': {'key': 'user1'}}},
                {'fields': {'assignee': {'key': 'user2'}}},
                {'fields': {'assignee': {'key': 'user1'}}}
            ]
        }
        mock_get.return_value = mock_response_1

        # Мокирование ответа для второго запроса (получение задач для конкретного пользователя)
        mock_response_2 = MagicMock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {
            'issues': [
                {'fields': {'assignee': {'key': 'user1'}, 'created': '2024-01-01T00:00:00.000+0000', 'resolutiondate': '2024-01-02T00:00:00.000+0000', 'changelog': {'histories': []}}},
                {'fields': {'assignee': {'key': 'user1'}, 'created': '2024-01-01T00:00:00.000+0000', 'resolutiondate': '2024-01-03T00:00:00.000+0000', 'changelog': {'histories': []}}}
            ]
        }
        mock_get.return_value = mock_response_2

        # Мокируем работу с datetime, чтобы вернуть фиксированные значения
        with patch('graf.get_resolved_time_for_assignee') as mock_get_time:
            mock_get_time.return_value = 24  # Мокируем, что время решения задачи для пользователя - 24 часа

            # Вызовем функцию graf5 с пользователем 'user1'
            graf5('user1')

            # Проверим, что запросы к API были выполнены с правильными параметрами
            mock_get.assert_any_call(
                'https://issues.apache.org/jira/rest/api/2/search',
                params={'jql': 'project=KAFKA AND status=Closed AND NOT assignee=null', 'maxResults': '1000', 'fields': 'assignee'}
            )
            mock_get.assert_any_call(
                'https://issues.apache.org/jira/rest/api/2/search',
                params={'jql': 'project=KAFKA AND status=Closed AND assignee=user1', 'maxResults': '1000', 'expand': 'changelog', 'fields': 'resolutiondate,created'}
            )

            # Проверим, что построение графика было вызвано
            mock_show.assert_called()

            # Проверим, что данные для графика (время решения задач) передаются корректно
            with patch('matplotlib.pyplot.hist') as mock_hist:
                graf5('user1')  # Повторный вызов, чтобы проверить вызов hist

                # Проверим, что plt.hist был вызван
                mock_hist.assert_called()

                # Получаем данные, передаваемые в hist
                args, kwargs = mock_hist.call_args
                times_list = args[0]  # Список времен для оси X

                # Проверим, что в times_list находится правильное количество времени
                expected_times = [24, 24]  # Должно быть 2 задачи с временем решения 24 часа
                self.assertEqual(times_list, expected_times)

class TestGraf6(unittest.TestCase):

    @patch('requests.get')  # Мокаем запрос к API JIRA
    @patch('matplotlib.pyplot.show')  # Мокаем отображение графиков
    def test_graf6(self, mock_show, mock_get):
        # Мокаем ответ от API JIRA для каждого приоритета
        mock_response = MagicMock()
        mock_response.status_code = 200
        # mock_response.json() должен возвращать объект, который распарсится как JSON
        mock_response.json.return_value = {'total': '10'}  # Пример ответа, где всего 10 задач для каждого приоритета

        # Настроим мок для метода requests.get, чтобы он возвращал наш mock_response для каждого приоритета
        mock_get.return_value = mock_response

        # Вызовем функцию graf6
        graf6()

        # Проверим, что запросы к API были выполнены с правильными параметрами
        priorities = ['Trivial', 'Minor', 'Major', 'Critical', 'Blocker']
        for prio in priorities:
            mock_get.assert_any_call(
                'https://issues.apache.org/jira/rest/api/2/search',
                params={'jql': f'project=KAFKA AND priority = {prio}', 'maxResults': '1', 'fields': 'priority'}
            )

        # Проверим, что метод show был вызван для отображения графика
        mock_show.assert_called()

        # Мокаем plt.plot, чтобы проверять, что данные передаются правильно
        with patch('matplotlib.pyplot.plot') as mock_plot:
            graf6()  # Запускаем функцию снова для проверки вызова plot

            # Проверим, что plt.plot был вызван
            mock_plot.assert_called()

            # Получаем данные, передаваемые в plot
            args, kwargs = mock_plot.call_args
            list_y = args[0]  # Список значений для оси Y

            # Проверим, что данные на оси Y (list_y) корректны
            expected_y_values = [10, 10, 10, 10, 10]  # Каждому приоритету должно быть присвоено 10 задач
            self.assertEqual(list_y, expected_y_values)

if __name__ == '__main__':
    unittest.main()
