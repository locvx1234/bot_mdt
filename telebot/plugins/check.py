from keystoneauth1.identity import v3
from keystoneauth1 import session
from neutronclient.v2_0 import client
import novaclient.client as novaclient
from config import *

def form(mylist):
    msg = ''
    width_col1 = max([len(x) for x in mylist.keys()])
    width_col2 = max([len(x) for x in mylist.values()])
    def f(ind):
        return mylist[ind]
    for i in mylist:
        msg += "{0:<{col1}} : {1:<{col2}}\n".format(i,f(i),
                                                 col1=width_col1,col2=width_col2)
    return msg

def authenticate():
    AUTH_URL = 'http://{}/identity/v3'.format(IP)
    auth = v3.Password(auth_url=AUTH_URL,
                       user_domain_name='default',
                       username=USERNAME,password=PASSWORD,
                       project_domain_name='default',
                       project_name=PROJECT_NAME)
    sess = session.Session(auth=auth)
    return sess

def neutron():
    sess = authenticate()
    neutron = client.Client(session=sess)
    mylist_agent_neutron = {}
    agents = neutron.list_agents()
    for count_agents in range(len(agents['agents'])):
        if agents['agents'][count_agents]['alive'] == True:
            mylist_agent_neutron[agents['agents'][count_agents]['agent_type']] = ':=)'
        else:
            mylist_agent_neutron[agents['agents'][count_agents]['agent_type']] = ':('
    return mylist_agent_neutron

def vm():
    sess = authenticate()
    nova = novaclient.Client("2.1", session=sess)
    mylist_vm = {"Name_instance":"status"}
    server_list = nova.servers.list()
    for count_server, i in enumerate(server_list):
        mylist_vm[server_list[count_server].name] = server_list[count_server].status
    return mylist_vm

def nova():
    sess = authenticate()
    nova = novaclient.Client("2.1", session=sess)
    mylist_services_nova = {}
    services = nova.services.list()
    for count_services, j in enumerate(services):
        data_dict = services[count_services]._info
        mylist_services_nova[data_dict['binary']] = data_dict['state']
    return mylist_services_nova

def handle(bot, update, args):
    try:
        action = args.pop(0)
        if action == 'nova':
            mylist_services_nova = nova()
            print(mylist_services_nova)
            msg_nova = form(mylist_services_nova)
            print(msg_nova)
            update.message.reply_text(msg_nova)
            return
        if action == 'neutron':
            mylist_agent_neutron = neutron()
            msg_neutron = form(mylist_agent_neutron)
            update.message.reply_text(msg_neutron)
            return
        else:
            raise ValueError
    except(IndexError, ValueError):
        update.message.reply_text('Usage: /check status')

