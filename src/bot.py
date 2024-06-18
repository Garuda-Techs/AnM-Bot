import os
import player # executes unabstracted code in player.py
import messages
import logging
from collections import defaultdict
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

print('BOT.PY BEGINS EXECUTION')
# Enable logging.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialise players.
# Default value for the dictionary is a new Player object.
players = defaultdict(player.Player)

async def start_command(update: Update, context: CallbackContext) -> None:
    # Sends a message when the command /start is issued.
    playerName = update.message.chat.username.lower()
    if players[playerName].username is None:
        # Player not found/ registered.
        update.message.reply_text(messages.NOT_REGISTERED)
        return
    # Registers chat id for message sending.
    players[playerName].setChatId(update.message.chat.id)
    logger.info(f'{playerName} started the bot with chat_id {players[playerName].chat_id}.')
    await update.message.reply_text(
        f'Hey {"Angel" if players[playerName].isAngel else "Mortal"} {playerName}!\n\n{messages.WELCOME_TEXT}{messages.HELP_TEXT}')
    await chat_command(update, context)

async def help_command(update: Update, context: CallbackContext) -> None:
    # Sends a message when the command /help is issued.
    await update.message.reply_text(messages.HELP_TEXT)

async def chat_command(update: Update, context: CallbackContext) -> None:
    # Checks if player can start chatting.
    playerName = update.message.chat.username.lower()
    if players[playerName].username is None:
        # Player not found/ registered.
        update.message.reply_text(messages.NOT_REGISTERED)
        return ConversationHandler.END
    if players[playerName].chat_id is None:
        # Player chat id not found.
        await update.message.reply_text(messages.ERROR_CHAT_ID)
        return ConversationHandler.END
    if players[playerName].partner.chat_id is None:
        # Player partner not available.
        await update.message.reply_text(
            messages.PARTNER_UNAVAILABLE_MORTAL
            if players[playerName].isAngel
            else messages.PARTNER_UNAVAILABLE_ANGEL
        )
    else:
        await update.message.reply_text(
            messages.PARTNER_AVAILABLE_MORTAL
            if players[playerName].isAngel
            else messages.PARTNER_AVAILABLE_ANGEL
        )
        await context.bot.send_message(
            text=messages.INFORM_PARTNER_ANGEL
            if players[playerName].isAngel
            else messages.INFORM_PARTNER_MORTAL,
            chat_id=players[playerName].partner.chat_id
        )

async def sendNonTextMessage(message, bot, chat_id, messageText) -> None:
    if message.photo:
        await bot.send_photo(
            photo=message.photo[-1],
            caption=messageText,
            chat_id=chat_id
        )
    elif message.sticker:
        await bot.send_sticker(
            sticker=message.sticker,
            chat_id=chat_id
        )
    elif message.document:
        await bot.send_document(
            document=message.document,
            caption=messageText,
            chat_id=chat_id
        )
    elif message.video:
        await bot.send_video(
            video=message.video,
            caption=messageText,
            chat_id=chat_id
        )
    elif message.video_note:
        await bot.send_video_note(
            video_note=message.video_note,
            caption=messageText,
            chat_id=chat_id
        )
    elif message.voice:
        await bot.send_voice(
            voice=message.voice,
            caption=messageText,
            chat_id=chat_id
        )
    elif message.audio:
        await bot.send_audio(
            audio=message.audio,
            caption=messageText,
            chat_id=chat_id
        )
    elif message.animation:
        await bot.send_animation(
            animation=message.animation,
            caption=messageText,
            chat_id=chat_id
        )

async def send_msg_command(update: Update, context: CallbackContext) -> None:
    playerName = update.message.chat.username.lower()
    logger.info("send msg command")
    if players[playerName].chat_id is None or players[playerName].partner.chat_id is None:
        logger.info("Failed here")
        return
    logger.info("sending message here")
    message = update.message
    messageText = angelOrMortal(playerName, update.message)
    if message.text:
        await context.bot.send_message(
            text=messageText,
            chat_id=players[playerName].partner.chat_id
        )
    else:
        await sendNonTextMessage(message, context.bot, players[playerName].partner.chat_id, messageText)

async def admin_command(update: Update, context: CallbackContext) -> None:
    # Displays admin guide when the command /admin is issued.
    update.message.reply_text(messages.ADMIN_GUIDE, parse_mode=constants.PARSEMODE_MARKDOWN_V2)
    with open('./csv/sample.csv', 'rb') as csv_file:
        await context.bot.send_document(update.message.chat.id, csv_file)

async def upload_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Saved file.')
    with open('./csv/pairings.csv', 'wb+') as csv_file:
        context.bot.get_file(update.message.document).download(out=csv_file)
    await reload_command(update, CallbackContext)

async def reload_command(update: Update, context: CallbackContext) -> None:
    # Reloads database after receiving new csv file.
    update.message.reply_text(player.loadPlayers(players))
    update.message.reply_text('Players reloaded successfully.')
    logger.info('Players reloaded with new csv file.')

async def reset_command(update: Update, context: CallbackContext) -> None:
    # Resets database when the command reset is issued.
    players.clear()
    update.message.reply_text('Players have been reset.')
    logger.info('Players have been reset.')

def angelOrMortal(playerName, message) -> str:
    if players[playerName].isAngel:
        if message.text:
            message = '\U0001F607' + str(message.text or '')
        else:
            message = '\U0001F607' + str(message.caption or '')
        return message
    else:
        if message.text:
            message = '\U0001F476' + str(message.text or '')
        else:
            message = '\U0001F476' + str(message.caption or '')
        return message   

def main():
    BOT_TOKEN = os.environ['BOT_TOKEN']
    # WEBHOOK_URL = os.environ['WEBHOOK_URL']

    logger.info(player.loadPlayers(players))
    # updater = Updater(BOT_TOKEN,use_context=True)
    app = Application.builder().token(BOT_TOKEN).build()

    # User commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(~filters.COMMAND & ~filters.Document.FileExtension("csv"), send_msg_command))

    # Admin commands.
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("reload", reload_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), upload_command))
    
    # app.run_webhook(listen="0.0.0.0",
    #                 port=int(os.environ.get('PORT', 5000)),
    #                 url_path=BOT_TOKEN,
    #                 webhook_url=WEBHOOK_URL)
    app.run_polling(poll_interval=1)

    # updater.start_webhook(listen="0.0.0.0",
    #                       port=int(os.environ.get('PORT', 5000)),
    #                       url_path=BOT_TOKEN,
    #                       webhook_url=WEBHOOK_URL)
    # #updater.start_polling()
    # updater.idle()

if __name__ == '__main__':
    try:
        logger.info("Bot has started.")
        main()
    finally:
        logger.info("Bot has terminated.")
