# data-parser — парсер статей блога с сохранением в SQLite

Скрипт на Python, который собирает статьи с блога, извлекает заголовки и текст, а затем сохраняет их в базу данных SQLite с защитой от дубликатов.

## Возможности

- Сбор статей с веб-страницы через `requests` + `BeautifulSoup`
- Извлечение заголовка и текста каждой статьи
- Сохранение в SQLite с защитой от повторов (`UNIQUE` + `INSERT OR IGNORE`)
- ООП-модель данных с сериализацией (`to_dict` / `from_dict`)
- Обработка сетевых ошибок и таймаутов
- Выборка последних записей из БД
- Понятный вывод в консоль на каждом этапе

## Стек

- Python 3.9+
- `requests` — HTTP-запросы
- `beautifulsoup4` — парсинг HTML
- `sqlite3` — встроенная БД (без внешних зависимостей)

## Установка

```bash
git clone https://github.com/your-username/blog-parser.git
cd data-parser
pip install -r requirements.txt
