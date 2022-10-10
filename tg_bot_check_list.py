from config import TOKEN
from datetime import datetime as dt

import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler,)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

priority, location, description, comment, date = 0, 0, 0, 0, 0

PRIORITY, LOCATION, DESCRIPTION, COMMENT, DATE = range(5)


def start(update, _):
    user = update.message.from_user
    reply_keyboard = [['Низкий', 'Средний', 'Высокий']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        f'Привет, {user.first_name}!\n'
        'Это бот-запоминатель задач и дел.\n\n'
        'Выбери приоритет поставленной задачи/дела.\n\n'
        'Команда /cancel, чтобы прекратить.',
        reply_markup=markup_key,)
    return PRIORITY

def select_priority(update, _):
    global priority
    user = update.message.from_user
    priority = update.message.text
    logger.info("%s выбрал %s приоритет задачи/дела.", user.first_name, update.message.text)
    reply_keyboard = [['Дом', 'Работа', 'Другое']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text('Выбери, где нужно сделать задачу/дело.', reply_markup=markup_key,)
    return LOCATION

def select_location(update, _):
    global location
    user = update.message.from_user
    location = update.message.text
    logger.info("%s выбрал место задачи/дела: %s.", user.first_name, update.message.text)
    update.message.reply_text('Теперь введи описание задачи', reply_markup=ReplyKeyboardRemove())
    return DESCRIPTION

def write_description(update, _):
    global description
    user = update.message.from_user
    description = update.message.text
    logger.info("%s описал задачу/дело: %s.", user.first_name, update.message.text)
    update.message.reply_text('Теперь введи комментарий.')
    return COMMENT

def write_comment(update, _):
    global comment
    user = update.message.from_user
    comment = update.message.text
    logger.info("%s написал комментарий: %s.", user.first_name, update.message.text)
    update.message.reply_text('Теперь введи дату выполнения.')
    return DATE

def write_date(update, _):
    global location
    global priority
    global date
    global description
    global comment
    user = update.message.from_user
    date = update.message.text
    logger.info("%s поставил выполнить задачу/дело к: %s", user.first_name, update.message.text)
    log = f'{priority} \t=\t {location} \t=\t {date} \t=\t {description} \t=\t {comment}'
    logg(log)
    update.message.reply_text(f'{user.first_name}!\n'
        'Задача/дело успешно сохранено.\n\n'
        'Ты его найдешь в файле log.csv.\n\n'
        'Команда /start, чтобы записать новую задачу.',)
    return ConversationHandler.END

def logg(result):
    '''
    Записывает время операции, саму операцию и её результат
    '''
    time = dt.now().strftime('%d.%m.%Y - %H:%M')
    with open('log.csv', 'a', encoding = 'UTF-8') as file:
        file.write(f'{time}: \t{result}\n')

def cancel(update, _):
    user = update.message.from_user
    logger.info("Пользователь %s отменил всё.", user.first_name)
    update.message.reply_text('Не хочешь - как хочешь =(', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


if __name__ == '__main__':
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PRIORITY: [MessageHandler(Filters.regex('^(Низкий|Средний|Высокий)$'), select_priority)],
            LOCATION: [MessageHandler(Filters.regex('^(Дом|Работа|Другое)$'), select_location)],
            DESCRIPTION: [MessageHandler(Filters.text, write_description)],
            COMMENT: [MessageHandler(Filters.text, write_comment)],
            DATE: [MessageHandler(Filters.text, write_date)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)

    print('server started')
    updater.start_polling()
    updater.idle()

