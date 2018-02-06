from keystoneauth1.identity import v3
from keystoneauth1 import session
import novaclient.client as novaclient
from telebot import config
from prettytable import PrettyTable

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

def vm():
    sess = authenticate()
    nova = novaclient.Client("2.1", session=sess)
    tables_list_vm = PrettyTable(['NAME VM', 'STATUS'])
    server_list = nova.servers.list()
    for count_server, i in enumerate(server_list):
        name_vm = server_list[count_server].name
        status_vm = server_list[count_server].status
        tables_list_vm.add_row([name_vm, status_vm])
    return tables_list_vm, server_list

def control_vm(name_vm_stop, action_vm):
    sess = authenticate()
    nova = novaclient.Client("2.1", session=sess)
    server_list = nova.servers.list()
    for count_server, i in enumerate(server_list):
        name_vm = server_list[count_server].name
        if name_vm_stop == name_vm:
            if action_vm == "stop":
                server_list[count_server].stop()
            if action_vm == "start":
                server_list[count_server].start()
        else:
            break
    tables_list_vm, server_list = vm()
    return tables_list_vm


def handle(bot, update, args):
    action = args.pop(0)
    if action == 'list':
        my_list_vm, servers_list = vm()
        update.message.reply_text(str(my_list_vm))
    elif action == 'start':
        print(type(args.pop(0)))
        control_vm(str(args.pop(0)), 'start')
    elif action == 'stop':
        print(args.pop(0))
        control_vm(str(args.pop(0)), 'stop')

