import sqlite3

conn_source = sqlite3.connect('skin_bot.db')

conn_target = sqlite3.connect('copy.db')

try:
    conn_source = sqlite3.connect('skin_bot.db')

    conn_target = sqlite3.connect('copy.db')

    conn_source.backup(conn_target)

    print("Копирование завершено успешно!")

except sqlite3.Error as e:
    print(f"Произошла ошибка при копировании: {e}")

conn_source.close()
conn_target.close()
