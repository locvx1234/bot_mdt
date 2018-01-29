"""Network plugin
/network in openstack!
"""
from keystoneauth1.identity import v2
from keystoneauth1 import session
from keystoneclient.v2_0 import client
from neutronclient.v2_0 import client
import pprint


def authenticate():
    auth_url = 'http://192.168.100.50:5000/v2.0'
    username = 'admin'
    password = 'Welcome123'
    tenant_name = 'admin'
    auth = v2.Password(username=username, password=password, tenant_name=tenant_name, auth_url=auth_url)
    sess = session.Session(auth=auth)
    # token = sess.get_token()
    # print(token)
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



