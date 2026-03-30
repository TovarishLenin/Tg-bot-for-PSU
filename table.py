import sqlite3 as sql

con = sql.connect('skin_bot.db')
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS basa_polz (
        id ШВ,
        name TEXT,
        rating NUMBER
       )""")

# Создаем временную таблицу с новой структурой
cur.execute("""CREATE TABLE IF NOT EXISTS opros (
    vopros TEXT,
    variant1 TEXT,
    variant2 TEXT,
    variant3 TEXT,
    variant4 TEXT
    )""")

# Создаем временную таблицу с новой структурой
cur.execute("""CREATE TABLE IF NOT EXISTS answer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            answer1 TEXT,
            answer2 TEXT,
            answer3 TEXT,
            FOREIGN KEY (user_id) REFERENCES basa_polz(id),
            UNIQUE(user_id)
        )""")

cur.execute("""CREATE TABLE IF NOT EXISTS otvet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kojza TEXT,
    budjet TEXT,
    image BLOB,
    text TEXT
        )""")



con.commit()

