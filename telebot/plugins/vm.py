from telebot.plugins import novautils
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def convert_keyboard_inline(dict_items):
    list_items = []
    keyboard_items = []
    for dict_item in dict_items:
        row = []
        row.extend([dict_item, dict_items[dict_item]])
        list_items.append(row)
    print('++++++++++++++')
    print(list_items)
    print('++++++++++++++')
    for list_item in list_items:
        keyboard_row = []
        keyboard_row.append(InlineKeyboardButton(list_item[0], callback_data='minh'))
        keyboard_row.append(InlineKeyboardButton(list_item[1], callback_data='minh'))
        keyboard_items.append(keyboard_row)
    reply_markup = InlineKeyboardMarkup(keyboard_items)
    print('++++++++++++++')
    print(reply_markup)
    print('++++++++++++++')
    return reply_markup


def handle(bot, update, args):
    nov = novautils.Nova('192.168.100.114', 'admin', 'locdev', 'admin')
    action = args.pop(0)
    if action == 'list':
        dict_servers = nov.list_vm()
        msg = convert_keyboard_inline(dict_servers)
        print(type(msg))
        print(msg)
        update.message.reply_text(u"VM status",
                                  reply_markup=msg)
    elif action == 'stop':
        name_vm = args.pop(0)
        nov.control(name_vm= name_vm, action_vm= action)
    elif action == 'start':
        name_vm = args.pop(0)
        nov.control(name_vm=name_vm, action_vm= action)
