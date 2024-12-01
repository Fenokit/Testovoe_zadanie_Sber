import json
from datetime import datetime
from datetime import timedelta
import webbrowser
import os

# Открываем файл и загружаем JSON
with open('тестовое_.json', 'r') as file:
    data = json.load(file)

# Создаем CSS и Код для вставки
paste_code_html = '''<h1>Тестовое задание 1.</h1>
                    <h2>Ккач - 80%</h2>'''
css_code = '''
    <style>
        table {
            width: 100%;
            border-collapse: collapse;            
        }
        th, td {                
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>'''

# Использование данных
num = timedelta(0)
markers = {}
for el in data:
    # Находим время выполнения задачи
    time_marker = datetime.fromisoformat(el['end_date']) - datetime.fromisoformat(el['start_date'])

    # Группируем задачи по разметчикам
    if el['marker_id'] in markers.keys():
        markers[el['marker_id']].update({el['assignment_id']: [el['status'], el['file_name'],
                                                               el['price'], time_marker]})
    else:
        markers.update({el['marker_id']: {el['assignment_id']: [el['status'], el['file_name'],
                                                                el['price'], time_marker]}})

# Создаем HTML
for index_marker, marker in enumerate(markers):
    total_do_tasks = 0
    total_accepted_tasks = 0
    total_time = timedelta(0)
    total_price = 0
    for index, assignment_id in enumerate(markers[marker].values()):
        if index == 0:
            paste_code_html += f'''
            <h2>Разметчик '{marker}'</h2>
            <table>
            <tr>
                <th>№</th>
                <th>Cтатус</th>
                <th>Наименование задачи</th>
                <th>Стоимость</th>
                <th>Время выполнения</th>
            </tr>'''
        paste_code_html += f'''
            <tr>
                <td>{index+1}</td>
                <td>{assignment_id[0]}</td>
                <td>{assignment_id[1]}</td>
                <td>{assignment_id[2]}</td>
                <td>{assignment_id[3]}</td>
            </tr>'''
        if assignment_id[0] != 'EXPIRED':
            total_do_tasks += 1
            total_time += assignment_id[3]
            if assignment_id[0] == 'ACCEPTED':
                total_accepted_tasks += 1
                total_price += assignment_id[2]
    try:
        krez = total_accepted_tasks / total_do_tasks
        md_time = total_time/total_do_tasks
    except ZeroDivisionError:
        krez = 0
        md_time = 0

    paste_code_html += f'''<tr>
                                <th>Крез</th>
                                <th>{round(krez, 3)}</th>
                                <th></th>
                                <th>{total_price}</th>
                                <th>{md_time}</th>
                            </tr>
                            </table>'''
    if krez < 0.8 and total_do_tasks >= 2:
        paste_code_html += f'''<h3>Разметчику "{marker}" срочно требуется ОС</h3>'''
    elif total_do_tasks < 2:
        paste_code_html += f'''<h3>Недостаточно для ОС, возможно Разметчик 
        "85251795-70c8-4d40-86b2-e7215e9dae4b" мало сделал</h3>'''
    else:
        paste_code_html += f'''<h3>Разметчик "{marker}" прекрасно справляется</h3>'''

index_html = f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Таблица с данными</title>
        {css_code}
    </head>
    <body>
        {paste_code_html}
    </body>
    </html>'''

# Сохранение HTML в файл
file_path = 'index.html'
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(index_html)

# Открытие HTML-файла в браузере
webbrowser.open('file://' + os.path.realpath(file_path))
