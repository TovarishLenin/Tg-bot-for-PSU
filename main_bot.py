import telebot
from telebot import types
import sqlite3 as sql
import time

bot = telebot.TeleBot('7540398947:AAHgBNmHGq1A0iUGgAXfGdiUGFexdW8DpKY')

markup_start = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn = types.KeyboardButton('Начать')

con = sql.connect('skin_bot.db')
cur = con.cursor()
user_questions = {}
def get_db_connection():
    return sql.connect('skin_bot.db')

def execute_query(query, params=()):
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute(query, params)
        result = cur.fetchall()
        con.commit()
        return result
    finally:
        con.close()

# Создаем главное меню один раз
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton('Опрос')
    btn2 = types.KeyboardButton('Каталог')
    btn3 = types.KeyboardButton('О нас')
    btn4 = types.KeyboardButton('Поддержка')
    btn5 = types.KeyboardButton('Справка')
    markup.row(btn1)
    markup.row(btn2, btn3)
    markup.row(btn4, btn5)
    return markup

def add_return_button():
    markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup_menu.add(types.KeyboardButton('Вернуться в меню'))
    return markup_menu

@bot.message_handler(commands=['start', 'restart'])
def start(message: types.Message):
    markup = get_main_menu()
    bot.send_message(message.chat.id,
                    f"Привет, {message.from_user.first_name}! 👋 "
                    f"Мы — бот для подбора косметики от «Золотое Яблоко». "
                    f"Здесь ты можешь найти идеальные продукты для своего типа кожи. "
                    f"Мы готовы помочь тебе сделать правильный выбор и подобрать самые подходящие средства.\n"
                    f"Ты знаешь свой тип кожи? 🌟 Давай начнем!",
                    reply_markup=markup)

    name_polsovatel = str(message.from_user.id)
    result = execute_query('SELECT id, name FROM basa_polz WHERE id =?', (name_polsovatel,))
    if not result:
        execute_query('INSERT INTO basa_polz (id, name) VALUES(?, ?)', (message.from_user.id, message.from_user.first_name,))

    cn = sql.connect('skin_bot.db')
    cr = cn.cursor()
    cr.execute('SELECT * FROM basa_polz')
    name = cr.fetchall()

@bot.message_handler(func=lambda message: message.text.lower() == "каталог")
@bot.message_handler(commands=["go_site"])
def catalog(message: types.Message):
    message_text = ('Можете посмотреть ассортимент товаров в онлайн-магазине "Золотое Яблоко." <a href="https://goldapple.ru/" style="color: #3498db; text-shadow: 0 '
                    '1px #2980b9, 0 2px #2980b9, 0 3px #2980b9, 0 4px #2980b9, 0 5px #2980b9; font-weight: bold; font-family: Arial, sans-serif;">Перейти на сайт</a>')
    markup_back = add_return_button()
    bot.reply_to(message, message_text, parse_mode='HTML', reply_markup=markup_back)

@bot.message_handler(func=lambda message: message.text.lower() == "поддержка")
@bot.message_handler(commands=["help"])
def help(message: types.Message):
    markup_back = add_return_button()
    bot.send_message(message.chat.id,'По всем вопросам обращаться в Telegram:\n'
                                    'Дмитрий Дроздов: @drozdd3', reply_markup=markup_back)


@bot.message_handler(func=lambda message: message.text.lower() == "о нас")
@bot.message_handler(commands=["about_us"])
def about_us(message: types.Message):
    markup_back = add_return_button()
    bot.send_message(message.chat.id, 'Мы команда студентов 2 курса образовательной программы '
                                    '"Бизнес-информатика" ПГНИУ - Пермь.\n'
                                    'Данный бот предназначен для подбора уходовой косметики '
                                    'для лица.', reply_markup=markup_back)


@bot.message_handler(func=lambda message: message.text.lower() == "справка")
def send_spravka(message: types.Message):
    markup_back = add_return_button()
    bot.send_message(message.chat.id, 'С помощью бота ты можешь пройти опрос, '
                                      'получить подборку косметики, узнать о нас и перейти'
                                      ' в каталог. Все просто!', reply_markup=markup_back)


@bot.message_handler(func=lambda message: message.text.lower() == "опрос")
@bot.message_handler(commands=["opros"])
def survey(message: types.Message):
    """Функция для проведения опроса и сохранения ответов"""
    markup_back = add_return_button()
    questions = execute_query('SELECT * FROM opros')

    if not questions:
        bot.send_message(message.chat.id,
                         'Ошибка: В базе данных нет вопросов для опроса.',
                         reply_markup=markup_back)
        return

    # Проверяем существующие ответы
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM answer WHERE user_id=?', (message.chat.id,))
        exists = cursor.fetchone()[0] > 0

        if exists:
            # Получаем существующие ответы
            cursor.execute('SELECT * FROM answer WHERE user_id=?', (message.chat.id,))
            existing_answers = cursor.fetchone()

            # Формируем текст с существующими ответами
            result_text = "У вас уже есть сохраненные ответы в базе данных:\n\n"
            result_text += f"Знаете ли свой тип кожи лица?:\n*{existing_answers[2]}*\n"
            result_text += f"Какой у вас тип кожи лица?:\n*{existing_answers[3]}*\n"
            result_text += f"Какой у вас бюджет?:\n*{existing_answers[4]}*\n\n"
            result_text += "Хотите начать новый опрос?"

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(types.KeyboardButton('Да'))
            markup.add(types.KeyboardButton('Нет'))
            bot.send_message(message.chat.id, result_text, reply_markup=markup, parse_mode="Markdown")
            return

    except Exception as e:
        print(f"Ошибка при проверке существующих ответов: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при проверке данных.")
        return
    finally:
        if conn is not None:
            conn.close()

    # Начинаем новый опрос
    global user_questions
    user_questions[message.chat.id] = {
        'answers': [],
        'question_index': 2
    }
    send_next_question(message.chat.id, questions)


def send_next_question(chat_id, questions):
    """Отправляет следующий вопрос или завершает опрос"""
    if chat_id not in user_questions:
        return_to_menu(chat_id)
        return True

    survey_state = user_questions[chat_id]

    # Если достигнут конец вопросов, завершаем опрос
    if survey_state['question_index'] < 0:
        finish_survey(chat_id)
        return

    # Получаем текущий вопрос
    current_question = questions[survey_state['question_index']]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    # Добавляем только существующие варианты ответов
    variants = [current_question[1], current_question[2], current_question[3], current_question[4]]
    for variant in variants:
        if variant is not None:
            markup.add(types.KeyboardButton(str(variant)))

    # Отправляем сообщение и получаем его ID
    msg = bot.send_message(chat_id, f'{current_question[0]}', reply_markup=markup)

    # Регистрируем следующий обработчик
    bot.register_next_step_handler(msg, lambda msg: handle_answer(msg, chat_id, questions))

@bot.message_handler(func=lambda message: message.text.lower() == "нет")
def handle_no_answer(message: types.Message):
    """Обработчик ответа 'нет' при наличии существующих данных"""
    markup = get_main_menu()
    bot.send_message(message.chat.id, "Хорошо, вы можете продолжить пользоваться ботом.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.lower() == "да")
def handle_yes_answer(message: types.Message):
    """Обработчик ответа 'да' при наличии существующих данных"""
    chat_id = message.chat.id
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Удаляем существующие ответы
        cursor.execute('DELETE FROM answer WHERE user_id=?', (chat_id,))
        conn.commit()

        # Запускаем новый опрос
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Опрос'))
        bot.send_message(chat_id, 'Начинаем новый опрос!', reply_markup=markup)

    except Exception as e:
        print(f"Ошибка при удалении данных: {e}")
        bot.send_message(chat_id, "Произошла ошибка при удалении данных.")
    finally:
        if conn is not None:
            conn.close()

def handle_answer(message, chat_id, questions):
    """Обрабатывает ответ пользователя"""
    # Проверяем, находится ли пользователь в процессе опроса
    if chat_id not in user_questions:
        return_to_menu(chat_id)
        return True

    if message.text == "Нет":
        with open("11.jpg", 'rb') as file:
            img = file.read()
        bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption="Чтобы определить свой тип кожи, следуйте этим шагам:\n\n"
                    "1. Умой лицо и подожди 1-2 часа.\n"
                    "2. Наблюдай:\n"
                    "    *Сухая*: стянутость и шелушение.\n"
                    "    *Жирная*: блестящая Т-зона и расширенные поры\n"
                    "    *Комбинированная*: жирная Т-зона и сухие щеки.\n"
                    "    *Нормальная*: здоровый и гладкий вид.\n\n"
                    "Если не уверена, обратись к специалисту!",
            parse_mode="Markdown")

    #Сохраняем ответ
    user_questions[chat_id]['answers'].append(message.text)

    # Увеличиваем индекс вопроса
    user_questions[chat_id]['question_index'] -= 1

    # Переходим к следующему вопросу или завершаем опрос
    send_next_question(chat_id, questions)


def finish_survey(chat_id):
    """Завершает опрос и сохраняет результаты"""
    survey_state = user_questions.pop(chat_id, None)
    if not survey_state:
        return_to_menu(chat_id)
        return True

    # Сохраняем ответы в базу данных
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, есть ли уже ответы для пользователя
        cursor.execute('SELECT COUNT(*) FROM answer WHERE user_id=?', (chat_id,))
        exists = cursor.fetchone()[0] > 0

        if exists:
            # Если ответы уже есть, показываем сообщение
            result_text = "У вас уже есть сохраненные ответы в базе данных.\n" \
                         "Хотите начать новый опрос?"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(types.KeyboardButton('Да'))
            markup.add(types.KeyboardButton('Нет'))
            bot.send_message(chat_id, result_text, reply_markup=markup)
            return

        # Если нет существующих ответов, сохраняем новые
        query = """INSERT INTO answer (answer1, answer2, answer3, user_id)
                   VALUES (?, ?, ?, ?)"""
        answers = survey_state['answers']
        params = (*answers, chat_id)

        cursor.execute(query, params)
        conn.commit()

        result_text = "Спасибо за участие в опросе!\nВаши ответы успешно сохранены."

        # Показываем персональную справку
        if not show_personal_spravka(chat_id, cursor):
            markup = get_main_menu()

    except Exception as e:
        print(f"Ошибка при сохранении ответов: {e}")
        result_text = "Спасибо за участие в опросе!\nИзвините, возникла ошибка при сохранении ответов."
    finally:
        if conn is not None:
            conn.close()

    markup = get_main_menu()
    bot.send_message(chat_id, result_text, reply_markup=markup)


def show_personal_spravka(chat_id, cursor):
    """Показывает персональную справку на основе ответов пользователя"""
    try:
        # Получаем последние ответы пользователя
        cursor.execute('SELECT answer2, answer3 FROM answer WHERE user_id = ? ORDER BY id DESC LIMIT 1', (chat_id,))
        user_answers = cursor.fetchone()

        if not user_answers:
            markup = get_main_menu()
            bot.send_message(chat_id, "Сначала пройдите опрос, чтобы получить персональные рекомендации.",
                             reply_markup=markup)
            return False

        kojza, budjet = user_answers

        # Ищем соответствующую справку
        cursor.execute('SELECT image, text FROM otvet WHERE kojza= ? AND  budjet= ?', (kojza, budjet))
        result = cursor.fetchone()

        if result:
            image_data, text = result

            # Создаем клавиатуру с кнопкой возврата
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
            markup.add(types.KeyboardButton('Вернуться в меню'))

            # Отправляем фото с текстом как подписью
            bot.send_photo(
                chat_id=chat_id,
                photo=image_data,
                caption=f"{text}",
                reply_markup=markup,
                parse_mode="HTML"
            )
            return True
        else:
            markup = get_main_menu()
            bot.send_message(chat_id,
                             "К сожалению, нет доступной справочной информации для вашего типа кожи и бюджета.",
                             reply_markup=markup)
            return False

    except Exception as e:
        print(f"Ошибка при получении справки: {e}")
        markup = get_main_menu()
        bot.send_message(chat_id, "Произошла ошибка при получении справки.", reply_markup=markup)
        return False

@bot.message_handler(func=lambda message: message.text.lower() == "вернуться в меню")
def return_to_menu(message: types.Message):
    markup = get_main_menu()
    bot.send_message(message.chat.id, "Вы вернулись в главное меню", reply_markup=markup)
    return True



def main():
    while True:
        try:
            bot.polling(none_stop=True, timeout=30)
        except Exception as e:
            print(f"Ошибка в polling: {e}")
            time.sleep(5)
            continue

if __name__ == "__main__":
    main()