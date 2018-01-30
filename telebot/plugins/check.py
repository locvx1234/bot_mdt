from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client
from prettytable import PrettyTable

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
    msg = ''
    sess = authenticate()
    nova = client.Client("2.1", session=sess)
    tables_servers = PrettyTable(['Name_instance', 'status'])
    server_list = nova.servers.list()
    for count_server,i in enumerate(server_list):
        Name_instance = server_list[count_server].name
        status = server_list[count_server].status
        tables_servers.add_row([Name_instance, status])
    msg = msg + str(tables_servers) + '\n'
    tables_services = PrettyTable(['binary', 'host', 'status', 'state', 'zone'])
    services = nova.services.list()
    for count_services,j in enumerate(services):
        data_dict = services[count_services]._info
        binary = data_dict['binary']
        host = data_dict['host']
        status = data_dict['status']
        state = data_dict['state']
        zone = data_dict['zone']
        tables_services.add_row([binary, host, status, state, zone])
    msg = msg + str(tables_services) + '\n'
    tables_flavors = PrettyTable(['ID', 'Name', 'Memory_MB', 'Disk', 'Ephemeral',
                                  'Swap', 'VCPUsRXTX_Factor', 'Is_Public'])
    flavors = nova.flavors.list()
    for count_flavors,k in enumerate(flavors):
        data_favors = flavors[count_flavors]._info
        ID = data_favors['id']
        Name = data_favors['name']
        Memory_MB = data_favors['ram']
        Disk = data_favors['disk']
        Ephemeral = data_favors['OS-FLV-EXT-DATA:ephemeral']
        Swap = data_favors['swap']
        VCPUsRXTX_Factor = data_favors['vcpus']
        Is_Public = data_favors['os-flavor-access:is_public']
        tables_flavors.add_row([ ID, Name, Memory_MB, Disk, Ephemeral, Swap, VCPUsRXTX_Factor, Is_Public])
    msg = msg + str(tables_flavors) + '\n'
    try:
        action = args.pop(0)
        if action == 'status':
            update.message.reply_text(msg)
            return
        else:
            raise ValueError
    except(IndexError, ValueError):
        update.message.reply_text('Usage: /check status')
