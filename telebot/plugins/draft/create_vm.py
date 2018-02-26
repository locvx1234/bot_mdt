import telegram
import config
from keystoneauth1.identity import v3
from keystoneauth1 import session
import novaclient.client as novaclient
from neutronclient.v2_0 import client
import glanceclient.client as glanceclient
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler

TELEGRAM_HTTP_API_TOKEN = '529971138:AAHaRo7KYsjfCwUhe9x3r7ilFftEDUwNyKM'

FIRST, SECOND, THIRD, FOURTH = range(4)
data = {}
def start(bot, update):
    keyboard = [
        [InlineKeyboardButton(u"Network", callback_data=str(FIRST))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        u"Start go to hera, Press network",
        reply_markup=reply_markup
    )
    return FIRST

def first(bot, update):
    query = update.callback_query
    list_networks, list_flavors, list_images = create_vm()
    keyboard_network, id_networks = keyboard_item(list_networks)
    print(query.data)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"Select network"
    )

    reply_markup = InlineKeyboardMarkup(keyboard_network)

    bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )
    #print(query.data)
    return SECOND

def second(bot, update):
    query = update.callback_query
    data["network"] = query.data
    list_networks, list_flavors, list_images = create_vm()
    keyboard_images, id_images = keyboard_item(list_images)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"select image"
    )
    reply_markup = InlineKeyboardMarkup(keyboard_images)
    bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup)
    return THIRD


def third(bot, update):
    query = update.callback_query
    data["image"] = query.data
    list_networks, list_flavors, list_images = create_vm()
    keyboard_flavors, id_images = keyboard_item(list_flavors)
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
    sess = authenticate()
    nova = novaclient.Client("2.1", session=sess)
    nova.servers.create(name = "minhkma",
                        image= data["image"],
                        flavor= data['flavor'],
                        nics= [{'net-id':data['network']}])
    return

def authenticate(auth_url= None, username= None ,password= None ,
                 project_name= None ):
    """ This function to get authentication with Keystone

    :return: Session
    """
    auth_url = auth_url or config.AUTH_URL
    username = username or config.USERNAME
    password = password or config.PASSWORD
    project_name = project_name or config.PROJECT_NAME
    auth = v3.Password(auth_url=auth_url,
                       user_domain_name='default',
                       username=username,password=password,
                       project_domain_name='default',
                       project_name=project_name)
    sess = session.Session(auth=auth)
    return sess

def create_vm():
    sess = authenticate()
    neutron = client.Client(session=sess)
    networks = neutron.list_networks()
    list_networks = []
    for count_network in range(len(networks["networks"])):
        Name = networks["networks"][count_network]["name"]
        ID = networks["networks"][count_network]["id"]
        button_networks = '{0} : {1}'.format(Name, ID)
        list_networks.append(button_networks)
    list_flavors = []
    nova = novaclient.Client("2.1", session=sess)
    flavors = nova.flavors.list()
    for flavor in flavors:
        id_flavor = flavor.id
        name_flavor = flavor.name
        button_flavors = '{0} : {1}'.format(name_flavor,id_flavor)
        list_flavors.append(button_flavors)
    list_images = []
    glance = glanceclient.Client('2', session=sess)
    for image in glance.images.list():
        name = image['name']
        id = image["id"]
        button_images = '{0} : {1}'.format(name,id)
        list_images.append(button_images)
    return list_networks, list_flavors, list_images

def keyboard_item(list_items):
    keyboard_items = []
    id_items = []
    for item in list_items:
        data_items = item.split(' : ')
        name_item = data_items[0]
        id_item = data_items[1]
        keyboard_items.append([InlineKeyboardButton(name_item,
                                                 callback_data=id_item)])
        id_items.append(id_item)
    #keyboard_items.append([InlineKeyboardButton('back', callback_data='back')])
    return keyboard_items, id_items


updater = Updater(TELEGRAM_HTTP_API_TOKEN)

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        FIRST: [CallbackQueryHandler(first)],
        SECOND: [CallbackQueryHandler(second)],
        THIRD: [CallbackQueryHandler(third)],
        FOURTH: [CallbackQueryHandler(fourth)]
    },
    fallbacks=[CommandHandler('start', start)]
)

updater.dispatcher.add_handler(conv_handler)

updater.start_polling()

updater.idle()
