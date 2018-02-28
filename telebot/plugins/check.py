IP = '192.168.100.48'
USERNAME = 'admin'
PASSWORD = 'minhkma'
PROJECT_NAME = 'admin'
AUTH_URL = 'http://{}/identity/v3'.format(IP)

url_monitor_ha = '192.168.100.37:80/monitor'
user_name_ha = 'root'
pass_ha = 'meditech2017'
from keystoneauth1.identity import v3
from keystoneauth1 import session
from neutronclient.v2_0 import client
import novaclient.client as novaclient
from telebot import config


def form(my_list):
    msg = ''
    width_col1 = max([len(x) for x in my_list.keys()])
    width_col2 = max([len(x) for x in my_list.values()])
    def f(ind):
        return my_list[ind]
    for i in my_list:
        msg += "{0:<{col1}} : {1:<{col2}}\n".\
            format(i,f(i),col1=width_col1,col2=width_col2)
    return msg

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


def neutron():
    sess = authenticate()
    neutron = client.Client(session=sess)
    my_list_agent_neutron = {}
    agents = neutron.list_agents()
    for count_agents in range(len(agents['agents'])):
        if agents['agents'][count_agents]['alive'] == True:
            my_list_agent_neutron[agents['agents'][count_agents][
                'agent_type']] = ':=)'
        else:
            my_list_agent_neutron[agents['agents'][count_agents][
                'agent_type']] = ':('
    return my_list_agent_neutron

def vm():
    sess = authenticate()
    nova = novaclient.Client("2.1", session=sess)
    my_list_vm = {"Name_instance":"status"}
    server_list = nova.servers.list()
    for count_server, i in enumerate(server_list):
        my_list_vm[server_list[count_server].name] = server_list[
            count_server].status
    return my_list_vm

def nova():
    """
    List status service agent in nova

    :return: my_list_service_nova
    """
    sess = authenticate()
    nova = novaclient.Client("2.1", session=sess)
    my_list_services_nova = {}
    services = nova.services.list()
    for count_services, j in enumerate(services):
        data_dict = services[count_services]._info
        my_list_services_nova[data_dict['binary']] = data_dict['state']
    return my_list_services_nova

def handle(bot, update, args):
    try:
        action = args.pop(0)
        if action == 'nova':
            my_list_services_nova = nova()
            print(my_list_services_nova)
            msg_nova = form(my_list_services_nova)
            print(msg_nova)
            update.message.reply_text(msg_nova)
            return
        if action == 'neutron':
            my_list_agent_neutron = neutron()
            msg_neutron = form(my_list_agent_neutron)
            update.message.reply_text(msg_neutron)
            return
        else:
            raise ValueError
    except(IndexError, ValueError):
        update.message.reply_text('Usage: /check nova or /check neutron ')

