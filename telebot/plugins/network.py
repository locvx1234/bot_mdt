"""Network plugin
/network in openstack!
"""
import pprint
from keystoneauth1.identity import v3
from keystoneauth1 import session
from neutronclient.v2_0 import client
# from prettytable import PrettyTable


def authenticate(ip, username, password, proj_name):
    auth_url = 'http://{}/identity/v3'.format(ip)
    auth = v3.Password(auth_url=auth_url,
                       user_domain_name='default',
                       username=username, password=password,
                       project_domain_name='default',
                       project_name=proj_name)
    sess = session.Session(auth=auth)
    return sess


def str_to_bool(s):
    """
    Convert from specific string to bool value
    :param s:
    :return: boolean
    """
    if s == 'True' or s == 'true':
        return True
    elif s == 'False' or s == 'false':
        return False
    else:
        raise ValueError


def count_item(networks, network_name):
    """
    how many networks are named 'network_name'
    """
    count = 0
    for item in networks["networks"]:
        if item['name'] == network_name:
            count += 1
    return count


def list_network(networks, subnets):
    """
    List all network
    :command: /network list
    """
    msg = 'List network : \n\n'
    for item in networks["networks"]:
        if item["name"] != '':
            name = item["name"]
        else:
            name = '(' + item["id"][:13] + ')'

        subnets_name = ''
        for subnet in item["subnets"]:
            subnet_name = find_name_by_id(subnets, subnet)
            subnets_name += '   - ' + subnet_name + '\n'
        msg += 'Name : ' + name + '\nSubnet:\n' + subnets_name + '\n\n'
    return msg


def show_network(networks, subnets, network_name):
    """
    Show infomation of network by name
    """
    if not any(item['name'] == network_name for item in networks["networks"]):
        msg = network_name + ' don\'t exist!'
    else:
        msg = ''
        for item in networks["networks"]:
            if item['name'] == network_name:
                identity = item['id']
                name = item['name']
                status = item['status']
                subnets_item = item['subnets']
                subnets_list = ''
                for subnet in subnets_item:
                    subnets_list += '\n     - ' + find_name_by_id(subnets, subnet) + '  -  ' + subnet
                print(subnets)
                msg += 'ID: ' + str(identity) + '\n' + 'Name: ' + str(name) + '\n' + \
                       'Status: ' + str(status) + '\n' + 'Subnet: ' + subnets_list + '\n\n'
                print(msg)
    return msg


def create_network(neutron, args):
    """
    Create a network
    :command: /network create -name <network-name>
            [-admin_state_up <True/False> -shared <True/False>]
    """
    network_options = {'name': '', 'admin_state_up': True, 'shared': False}  # default
    keys_type = {'name': 'str', 'admin_state_up': 'bool', 'shared': 'bool'}
    try:
        print(args)
        for i in range(0, len(args), 2):
            if args[i].startswith("-"):
                _key = args[i][1:]
                if _key in keys_type:
                    if keys_type[_key] == 'bool':
                        args[i+1] = str_to_bool(args[i+1])
                    network_options[_key] = args[i+1]
                else:
                    msg = 'Non-existent option : ' + _key
                    return msg
            else:
                raise ValueError
        print(network_options)
        neutron.create_network({'network': network_options})
        msg = 'Create network complete!'
    except(IndexError, ValueError):
        msg = 'Usage: /network create -name <instance-name> ' \
              '-shared <True/False> -admin_state_up <True/False>'
    return msg


def delete_port(neutron, network_id):
    """
    Delete all interfaces attached to network
    """
    ports = neutron.list_ports()
    for item in ports['ports']:
        if item['network_id'] == network_id:
            neutron.delete_port(item['id'])
    return


def delete_network(neutron, networks, network_name):
    msg = ''
    try:        # delete by id
        delete_port(neutron, network_name)
        neutron.delete_network(network_name)
        msg = 'Delete network complete!'
    except:     # delete by name
        if count_item(networks, network_name) == 1:
            network_id = None
            for item in networks["networks"]:
                if item["name"] == network_name:
                    network_id = item["id"]
                    print("ID : " + network_id)
            if network_id is not None:
                delete_port(neutron, network_id)
                neutron.delete_network(network_id)
                msg = 'Delete network complete!'
        elif count_item(networks, network_name) > 1:
            msg = network_name + ' is duplicate. Use id instead'
        else:      # equal 0
            msg = network_name + ' don\'t exist!'
    return msg


def find_id_by_name(subnets, subnet_name):
    list_id = []
    for item in subnets["subnets"]:
        if item["name"] == subnet_name:
            list_id.append(item["id"])
    return list_id


def find_name_by_id(subnets, subnet_id):
    for item in subnets["subnets"]:
        if item["id"] == subnet_id and item["name"] != '':
            return item["name"]
        elif item["id"] == subnet_id:
            return '(' + item["id"][:13] + ')'
    return


def handle(bot, update, args):
    sess = authenticate('192.168.100.114', 'admin', 'locdev', 'admin')
    neutron = client.Client(session=sess)
    networks = neutron.list_networks()
    subnets = neutron.list_subnets()
    # for debug <<<
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(networks)
    # >>>

    try:
        action = args.pop(0)
        if action == 'list':
            msg = list_network(networks, subnets)
            update.message.reply_text(msg)
            return
        elif action == 'show':
            network_name = args.pop(0)
            msg = show_network(networks, subnets, network_name)
            update.message.reply_text(msg)
            return
        elif action == 'create':
            msg = create_network(neutron, args)
            update.message.reply_text(msg)
            return
        elif action == 'delete':
            network_name = args.pop(0)
            msg = delete_network(neutron, networks, network_name)
            update.message.reply_text(msg)
            return
        else:
            raise ValueError
    except(IndexError, ValueError):
        update.message.reply_text(
            'Usage: /network list or /network show <name-network> or /network delete <name-network>')



