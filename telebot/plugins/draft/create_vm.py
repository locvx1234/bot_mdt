import telegram
import config
from keystoneauth1.identity import v3
from keystoneauth1 import session
import novaclient.client as novaclient
from neutronclient.v2_0 import client
import glanceclient.client as glanceclient
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

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
    keyboard_items.append([InlineKeyboardButton('back', callback_data='back')])
    return keyboard_items, id_items

def dm(bot, update):

    keyboard = [[InlineKeyboardButton("networks", callback_data='network'),
                 InlineKeyboardButton("images",
                                      callback_data='image')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

def button(bot, update):
    keyboard = [[InlineKeyboardButton("networks", callback_data='network'),
                 InlineKeyboardButton("images",
                                      callback_data='image')]]

    reply_markup = InlineKeyboardMarkup(keyboard)


    list_networks, list_images = create_vm()
    keyboard_network, id_networks = keyboard_item(list_networks)
    keyboard_image, id_images = keyboard_item(list_images)
    reply_markup_network = InlineKeyboardMarkup(keyboard_network)
    reply_markup_image = InlineKeyboardMarkup(keyboard_image)
    # bot.edit_message_text(text="Selected option - dkm: {}".format(query.data),
    #                        chat_id=query.message.chat_id,
    #                        message_id=query.message.message_id)
    if update.callback_query.data == 'network':
        # list_networks, list_images = create_vm()
        # keyboard_network, id_items = keyboard_item(list_networks)
        # reply_markup_network = InlineKeyboardMarkup(keyboard_network)
        bot.edit_message_text(text="Selected option: {}".format(update.callback_query.data),
                          chat_id=update.callback_query.message.chat_id,
                          message_id=update.callback_query.message.message_id,
                              reply_markup=reply_markup_network)
        # print(list_networks)
        # print(id_networks)


    if update.callback_query.data == 'image':
        # list_networks, list_images = create_vm()
        # keyboard_image = keyboard_item(list_images)
        # reply_markup_image = InlineKeyboardMarkup(keyboard_image)
        bot.edit_message_text(text="Selected option: {}".format(update.callback_query.data),
                              chat_id=update.callback_query.message.chat_id,
                              message_id=update.callback_query.message.message_id,
                              reply_markup=reply_markup_image)

    if update.callback_query.data == 'back':
        bot.edit_message_text(text="Selected option: ",
                              chat_id=update.callback_query.message.chat_id,
                              message_id=update.callback_query.message.message_id,
                              reply_markup=reply_markup)

    if update.callback_query.data in id_networks:
        network = update.callback_query.data
        print("id network is : {}".format(network))

    if update.callback_query.data in id_images:
        image = update.callback_query.data
        print("id image is : {}".format(image))




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
    list_network = []
    for count_network in range(len(networks["networks"])):
        Name = networks["networks"][count_network]["name"]
        ID = networks["networks"][count_network]["id"]
        button_network = '{0} : {1}'.format(Name, ID)
        list_network.append(button_network)
    list_images = []
    glance = glanceclient.Client('2', session=sess)
    for image in glance.images.list():
        name = image['name']
        id = image["id"]
        button_images = '{0} : {1}'.format(name,id)
        list_images.append(button_images)
    return list_network, list_images

def help(bot, update):
    update.message.reply_text("Use /dm to test this bot.")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater("529971138:AAHaRo7KYsjfCwUhe9x3r7ilFftEDUwNyKM")

    updater.dispatcher.add_handler(CommandHandler('dm', dm))
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


