from datetime import timedelta
import json
import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler, JobQueue
from ws import WayFinder
from keys import TOKEN
import schedule
import asyncio
from pprint import pprint

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


# Определяем функцию-обработчик сообщений.
# У неё два параметра, сам бот и класс updater, принявший сообщение.
def Help(update, context):
    update.message.reply_text(
        'Я волшебный колобок и я проведу вас по этому страшному лабиринту.'
        '\nВот, что я могу:\n/SetLocation ...(геолокация) - Задаёт начальное местоположение'
        '\n/FindOne ... - Ищет ближайший объект, указанный после команды, оценивает время до него'
        '\n/FindAny ...(количество) ...(объект) - Ищет ближайшие объекты, количество и тип которых указано после команды, оценивает время до них'
        '\n/FindList ...(объекты) - Ищет ближайшие объекты, которые указаны после команды'
        '\n/From ...(место откуда) to ...(место куда) - Оценивает время пути между 2 точками'
        '\n/Text ...(предложение) - Расапознаёт запрос пользователя и сообщает куда и как долго ему нужно идти'
        '\n/FindOrder <место1>, <место2>... - ищет места для посещения в порядке, например если человек хочет сходить в кино, а затем поужинать, он напишет /FindOrder кино, кафе')


def SetLocation(update, context):
    update.message.reply_text('Отправьте свою геопозицию')
    return 1


def Location(update, context):
    context.user_data['coords'] = update.message.location['longitude'], update.message.location['latitude']
    context.user_data['way'] = WayFinder()
    context.user_data['way'].set_location(update.message.from_user.id, update.message.from_user.last_name,
                                          update.message.from_user.first_name, update.message.from_user.language_code,
                                          update.message.from_user.is_bot, context.user_data['coords'])
    update.message.reply_text('Спасибо! Можете спрашивать у меня куда вам надо')
    return -1


def FindOne(update, context):  # +
    try:
        tasks.append(asyncio.create_task(
            context.user_data['way'].do_work(update.message.text.split()[1:], '/FindOne', update.message.from_user.id,
                                             context.user_data['coords'],update=update)))
    except KeyError:
        update.message.reply_text('Сначала отправьте координаты')


def FindAny(update, context):  # +
    try:
        tasks.append(asyncio.create_task(
            context.user_data['way'].do_work(update.message.text.split()[1:], '/FindAny', update.message.from_user.id,
                                             context.user_data['coords'],update=update)))
    except KeyError:
        update.message.reply_text('Сначала отправьте координаты')


def FindList(update, context):  # +
    try:
        tasks.append(asyncio.create_task(
            context.user_data['way'].do_work(' '.join(update.message.text.split()[1:]).split(','), '/FindList',
                                             update.message.from_user.id, context.user_data['coords'],update=update)))
    except KeyError:
        update.message.reply_text('Сначала отправьте координаты')


def FindOrder(update, context):  # +
    try:
        tasks.append(asyncio.create_task(
            context.user_data['way'].do_work(' '.join(update.message.text.split()[1:]).split(','), '/FindOrder',
                                             update.message.from_user.id, context.user_data['coords'],update=update)))
    except KeyError:
        update.message.reply_text('Сначала отправьте координаты')


def From(update, context):
    try:
        text = update.message.text
        begin = []
        end = []
        has_to = False
        for word in text.split()[1:]:
            if word == 'to':
                has_to = True
            elif has_to:
                end.append(word)
            else:
                begin.append(word)
        # print(context.user_data['coords'])
        tasks.append(asyncio.create_task(
            context.user_data['way'].do_work((' '.join(begin), ' '.join(end)), '/From', update.message.from_user.id,
                                             context.user_data['coords'],update=update)))
    except KeyError:
        update.message.reply_text('Сначала отправьте координаты')


def Text(update, context):  # ++-
    tasks.append(asyncio.create_task(
        context.user_data['way'].do_work(' '.join(update.message.text.split()[1:]), '/Text',
                                         update.message.from_user.id, context.user_data['coords'],update=update)))


def something(update, context):
    try:
        tasks.append(asyncio.create_task(
            context.user_data['way'].do_work(' '.join(update.message.text.split()), '/Text',
                                             update.message.from_user.id, context.user_data['coords'],update=update)))
    except Exception as e:
        print(e) #???


def do_tasks(context):
    global tasks
    if tasks:
        asyncio.gather(*tasks)
    tasks = []


def main():
    global tasks
    tasks = []

    updater = Updater(TOKEN)

    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('SetLocation', SetLocation)],
        states={
            1: [MessageHandler(Filters.location, Location)]
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('Start', Help))
    dp.add_handler(CommandHandler('FindOne', FindOne))
    dp.add_handler(CommandHandler('FindAny', FindAny))
    dp.add_handler(CommandHandler('FindList', FindList))
    dp.add_handler(CommandHandler('FindOrder', FindOrder))
    dp.add_handler(CommandHandler('From', From))
    dp.add_handler(CommandHandler('Text', Text))
    dp.add_handler(CommandHandler('Help', Help))
    dp.add_handler(MessageHandler(Filters.text, something))

    updater.start_polling()

    jobq = JobQueue()

    jobq.set_dispatcher(dp)

    jobq.run_repeating(callback=do_tasks, interval=timedelta(seconds=5))

    jobq.start()
    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
