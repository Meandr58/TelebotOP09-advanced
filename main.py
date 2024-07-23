import telebot
import datetime
import time
import threading
import random
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot('6827280483:AAHsl-FGn4FB4N5Na1U-5zrJojbw7WY29I4')

# Список фактов о воде
facts = [
    "Вода на Земле может быть старше самой Солнечной системы: Исследования показывают, что от 30% до 50% воды в наших океанах возможно присутствовала в межзвездном пространстве еще до формирования Солнечной системы около 4,6 миллиарда лет назад.",
    "Горячая вода замерзает быстрее холодной: Это явление известно как эффект Мпемба. Под определенными условиями горячая вода может замерзать быстрее, чем холодная, хотя ученые до сих пор полностью не разгадали механизм этого процесса.",
    "Больше воды в атмосфере, чем во всех реках мира: Объем водяного пара в атмосфере Земли в любой момент времени превышает объем воды во всех реках мира вместе взятых. Это подчеркивает важную роль атмосферы в гидрологическом цикле, перераспределяя воду по планете."
]

# Словарь для хранения пользовательских напоминаний
user_reminders = {}
lock = threading.Lock()

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, 'Привет! Я чат бот, который будет напоминать тебе пить водичку!')
    if not any(thread.name == str(message.chat.id) for thread in threading.enumerate()):
        reminder_thread = threading.Thread(target=send_reminders, args=(message.chat.id,), name=str(message.chat.id))
        reminder_thread.start()


@bot.message_handler(commands=['fact'])
def send_random_fact(message):
    random_fact = random.choice(facts)
    bot.reply_to(message, f'Лови факт о воде: \n{random_fact}')

@bot.message_handler(commands=['set_reminder'])
def set_reminder(message):
    try:
        # Формат команды: /set_reminder HH:MM
        reminder_time = message.text.split()[1]
        datetime.datetime.strptime(reminder_time, '%H:%M')  # Проверка формата времени
        with lock:
            if message.chat.id not in user_reminders:
                user_reminders[message.chat.id] = []
            user_reminders[message.chat.id].append(reminder_time)
        bot.reply_to(message, f'Напоминание установлено на {reminder_time}')
    except (IndexError, ValueError):
        bot.reply_to(message, 'Пожалуйста, укажите время в формате HH:MM. Пример: /set_reminder 15:30')

@bot.message_handler(commands=['view_reminders'])
def view_reminders(message):
    with lock:
        reminders = user_reminders.get(message.chat.id, [])
    if reminders:
        reminders_str = '\n'.join(reminders)
        bot.reply_to(message, f'Ваши напоминания:\n{reminders_str}')
    else:
        bot.reply_to(message, 'У вас нет установленных напоминаний.')

# Функция автоматического напоминания
def send_reminders(chat_id):
    while True:
        now = datetime.datetime.now().strftime('%H:%M')
        with lock:
            reminders = user_reminders.get(chat_id, [])
            if now in reminders:
               try:
                   bot.send_message(chat_id, "Напоминание - выпей стакан воды")
                   logging.info(f'Напоминание отправлено в {now} пользователю {chat_id}')
               except Exception as e:
                   logging.error(f'Ошибка при отправке сообщения пользователю {chat_id}: {e}')

        time.sleep(60)

# Обработка ошибок
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.reply_to(message, "Я не понимаю эту команду. Попробуйте /start, /fact, /set_reminder или /view_reminders.")

bot.polling(none_stop=True)