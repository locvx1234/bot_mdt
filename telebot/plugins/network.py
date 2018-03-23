"""Network plugin
/network in openstack!
"""
import pprint
from telebot.plugins import networkutils
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, RegexHandler, MessageHandler, Filters
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_NETWORK_NAME, CHOOSE_NETWORK_ADMIN, CHOOSE_NETWORK_SHARED, CREATE_NETWORK = range(5)


def handle(bot, update):
    keyboard = [[InlineKeyboardButton('List network', callback_data="list_network"),
                 InlineKeyboardButton('Create network', callback_data="create_network")],
                [InlineKeyboardButton('Close', callback_data="close")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Hi! Welcome to network function",
        reply_markup=reply_markup)

    return CHOOSING


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def choose(bot, update):
    query = update.callback_query
    query_data = query.data
    if query_data == 'list_network' or query_data == 'back_list_network':
        list_network(bot, query)
        return CHOOSING
    elif query_data.startswith('list_network_'):
        list_network_menu(bot, query)
        return CHOOSING
    elif query_data == 'back_menu_network':
        menu_network(bot, query)
        return CHOOSING
    elif query_data.startswith('detail_network_'):
        detail_network(bot, query)
        return ConversationHandler.END
    elif query_data.startswith('delete_network_'):
        delete_network(bot, query)
        return ConversationHandler.END
    elif query_data == 'create_network':
        bot.edit_message_text(text="Alright, a new network. Please choose a name for your network.",
                              chat_id=query.message.chat_id, message_id=query.message.message_id)
        return CHOOSE_NETWORK_ADMIN
    elif query_data == 'close':
        close(bot, query)
        return ConversationHandler.END
    else:
        pass


def list_network(bot, query):
    list_net = []
    net = networkutils.Neutron()
    for item in net.list_network():
        print('list_network' + '_' + item["id"])

        if item["name"] == '':
            name = item['id']
        else:
            name = item["name"]

        list_net.append([InlineKeyboardButton(name, callback_data='list_network' + '_' + item["id"])])
    list_net.append([InlineKeyboardButton("<< Back to network menu", callback_data='back_menu_network')])
    print(list_net)
    reply_markup = InlineKeyboardMarkup(list_net)
    bot.edit_message_text(text='List networks id:',
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          reply_markup=reply_markup)


def list_network_menu(bot, query):
    query_data = query.data
    network_id = query_data[13:]

    options = [[InlineKeyboardButton("Detail", callback_data='detail_network' + '_' + network_id),
                InlineKeyboardButton("Delete", callback_data='delete_network' + '_' + network_id)],
               [InlineKeyboardButton("Subnet", callback_data='subnet_network' + '_' + network_id),
                InlineKeyboardButton("<< Back", callback_data='back_list_network')]]

    reply_markup = InlineKeyboardMarkup(options)
    bot.edit_message_text(text='Options:',
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          reply_markup=reply_markup)


def menu_network(bot, query):
    keyboard = [[InlineKeyboardButton("List network", callback_data="list_network"),
                 InlineKeyboardButton("Create network", callback_data="create_network")],
                [InlineKeyboardButton("Close", callback_data="close")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(text='Network menu:',
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          reply_markup=reply_markup)


def detail_network(bot, query):
    net = networkutils.Neutron()
    query_data = query.data
    network_id = query_data[15:]
    network_detail = net.show_network(network_id)
    output = "*Detail network*" + \
             "```" + "\n" + "ID: " + network_detail["id"] + "\n" + \
             "Name: " + network_detail["name"] + "\n" +  \
             "Description: " + network_detail["description"] + "\n" + \
             "Admin state up: " + str(network_detail["admin_state_up"]) + "\n" + \
             "Status: " + network_detail["status"] + "\n" + \
             "```"
    bot.edit_message_text(text=output,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id, parse_mode='Markdown')


def delete_network(bot, query):
    net = networkutils.Neutron()
    query_data = query.data
    network_id = query_data[15:]
    net.delete_network(network_id)
    bot.edit_message_text(text="Delete complete",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


# def typing_network_name(bot, que)


def network_admin_choice(bot, update, user_data):
    network_name = update.message.text
    user_data['name'] = network_name
    keyboard = [[InlineKeyboardButton('Yes', callback_data="True"),
                 InlineKeyboardButton('NO', callback_data="False")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Network {}? Yes, Would you like to assign admin state up? '.format(network_name),
        reply_markup=reply_markup)
    return CHOOSE_NETWORK_SHARED


def network_shared_choice(bot, update, user_data):
    print(update)
    user_data['admin_state_up'] = update.callback_query.data
    print(user_data)
    keyboard = [[InlineKeyboardButton('Yes', callback_data="True"),
                 InlineKeyboardButton('NO', callback_data="False")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # bot.edit_message_text(text='Network {}, Admin state up : {}. Shared ?'.format(user_data['network_name'], user_data['admin_state_up']),
    #                       chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=reply_markup)

    update.callback_query.message.reply_text(
        'Network {}, Admin state up : {}. Shared ?'.format(user_data['name'], user_data['admin_state_up']),
        reply_markup=reply_markup)
    return CREATE_NETWORK


def create_network(bot, update, user_data):
    net = networkutils.Neutron()
    user_data['shared'] = update.callback_query.data
    print(user_data)

    # network_options = {'name': network_name, 'admin_state_up': True, 'shared': False}
    net.create_network(user_data)
    update.callback_query.message.reply_text("Create network complete")
    return ConversationHandler.END


def close(bot, query):
    bot.edit_message_text(text='Bye bye baby',
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('network', handle)],

    states={
        CHOOSING: [CallbackQueryHandler(choose),
                   ],
        TYPING_NETWORK_NAME: [MessageHandler(Filters.text, create_network)],
        CHOOSE_NETWORK_ADMIN: [MessageHandler(Filters.text, network_admin_choice, pass_user_data=True)],
        CHOOSE_NETWORK_SHARED: [CallbackQueryHandler(network_shared_choice, pass_user_data=True)],
        CREATE_NETWORK: [CallbackQueryHandler(create_network, pass_user_data=True)],
    },

    fallbacks=[CommandHandler('close', close)]
)