import logging
from crontab import CronTab
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import ChatAction
import requests
import os

from telegram.vendor.ptb_urllib3.urllib3 import util

from light import light_on,light_off,get_light_status,schedule_light_on,schedule_light_off,get_times


BOT_TOKEN=***
MOTION_FOLDER="/home/pi/Desktop/motion"

cron = CronTab(user=True)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def check_Status():
    status = requests.get('http://localhost:8080/0/detection/status')
    if status.text.endswith("ACTIVE \n"):
        return True
    else:
        return False

def get_Keyboard():
    auto=check_Status()
    if not auto:
        keyboard = [[InlineKeyboardButton("Auto on", callback_data='1'),
                     InlineKeyboardButton("Control now", callback_data='2'),
                     InlineKeyboardButton("Last video", callback_data='3'),
                     InlineKeyboardButton("Live stream", callback_data='5', url='192.168.1.6:8081')]]
    else:
        keyboard = [[InlineKeyboardButton("Auto off", callback_data='4'),
                     InlineKeyboardButton("Last video", callback_data='3'),
                     InlineKeyboardButton("Live stream", callback_data='5', url='192.168.1.6:8081')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def start(update, context):
    logger.info("User %s started the conversation.", update.message.from_user.first_name)
    chatId=update.effective_chat.id
    print("Chat id:",update.effective_chat.id)
    update.message.reply_text('Choose an option:',reply_markup=get_Keyboard())



def button(update, context):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    choice=query.data
    if choice=='1':
        status=setAutoModeOn()
        context.bot.send_message(chat_id=update.effective_chat.id, text="STATUS : "+status, reply_markup=get_Keyboard())
    #Control now
    elif choice=='2':
        capture_snapshot()
    elif choice=='3':
        get_last_cat_video(update,context)
    elif choice=='4':
        status=setAutoModeOff()
        context.bot.send_message(chat_id=update.effective_chat.id, text="STATUS : " + status, reply_markup=get_Keyboard())

def capture_snapshot():
    now, sunset, sunrise = get_times()
    if now > sunset:
        status=get_light_status()
        if status==0:
            light_on()
    requests.get('http://localhost:8080/0/action/snapshot')
    if now > sunset and status==0:
        light_off()

def get_last_cat_video(update,context):
    if os.path.exists(MOTION_FOLDER + '/cat.mp4'):
        last_video=open(MOTION_FOLDER + '/cat.mp4','rb')
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)
        context.bot.send_video(chat_id=update.effective_chat.id,video=last_video,caption="Last cat video",reply_markup=get_Keyboard())
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='No cat video found',reply_markup=get_Keyboard())


def help(update, context):
    update.message.reply_text("Use /start to test this bot.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)



def setAutoModeOff():
    #light_off()
    #cron.remove_all()
    #cron.write()
    print("auto mode off")
    requests.get('http://localhost:8080/0/detection/pause')
    status = requests.get('http://localhost:8080/0/detection/status')
    return status.text


def setAutoModeOn():
    #now,sunset,sunrise=get_times()
    #if now>sunset:
    #     light_on()
    # schedule_light_on(cron,sunset)
    # schedule_light_off(cron,sunrise)
    print("auto mode on")
    requests.get('http://localhost:8080/0/detection/start')
    status=requests.get('http://localhost:8080/0/detection/status')
    return status.text





def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(BOT_TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
