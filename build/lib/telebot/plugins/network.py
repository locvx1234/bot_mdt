"""Network plugin
/network in openstack!
"""
import pprint
from keystoneauth1.identity import v3
from keystoneauth1 import session
from neutronclient.v2_0 import client


def authenticate():
    IP = '192.168.100.114'
    USERNAME = 'admin'
    PASSWORD = 'locdev'
    PROJECT_NAME = 'admin'
    AUTH_URL = 'http://{}/identity/v3'.format(IP)
    auth = v3.Password(auth_url=AUTH_URL,
                       user_domain_name='default',
                       username=USERNAME,password=PASSWORD,
                       project_domain_name='default',
                       project_name=PROJECT_NAME)
    sess = session.Session(auth=auth)
    return sess

def handle(bot, update, args):
    sess = authenticate()
    neutron = client.Client(session=sess)
    networks = neutron.list_networks()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(networks)
    network_len = len(networks["networks"])
    network_list = []
    for i in range(network_len):
        network_list.append(networks["networks"][i]["name"])

    try:
        action = args.pop(0)
        if action == 'list':
            update.message.reply_text(network_list)
            return
        elif action == 'show':
            network_name = args.pop(0)
            if network_name in network_list:
                for i in range(network_len):
                    if networks["networks"][i]["name"] == network_name:
                        pp_output = pprint.pformat(networks["networks"][i], 4)
                        update.message.reply_text(pp_output)
            else:
                update.message.reply_text(network_name + ' don\'t exist!')
            return
        elif action == 'create':
            network_name = args.pop(0)
            if network_name in network_list:
                update.message.reply_text(network_name + ' already exist!')
            else:
                network_create = {'name': network_name, 'admin_state_up': True}
                neutron.create_network({'network': network_create})
                update.message.reply_text('Create network complete!')
            return
        elif action == 'delete':
            network_name = args.pop(0)
            if network_name in network_list:
                for i in range(network_len):
                    if networks["networks"][i]["name"] == network_name:
                        network_id = networks["networks"][i]["id"]
                neutron.delete_network(network_id)
                update.message.reply_text('Delete network complete!')
            else:
                update.message.reply_text(network_name + ' don\'t exist!')
            return
        else:
            raise ValueError
    except(IndexError, ValueError):
        update.message.reply_text(
            'Usage: /network list or /network show <name-network> or /network delete <name-network>')



