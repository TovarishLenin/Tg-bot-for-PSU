import sqlite3

# Подключаемся к исходной базе данных
conn_source = sqlite3.connect('skin_bot.db')

    # Создаём подключение к новой базе данных
conn_target = sqlite3.connect('copy.db')

try:
    # Подключаемся к исходной базе данных
    conn_source = sqlite3.connect('skin_bot.db')

    # Создаём подключение к новой базе данных
    conn_target = sqlite3.connect('copy.db')

    # Выполняем операцию VACUUM INTO
    conn_source.backup(conn_target)

    print("Копирование завершено успешно!")

except sqlite3.Error as e:
    print(f"Произошла ошибка при копировании: {e}")

conn_source.close()
conn_target.close()