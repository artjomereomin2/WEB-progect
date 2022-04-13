import datetime
import json
import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from ws import WayFinder

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5263728547:AAHgyA2cnCALO-XV8YMFipAFG_hzQOVGaZ4'

wf = WayFinder()


# Определяем функцию-обработчик сообщений.
# У неё два параметра, сам бот и класс updater, принявший сообщение.
def SetLocation(update, context):
    update.message.reply_text('Отправьте свою геопозицию')
    return 1


def Location(update, context):
    wf.start = (update.message.location.longitude, update.message.location.latitude)
    update.message.reply_text('Спасибо! Можете спрашивать у меня куда вам надо')
    return -1


def FindOne(update, context):
    update.message.reply_text(wf.do_work(update.message.text.split()[1], 1, '/FindOne'))


def FindAny(update, context):
    update.message.reply_text(wf.do_work(update.message.text.split()[2], update.message.text.split()[1], '/FindAny'))


def FindList(update, context):
    update.message.reply_text(wf.do_work(update.message.text.split()[2], '*', '/FindList'))


def From(update, context):
    update.message.reply_text(wf.do_work(update.message.text.split()[1], update.message.text.split()[2], '/From'))


def Text(update, context):
    update.message.reply_text(wf.do_work(' '.join(update.message.text.split()[1:]), '*', '/Text'))


def main():
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
    dp.add_handler(CommandHandler('From', From))
    dp.add_handler(CommandHandler('Text', Text))

    updater.start_polling()

    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
