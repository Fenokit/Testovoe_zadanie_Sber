from IPython.display import Markdown
from crowd_sdk.tagme import TagmeClientAdvanced
from crowd_sdk.tagme.types import MethodData, MethodForms
from crowd_sdk.tagme.types import TaskDataRequest, TaskType

import aiohttp
import asyncio
import pandas as pd
import json


async def download_text(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        return await resp.text()


# Initializing the client
client = TagmeClientAdvanced("crowd.cfg")

url_project = "https://tagme.sberdevices.ru/company/7b7c35ee-f08b-42f5-a9c4-1de787c65216/" \
              "project/7e73c4cb-b153-41ed-ae30-f7a1cd95e42e"


# Creating our own project using the SDK
async def first_task():
    project = await client.create_project(
        name="Настроение текста",
        description="Разметка того, какие чувства передаёт текст",
        inner_comment="Внутренний комментарий для заказчика",
    )

    project_link = await client.gen_project_url(project.uid, project.organization_id)
    Markdown(f'**[https://tagme.sberdevices.ru/'
             f'company/d9d24126-e268-4a7e-bb83-8ee9123e0ef7/'
             f'project/34b229eb-10be-4393-9feb-2173339ce2b7]({project_link})**')

    # Adding the instructions and the interface
    marker_brief = """
        <h1> Инструкция по проекту </h1>
        <ul>
        <li>1. Помнить 2 правило</li>
        <li>2. Не забывать 1 правило</li>
        </ul>
    """

    html = """
    <tm-block title="Прочитайте текст">
        <tm-html html="{{text}}"></tm-html>
        <tm-title subTitle="Какое-то доп описание">Выберите эмоциональный контекст сообщения:</tm-title>
        <tm-radio name="emotion" label="Нейтральный" value="1" hotkey="1"></tm-radio>
        <tm-radio name="emotion" label="Агрессивный" value="2" hotkey="2"></tm-radio>
        <tm-radio name="emotion" label="Веселый" value="3" hotkey="3"></tm-radio>
    </tm-block>
    """

    css = """
    .tm-block {
    width: 90% !important;
    }
    """

    js = """
    exports.Task = class Task extends exports.Task {
      validate() {
        const radioButtons = Array.from(document.querySelectorAll('input[type="radio"]'));
    
        if (radioButtons.every(e => !e.checked)) {
          return this.validationError('Вы не выбрали ни одного ответа.');
        }
    
        return true;
      }
    };
    """

    forms = MethodForms(
        html=html,
        css=css,
        js=js,
        example={"text": "Посмотри какая стоимость, это ВСË РАДИ ТЕБЯ <3"}
    )

    method = MethodData(
        uid=project.method_id,
        name="Название методики",
        forms=forms,
        marker_brief=marker_brief,
    )

    await client.update_method(method=method)
    Markdown(f'**[https://tagme.sberdevices.ru/company/7b7c35ee-f08b-42f5-a9c4-1de787c65216/'
             f'project/d8838fdf-c906-4e75-82f1-f3340e36c7c0/forms]({project_link}/forms)**')


async def second_task():
    project = await client.update_project(
        project_id="fe482b6f-108d-4d43-b4c1-d2a9fb8136ca",
        name='Настроение текста',
        organization_id="7b7c35ee-f08b-42f5-a9c4-1de787c65216")

    # Adding a task to the project
    for el in '321':
        create_task_request = TaskDataRequest(
            project_id=project.uid,
            organization_id=project.organization_id,
            name=el,
            price=99999,
            type=TaskType.PROD,  # or TaskType.STUDY | TaskType.EXAM
            description="Описание задачи",
        )

        task = await client.create_task(create_task_request)

        task_link = await client.gen_task_url(task.project_id, task.uid, task.organization_id)
        Markdown(f'**[{url_project}]({task_link})**')


async def three_and_four_tasks():
    project = await client.update_project(
        project_id="fe482b6f-108d-4d43-b4c1-d2a9fb8136ca",
        name='Настроение текста',
        organization_id="7b7c35ee-f08b-42f5-a9c4-1de787c65216")

    tasks = await client.get_tasks(project_id=project.uid)
    for el in tasks:
        if el.name == '1':
            el.overlap = 82
        elif el.name == '2':
            el.priority = 82

        await client.remove_task(el.uid)
        await client.create_task(el)


async def five_task():
    project = await client.update_project(
        project_id="fe482b6f-108d-4d43-b4c1-d2a9fb8136ca",
        name='Настроение текста',
        organization_id="7b7c35ee-f08b-42f5-a9c4-1de787c65216"
    )

    # Определяем имена файлов
    tasks_data = [
        {"text": 'Солнце такое классное!!'},
        {"text": 'Мерзкая погода!'},
        {"text": 'На улице облачно!'}
    ]

    # Создаём файлы и записываем в них данные
    name_files = []
    for el, data in enumerate(tasks_data):
        name_file = f'Задание {el + 1}.txt'
        with open(name_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))
        name_files.append(name_file)

    #
    tasks = await client.get_tasks(project_id=project.uid)
    for task in tasks:
        if task.name == '3':
            await client.upload_files(task.uid, name_files)


async def elsen_tasks():
    projects = await client.get_projects()

    # Находим нужный проект и получаем его задачи
    project = next((p for p in projects if p.name == 'Тестовый проект'), None)

    if project:
        tasks = await client.get_project_tasks(project.uid)
        # Находим нужную задачу
        task = next((t for t in tasks if t.name == 'task' or t.name == 'start/stop task'), None)

        if task.name == "task":
            results = await client.get_task_assignments_df(task.uid)
            df = pd.DataFrame(results)
            df.to_excel('output.xlsx', index=False)

        elif task.name == "start/stop task":
            # Узнаем состояние задачи
            status_task = await client.get_task_info(task.uid)

            # 7 task
            if not status_task['is_blocked']:
                await client.start_task(task.uid)

            # 8 task
            else:
                await client.stop_task(task.uid)


asyncio.run(elsen_tasks())
