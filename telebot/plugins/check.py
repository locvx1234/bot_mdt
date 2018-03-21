from telebot.plugins import novautils
from  telebot.plugins import networkutils
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def convert_keyboard_inline(list_items):
    # list_items = []
    # keyboard_items = []
    # for dict_item in dict_items:
    #     row = []
    #     row.extend([dict_item, dict_items[dict_item]])
    #     list_items.append(row)
    keyboard_items = []
    for list_item in list_items:
        keyboard_row = []
        for count,_item in enumerate(list_item):
            keyboard_row.append(InlineKeyboardButton(list_item[count],
                                                 callback_data='minh'))
        keyboard_items.append(keyboard_row)
    reply_markup = InlineKeyboardMarkup(keyboard_items)
    return reply_markup


def handle(bot, update, args):
    nov = novautils.Nova('192.168.100.60', 'admin', 'minhkma', 'admin')
    neu = networkutils.Neutron('192.168.100.60', 'admin', 'minhkma', 'admin')
    action = args.pop(0)
    if action == 'nova':
        # print('abc')
        # a = nov.service()
        # print(a)
        list_services = nov.service()
        # print(list_services)
        msg = convert_keyboard_inline(list_services)
        update.message.reply_text(u"Agent Nova",
                                  reply_markup=msg)
    if action == "neutron":
        dict_services = neu.list_agent()
        # print(dict_services)
        list_services = []
        for dict_service in dict_services:
            list_service = []
            print(dict_service)
            list_service.extend([dict_service['agent_type'],
                                dict_service['host'],
                                str(dict_service['alive'])])
            list_services.append(list_service)
        print(list_services)
        msg = convert_keyboard_inline(list_services)
        # print(msg)
        update.message.reply_text(u"Agent Neutron",
                                   reply_markup=msg)
