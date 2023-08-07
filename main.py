import re
import sqlite3
from google_play_scraper import app



def create_table():
    # создаем подключение к базе данных
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS app_details
                      (app_id TEXT PRIMARY KEY,
                      title TEXT,
                      developer TEXT,
                      category TEXT,
                      rating REAL,
                      installs TEXT)''')
    conn.commit()
    conn.close()


def insert_app_data(app_data):
    # вставляем новую запись или обновляем данные в базе данных
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()

    #sql запрос для вставки или обновления данных
    cursor.execute('''INSERT OR REPLACE INTO app_details
                      (app_id, title, developer, category, rating, installs)
                      VALUES (?, ?, ?, ?, ?, ?)''', (
        app_data.get('appId'),
        app_data.get('title'),
        app_data.get('developer'),
        app_data.get('genre'),
        app_data.get('score'),
        remove_plus(app_data.get('installs')),
    ))

    conn.commit()
    conn.close()


def get_app_details(app_url):
    # преобразование ссылки из файла в формат, который принимает библиотека
    parts = app_url.split(' ')
    app_url = parts[-1]  # берем последний элемент - ссылку на приложение

    #извлечение идентификатора пакета из ссылки
    pattern = r'id=([\w.]+)'
    match = re.search(pattern, app_url)
    if match:
        app_id = match.group(1)
    else:
        print("Ошибка: Неверный формат ссылки на приложение.")
        return None

    try:
        # получаем данные о приложении из Google Play по его идентификатору
        app_details = app(app_id, lang='ru', country='ru')
        return app_details
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None

# убираем + из поля installs
def remove_plus(value):
    return value.replace("+", "")

def main():
    # создаем таблицу, если она не существует
    create_table()

    filename = 'gplay_urls.txt'

    with open(filename, 'r') as file:
        app_urls = file.readlines()

    for app_url in app_urls:
        app_url = app_url.strip()  # удаляем лишние пробелы и символы переноса строки
        app_data = get_app_details(app_url)

        if app_data:
            # вставляем данные о приложении в базу данных
            insert_app_data(app_data)
            print(f"Данные о приложении из ссылки {app_url} сохранены в базу данных.")
        else:
            print(f"Не удалось получить данные о приложении из ссылки {app_url}.")


if __name__ == "__main__":
    main()
