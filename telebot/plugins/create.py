from telebot.plugins import novautils
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler,\
    ConversationHandler

FIRST, SECOND, THIRD, FOURTH = range(4)
data = {}
nov = novautils.Nova('192.168.100.114', 'admin', 'locdev', 'admin')


def handle(bot, update, args):
    keyboard = [
        [InlineKeyboardButton(u"Network", callback_data=str(FIRST))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    print(reply_markup)
    print(type(reply_markup))
    update.message.reply_text(
        u"Start go to hera, Press network",
        reply_markup=reply_markup
    )
    data['name'] = args.pop(0)
    return FIRST


def first(bot, update):
    query = update.callback_query
    dict_networks = nov.networks()
    print(dict_networks)
    keyboard_networks = nov.keybroad_items(dict_networks)
    print(query.data)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"Select network"
    )

    reply_markup = InlineKeyboardMarkup(keyboard_networks)

    bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )
    # print(query.data)
    return SECOND


def second(bot, update):
    query = update.callback_query
    data["network"] = query.data
    dict_images = nov.list_images()
    keyboard_images = nov.keybroad_items(dict_images)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"select image"
    )
    reply_markup = InlineKeyboardMarkup(keyboard_images)
    print('abc : {0}'.format(reply_markup))
    bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup)
    return THIRD


def third(bot, update):
    query = update.callback_query
    data["image"] = query.data
    dict_flavors = nov.list_flavors()
    keyboard_flavors = nov.keybroad_items(dict_flavors)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"select flavor"
    )
    reply_markup = InlineKeyboardMarkup(keyboard_flavors)
    bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup)
    return FOURTH


def fourth(bot, update):
    query = update.callback_query
    data['flavor'] = query.data
    print(data)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=str(data))
    nov.create_vm(name= data['name'],
                  image= data['image'],
                  flavor= data['flavor'],
                  nic= data['network'])
    return

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create', handle, pass_args=True)],
    states={
        FIRST: [CallbackQueryHandler(first)],
        SECOND: [CallbackQueryHandler(second)],
        THIRD: [CallbackQueryHandler(third)],
        FOURTH: [CallbackQueryHandler(fourth)]
    },
    fallbacks=[CommandHandler('create', handle, pass_args=True)],
)

