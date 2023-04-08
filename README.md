## Celery + Flask + redis + opencv
Проект показывает работу celery, redis, flask при выполнении "долгого" запроса по обработке изображения (upscale).
<br> Реализованы методы:
<br> post - загрузка фото на обработку
<br> get - запрос по task_id о состоянии задачи (выполнена или нет)
<br> get - скачивание или отображение в браузере обработанного изображения

### Запуск:
```shell
docker-compose up
```
```shell
celery -A app.celery worker -c 2
```
<br> app.py - RUN
<br> request_example.py - RUN