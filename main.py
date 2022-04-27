from datetime import timedelta
import json
import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler, JobQueue
from telegram import ReplyKeyboardMarkup
from ws import WayFinder
from keys import TOKEN
import asyncio
import os
from data import db_session
from data.requests import Requests

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


# Определяем функцию-обработчик сообщений.
# У неё два параметра, сам бот и класс updater, принявший сообщение.
def Help(update, context):
    k = list(map(lambda x: x.request,
                               list(db_sess.query(Requests).filter(Requests.user_id == update.message.from_user.id))))
    if len(k) > 2:
        k = k[-2:]
    reply_keyboard = [['/SetLocation', '/help'],
                      k]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        'Я волшебный колобок и я проведу вас по этому страшному лабиринту.'
        '\nВот, что я могу:\n/SetLocation ...(геолокация) - Задаёт начальное местоположение'
        '\n/FindOne ... - Ищет ближайший объект, указанный после команды, оценивает время до него'
        '\n/FindAny ...(количество) ...(объект) - Ищет ближайшие объекты, количество и тип которых указано после '
        'команды, оценивает время до них'
        '\n/FindList ...(объекты) - Ищет ближайшие объекты, которые указаны после команды'
        '\n/From ...(место откуда) to ...(место куда) - Оценивает время пути между 2 точками'
        '\n/Text ...(предложение) - Расапознаёт запрос пользователя и сообщает куда и как долго ему нужно идти'
        '\n/FindOrder <место1>, <место2>... - ищет места для посещения в порядке, например если человек хочет '
        'сходить в кино, а затем поужинать, он напишет /FindOrder кино, кафе', reply_markup=markup)


def SetLocation(update, context):
    update.message.reply_text('Отправьте свою геопозицию')
    return 1


def Location(update, context):
    context.user_data['coords'] = update.message.location['longitude'], update.message.location['latitude']
    print(context.user_data['coords'])
    context.user_data['way'].set_location(update.message.from_user.id, context.user_data['coords'], db_sess)
    update.message.reply_text('Спасибо! Можете спрашивать у меня куда вам надо')
    return -1


def FindOne(update, context):  # +
    try:
        funcs.append(context.user_data['way'].do_work)
        args.append([update.message.text.split()[1:], '/FindOne', update.message.from_user.id, db_sess,
                     context.user_data['coords'], update])
        """tasks.append(asyncio.create_task(
            context.user_data['way'].do_work(update.message.text.split()[1:], '/FindOne', update.message.from_user.id,
                                             context.user_data['coords'],update=update)))"""
    except KeyError:
        db_sess.rollback()
        update.message.reply_text('Сначала отправьте координаты')


def FindAny(update, context):  # +
    try:
        funcs.append(context.user_data['way'].do_work)
        args.append([update.message.text.split()[1:], '/FindAny', update.message.from_user.id, db_sess,
                     context.user_data['coords'], update])
        """tasks.append(asyncio.create_task(
            context.user_data['way'].do_work(update.message.text.split()[1:], '/FindAny', update.message.from_user.id,
                                             context.user_data['coords'],update=update)))"""
    except KeyError:
        db_sess.rollback()
        update.message.reply_text('Сначала отправьте координаты')


def FindList(update, context):  # +
    try:
        funcs.append(context.user_data['way'].do_work)
        args.append([' '.join(update.message.text.split()[1:]).split(','), '/FindList',
                     update.message.from_user.id, db_sess, context.user_data['coords'], update])
        """tasks.append(asyncio.create_task(
            context.user_data['way'].do_work(' '.join(update.message.text.split()[1:]).split(','), '/FindList',
                                             update.message.from_user.id, context.user_data['coords'],update=update)))"""
    except KeyError:
        db_sess.rollback()
        update.message.reply_text('Сначала отправьте координаты')


def FindOrder(update, context):  # +
    try:
        funcs.append(context.user_data['way'].do_work)
        args.append([' '.join(update.message.text.split()[1:]).split(','), '/FindOrder',
                     update.message.from_user.id, db_sess, context.user_data['coords'], update])
        """tasks.append(asyncio.create_task(
            context.user_data['way'].do_work(' '.join(update.message.text.split()[1:]).split(','), '/FindOrder',
                                             update.message.from_user.id, context.user_data['coords'],update=update)))"""
    except KeyError:
        db_sess.rollback()
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
        funcs.append(context.user_data['way'].do_work)
        args.append([(' '.join(begin), ' '.join(end)), '/From', update.message.from_user.id, db_sess,
                     context.user_data['coords'], update])
        """tasks.append(asyncio.create_task(
            context.user_data['way'].do_work((' '.join(begin), ' '.join(end)), '/From', update.message.from_user.id,
                                             context.user_data['coords'],update=update)))"""
    except KeyError:
        db_sess.rollback()
        update.message.reply_text('Сначала отправьте координаты')


def Text(update, context):  # ++-
    try:
        funcs.append(context.user_data['way'].do_work)
        args.append([' '.join(update.message.text.split()[1:]), '/Text',
                     update.message.from_user.id, context.user_data['coords'], update])
    except KeyError:
        db_sess.rollback()
        update.message.reply_text('Сначала отправьте координаты')
    """tasks.append(asyncio.create_task(
        context.user_data['way'].do_work(' '.join(update.message.text.split()[1:]), '/Text',
                                         update.message.from_user.id, context.user_data['coords'],update=update)))"""


def something(update, context):
    funcs.append(context.user_data['way'].do_work)
    args.append([' '.join(update.message.text.split()), '/Text',
                 update.message.from_user.id, context.user_data['coords'], update])
    '''tasks.append(asyncio.create_task(
        context.user_data['way'].do_work(' '.join(update.message.text.split()), '/Text',
                                         update.message.from_user.id, context.user_data['coords'],update=update)))'''


funcs = []
args = []


async def do_tasks1():
    global tasks, funcs, args
    for i in range(len(funcs)):
        tasks.append(asyncio.create_task(funcs[i](*args[i])))
    if tasks:
        await asyncio.gather(*tasks)
    tasks = []
    funcs = []
    args = []


def do_tasks(context):
    asyncio.run(do_tasks1())


def start(update, context):
    context.user_data['way'] = WayFinder()
    context.user_data['way'].add_user(update.message.from_user.id, update.message.from_user.last_name,
                                      update.message.from_user.first_name, update.message.from_user.language_code,
                                      update.message.from_user.is_bot, db_sess)
    Help(update, context)


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
    dp.add_handler(CommandHandler('FindOne', FindOne))
    dp.add_handler(CommandHandler('FindAny', FindAny))
    dp.add_handler(CommandHandler('FindList', FindList))
    dp.add_handler(CommandHandler('FindOrder', FindOrder))
    dp.add_handler(CommandHandler('From', From))
    dp.add_handler(CommandHandler('Text', Text))
    dp.add_handler(CommandHandler('help', Help))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, something))

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
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    db_session.global_init("db/peoples.sqlite")
    db_sess = db_session.create_session()
    main()
