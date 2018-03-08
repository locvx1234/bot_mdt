"""Network plugin
/network in openstack!
"""
import pprint
from telebot.plugins import networkutils


def handle(bot, update, args):
    net = networkutils.Neutron('192.168.100.114', 'admin', 'locdev', 'admin')
    try:
        action = args.pop(0)
        if action == 'list':
            network_list = net.list_network()
            pp = pprint.PrettyPrinter(indent=4)
            # pp.pprint("-----------------------")
            pp.pprint(network_list)
            update.message.reply_text(network_list)
            return
        elif action == 'show':
            network_name = args.pop(0)
            network_list = net.show_network(network_name)
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(network_list)
            update.message.reply_text(network_list)
            return
        elif action == 'create':
            network_name = args.pop(0)
            network_options = {'name': network_name, 'admin_state_up': True, 'shared': False}
            net.create_network(network_options)
            msg = "Create network complete"
            update.message.reply_text(msg)
            return
        elif action == 'delete':
            network_name = args.pop(0)
            msg = net.delete_network(network_name)
            update.message.reply_text(msg)
            return
        else:
            raise ValueError
    except(IndexError, ValueError):
        update.message.reply_text(
            'Usage: \n  - /network list to list all network  '
            '\n  - /network show <name-network> to show detail a network'
            '\n  - /network delete <name-network> to delete a network')
