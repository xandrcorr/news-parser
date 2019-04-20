# News parser

Hacker News parsing service.

## Использование

Формат запроса:
http://localhost:8080/posts?[params]
где params:
- limit - число выводимых постов (целое число)
- offset - смещение (целое число)
- order - сортировка. Значение вида [order=<ключ>_<порядок>]
    - ключ - поле, по которому происходит сортировка [title, url, created]
    - порядок - порядок сортировки [asc, desc]

Пример:
http://localhost:8080/posts?limit=30&offset=5&order=created_desc


## Запуск
Запустить сервис можно как локально в виртуальном окружении, так и через docker-compose.
**Внимание!** Для локального запуска необходимо иметь на машине python3 (желательно 3.6.7, но проверено и с 3.5), python3-pip python3-venv, а так же рабочий экземпляр MongoDB. Настройки по умолчанию можно изменить с помощью переменных окружения:
- REPOSITORY_HOST - адрес экземпляра MongoDB (по умолчанию ```localhost```)
- REPOSITORY_PORT - порт MongoDB (по умолчанию ```27017```)
- REPOSITORY_DB - имя базы для хранения постов (по умолчанию ```news-storage```)
- HTTP_SERVER_PORT - порт, который слушает http-сервер (по умолчанию ```8080```)
- POST_UPDATE_TIMEOUT - таймаут до повторного запроса к hackernews. (по умолчанию ```3600``` секунд)

### Запуск сервиса локально в Linux

1. Скачать исходный код с помощью git
```
$ git clone https://github.com/xandrcorr/news-parser.git
```
2. Сгенерировать виртуальное окружение и войти в него
```
$ chmod +x ./venv-init.sh
```
```
$ ./venv-init.sh
```
```
$ source ./venv/bin/activate
```
3. Установить зависимости
```
$ pip install -r requirements.txt
```
4. Запустить сервис
```
$ python src/main.py
```
Сервис запущен, можно делать запросы к http://localhost:8080/

### Запуск сервиса в Docker
Для ленивых я собрал образ с сервисом на основе официального ```python:3.6.7```.
Чтобы запустить, необходимо скачать себе файл ```docker-compose.yml``` из репозитория, перейти в папку с ним и выполнить команду
```
$ docker-compose up
```
**Внимание!** Логично, но для запуска нужно иметь установленные Docker и docker-compose на целевой машине.
