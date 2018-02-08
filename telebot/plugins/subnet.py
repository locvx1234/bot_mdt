"""Subnet plugin
/subnet in openstack!
"""
import pprint
from keystoneauth1.identity import v3
from keystoneauth1 import session
from neutronclient.v2_0 import client
import ipaddress


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
    if s == 'True' or s == 'true':
        return True
    elif s == 'False' or s == 'false':
        return False
    else:
        return 'ERR'


def validate_address(addr):
    try:
        ipaddress.ip_address(addr)
        return True
    except(IndexError, ValueError):
        return False


def validate_network(addr):
    try:
        ipaddress.ip_network(addr)
        return True
    except(IndexError, ValueError):
        return False


def validate_ip_version(num):
    if num == '4' or num == '6':
        return int(num)
    else:
        return 'ERR'


def find_network_name_by_id(networks, network_id):
    for item in networks["networks"]:
        if item["id"] == network_id and item["name"] != '':
            return item["name"]
        elif item["id"] == network_id:
            return '(' + item["id"][:13] + ')'
    return


def show_subnet(networks, subnets, subnet_name):
    if not any(item['name'] == subnet_name for item in subnets["subnets"]):
        msg = subnet_name + ' don\'t exist!'
    else:
        msg = ''
        for item in subnets["subnets"]:
            if item['name'] == subnet_name:
                identity = item['id']
                name = item['name']
                dhcp = item['enable_dhcp']
                ip_version = item['ip_version']
                cidr = item['cidr']
                gateway = item['gateway_ip']
                network = find_network_name_by_id(networks, item['network_id'])
                pool_start = item['allocation_pools'][0]['start']
                pool_end = item['allocation_pools'][0]['end']

                msg += 'ID: ' + str(identity) + '\n' + 'Name: ' + str(name) + '\n' + \
                       'DHCP: ' + str(dhcp) + '\n' + 'IP Version: ' + str(ip_version) + '\n' + \
                       'Cidr: ' + cidr + '\n' + 'Gateway: ' + gateway + '\n' + 'Network: ' + network + '\n' + \
                       'Pool: ' + pool_start + ' - ' + pool_end + '\n\n'
                print(msg)
    return msg


def create_subnet(neutron, networks, subnets, subnet_name, args):
    subnet_options = {'name': subnet_name, 'enable_dhcp': True, 'gateway_ip': None}
    keys_type = {'enable_dhcp': 'bool', 'gateway_ip': 'address', 'cidr': 'network', 'network': 'str', 'ip_version': 'int'}
    try:
        check = check_type(args, keys_type, subnet_options)
        if check != 'OK':
            return check

        msg = handle_network_arg(networks, subnet_options["network"])
        if msg.startswith('ERROR'):
            return msg
        else:
            subnet_options.pop('network')
            subnet_options['network_id'] = msg

        if all(x in subnet_options for x in ['cidr', 'ip_version', 'network_id']):
            network_id = subnet_options['network_id']
            cidr = ipaddress.ip_network(subnet_options['cidr'])
            if check_overlaps(cidr, get_cidr_in_network(networks, subnets, network_id)):
                msg = 'ERROR: Subnet overlaps'
            elif cidr.version != subnet_options['ip_version']:
                msg = 'ERROR: Network Address and IP version are inconsistent.'
            else:
                neutron.create_subnet({'subnet': subnet_options})
                msg = 'Create subnet complete!'
        else:
            msg = 'ERROR: Argument "-cidr" "-ip_version" and "-network" are required'
    except(IndexError, ValueError):
        msg = 'Usage: /subnet create <subnet-name> \n -network <network name/ID> \n -cidr <subnet/prefix> ' \
              '\n -ip_version <4/6> \n -gateway_ip <IP-gateway>'
    return msg


def list_subnet_in_network(networks, network_id):
    """
    Get all subnet id in the network
    :return: list
    """
    for network in networks["networks"]:
        if network["id"] == network_id:
            return network["subnets"]


def get_subnet_detail(subnets, subnet_id):
    """
    Get info of a subnet
    :return: dict
    """
    for subnet in subnets["subnets"]:
        if subnet["id"] == subnet_id:
            return subnet


def check_type(args, keys_type, options):
    for i in range(0, len(args), 2):
        if args[i].startswith("-"):
            _key = args[i][1:]
            if _key not in keys_type:
                msg = 'ERROR: Argument -' + _key + ' not support'
                return msg

            if keys_type[_key] == 'bool' and str_to_bool(args[i+1]) != 'ERR':
                args[i+1] = str_to_bool(args[i+1])
            elif keys_type[_key] == 'address' and validate_address(args[i+1]):
                pass
            elif keys_type[_key] == 'network' and validate_network(args[i+1]):
                pass
            elif keys_type[_key] == 'int' and validate_ip_version(args[i+1]) != 'ERR':
                args[i+1] = validate_ip_version(args[i+1])
            elif keys_type[_key] == 'str':
                pass
            else:
                msg = 'ERROR: Value of -' + _key + ' invalid'
                return msg
            options[_key] = args[i+1]
        else:
            raise ValueError
    return 'OK'


def get_cidr_in_network(networks, subnets, network_id):
    """
    Get all subnet in the network
    :return: list
    """
    cidr_list = []
    for subnet_id in list_subnet_in_network(networks, network_id):
        subnet = get_subnet_detail(subnets, subnet_id)
        cidr_list.append(ipaddress.ip_network(subnet["cidr"]))
    return cidr_list


def check_overlaps(cidr, cidr_list_already_exist):
    """
    Check a subnet overlaps with other subnet in the network
    :return: True if overlaps
    """
    for item in cidr_list_already_exist:
        if cidr.overlaps(item):
            return True
    return False


def count_network_by_name(networks, network_name):
    """
    how many networks are named 'network_name'
    """
    count = 0
    for item in networks["networks"]:
        if item['name'] == network_name:
            count += 1
    return count


def check_network_id_existed(networks, network_id):
    """
    Is the network 'network_id' existed ?
    """
    for item in networks["networks"]:
        if item['id'] == network_id:
            return True
    return False


def handle_network_arg(networks, network_arg):
    """
     network_arg is network_name or network_id? exist? unique or duplicate?
     :return: network_id or ERROR message
    """
    msg = ''
    if count_network_by_name(networks, network_arg) == 0 and check_network_id_existed(networks, network_arg) is False:
        msg = "ERROR: Network " + network_arg + " non existed!"
    elif count_network_by_name(networks, network_arg) > 1:
        msg = "ERROR: Network " + network_arg + " is duplicate, please use network ID instead"
    else:
        for item in networks["networks"]:
            if item["name"] == network_arg or item["id"] == network_arg:
                msg = item["id"]
    return msg


def count_subnet_by_name(subnets, subnet_name):
    """
    how many subnets are named 'subnet_name'
    """
    count = 0
    for item in subnets["subnets"]:
        if item['name'] == subnet_name:
            count += 1
    return count


def check_subnet_id_existed(subnets, subnet_id):
    """
    Is the subnet 'subnet_id' existed ?
    """
    for item in subnets["subnets"]:
        if item['id'] == subnet_id:
            return True
    return False


def delete_port_in_subnet(neutron, subnet_id):
    """
    Delete all interfaces attached to subnet
    """
    ports = neutron.list_ports()
    for port in ports['ports']:
        for item in port['fixed_ips']:
            if item['subnet_id'] == subnet_id:
                neutron.delete_port(port['id'])
    return


def delete_subnet(neutron, subnets, subnet_arg):
    msg = ''
    if count_subnet_by_name(subnets, subnet_arg) == 0 and check_subnet_id_existed(subnets, subnet_arg) is False:
        msg = "ERROR: Subnet " + subnet_arg + " non existed!"
    elif count_subnet_by_name(subnets, subnet_arg) > 1:
        msg = "ERROR: Subnet " + subnet_arg + " is duplicate, please use subnet ID instead"
    else:
        for subnet in subnets["subnets"]:
            if subnet["name"] == subnet_arg or subnet["id"] == subnet_arg:
                delete_port_in_subnet(neutron, subnet["id"])
                neutron.delete_subnet(subnet["id"])
                msg = 'Delete subnet ' + subnet_arg + ' successful!'
                break
    return msg


def handle(bot, update, args):
    sess = authenticate('192.168.100.114', 'admin', 'locdev', 'admin')
    neutron = client.Client(session=sess)
    networks = neutron.list_networks()
    subnets = neutron.list_subnets()

    # for debubg >>>
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(subnets)
    # <<<

    try:
        action = args.pop(0)
        if action == 'show':
            subnet_name = args.pop(0)
            msg = show_subnet(networks, subnets, subnet_name)
            update.message.reply_text(msg)
            return
        elif action == 'create':
            subnet_name = args.pop(0)
            if len(args):
                msg = create_subnet(neutron, networks, subnets, subnet_name, args)
            else:
                raise ValueError
            update.message.reply_text(msg)
            return
        elif action == 'delete':
            subnet_name = args.pop(0)
            msg = delete_subnet(neutron, subnets, subnet_name)
            update.message.reply_text(msg)
            return
        else:
            raise ValueError
    except(IndexError, ValueError):
        update.message.reply_text(
            'Usage: \n  - /subnet show <subnet name> to show info a subnet \n  '
            '- /subnet create <subnet name> -network <network name> -cidr <cidr> -ip_version <4/6> to create a subnet \n  '
            '- /subnet delete <subnet name/ID> to delete a subnet')
