"""Network plugin
/network in openstack!
"""
import pprint
from keystoneauth1.identity import v3
from keystoneauth1 import session
from neutronclient.v2_0 import client
# from prettytable import PrettyTable
from telebot.plugins import openstackutils

def handle(bot, update, args):
    net = openstackutils.Neutron('192.168.100.114', 'admin', 'locdev', 'admin')
    try:
        action = args.pop(0)
        if action == 'list':
            msg = net.list_network()
            update.message.reply_text(msg)
            return
        elif action == 'show':
            network_name = args.pop(0)
            msg = net.show_network(network_name)
            update.message.reply_text(msg)
            return
        elif action == 'create':
            network_name = args.pop(0)
            msg = net.create_network(network_name, args)
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
