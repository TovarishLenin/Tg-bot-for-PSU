import sqlite3 as sql

con = sql.connect('skin_bot.db')
cur = con.cursor()

# Открываем изображение в бинарном режиме
with open("8.jpg", 'rb') as file:
    image_data = file.read()

text = ("Уход за сухой кожей может быть доступным и эффективным! "
        "Вот твоя косметика для сухой кожи в бюджетном сегменте:\n"
        "- Очищение: <a href='https://goldapple.ru/9411100008-shea-butter'>FRUDIA"
        " my orchard shea butter mochi cleansing foam</a>\n"
        "- Увлажнение: <a href='https://goldapple.ru/19000028594-intensive-moisture'>ARAVIA "
        "PROFESSIONAL intensive moisture</a>\n"
        "- Питание: <a href='https://goldapple.ru/19000032951-cera-moisture-cream'>ARAVIA PROFESSIONAL cera-moisture cream</a>"
        "")


"Бюджетный	Люкс"
"Сухой	Нормальный	Комбинированный	Жирный"

# Сохраняем в базу данных
cur.execute("""
    INSERT INTO otvet (kojza, budjet, image, text)
    VALUES (?, ?, ?, ?)
""", ("Сухой", "Бюджетный", sql.Binary(image_data), text))

con.commit()
con.close()