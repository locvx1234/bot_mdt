from keystoneauth1.identity import v3
from keystoneauth1 import session
from neutronclient.v2_0 import client as neutronclient


def str_to_bool(s):
    """
    Convert from specific string to bool value
    :return: boolean
    """
    if s == 'True' or s == 'true':
        return True
    elif s == 'False' or s == 'false':
        return False
    else:
        raise ValueError


class Base:
    def __init__(self, ip, username, password, project_name):
        self.ip = ip
        self.username = username
        self.password = password
        self.project_name = project_name
        auth_url = 'http://{}/identity/v3'.format(self.ip)
        auth = v3.Password(auth_url = auth_url, user_domain_name = 'default', username = self.username,
                            password = self.password, project_domain_name = 'default', project_name = self.project_name)
        self.sess = session.Session(auth = auth)


class Neutron(Base):
    def __init__(self, ip, username, password, project_name):
        Base.__init__(self, ip, username, password, project_name)
        self.neutron = neutronclient.Client(session=self.sess)
        self.networks = self.neutron.list_networks()
        self.subnets = self.neutron.list_subnets()
        self.ports = self.neutron.list_ports()

    def _find_network_name_by_id(self, subnets, subnet_id):
        for item in subnets["subnets"]:
            if item["id"] == subnet_id and item["name"] != '':
                return item["name"]
            elif item["id"] == subnet_id:
                return '(' + item["id"][:13] + ')'
        return

    def _count_network(self, network_name):
        """
        how many networks are named 'network_name'
        """
        count = 0
        for network in self.networks["networks"]:
            if network['name'] == network_name:
                count += 1
        return count

    def _check_network_id_exist(self, network_id):
        for network in self.networks["networks"]:
            if network['id'] == network_id:
                return True
        else:
            return False

    # def _count_port(self, network_id):
    #     # number of port with id = network_id
    #     count = 0
    #     for item in self.ports['ports']:
    #         if item['network_id'] == network_id:
    #             count += 1
    #     return count

    def list_network(self):
        """
        List all network
        :command: /network list
        """
        msg = 'List network : \n\n'
        for item in self.networks["networks"]:
            if item["name"] != '':
                name = item["name"]
            else:
                name = '(' + item["id"][:13] + ')'

            subnets_name = ''
            for subnet in item["subnets"]:
                subnet_name = self._find_network_name_by_id(self.subnets, subnet)
                subnets_name += '   - ' + subnet_name + '\n'
            msg += 'Name : ' + name + '\nSubnet:\n' + subnets_name + '\n\n'
        return msg

    def show_network(self, network_name):
        """
        Show infomation of network by name
        """
        if not any(item['name'] == network_name for item in self.networks["networks"]):
            msg = network_name + ' don\'t exist!'
        else:
            msg = ''
            for item in self.networks["networks"]:
                if item['name'] == network_name:
                    identity = item['id']
                    name = item['name']
                    status = item['status']
                    subnets_item = item['subnets']
                    subnets_list = ''
                    for subnet in subnets_item:
                        subnets_list += '\n     - ' + self._find_network_name_by_id(self.subnets, subnet) + '  -  ' + subnet
                    msg += 'ID: ' + str(identity) + '\n' + 'Name: ' + str(name) + '\n' + \
                           'Status: ' + str(status) + '\n' + 'Subnet: ' + subnets_list + '\n\n'
                    print(msg)
        return msg

    def create_network(self, network_name, args):
        """
        Create a network
        :command: /network create <network name>
                [-admin_state_up <True/False> -shared <True/False>]
        """
        network_options = {'name': network_name, 'admin_state_up': True, 'shared': False}  # default
        keys_type = {'admin_state_up': 'bool', 'shared': 'bool'}
        try:
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
            self.neutron.create_network({'network': network_options})
            msg = 'Create network complete!'
        except(IndexError, ValueError):
            msg = 'Usage: /network create <network name> ' \
                  '-shared <True/False> -admin_state_up <True/False>'
        return msg

    def delete_port(self, network_id):
        """
        Delete all interfaces attached to network
        """
        for port in self.ports['ports']:
            if port['network_id'] == network_id:
                self.neutron.delete_port(port['id'])
        return

    def delete_network(self, network_name):
        msg = ''
        if self._check_network_id_exist(network_name):  # delete by id, `network_name` are understood as `network_id`
            self.delete_port(network_name)
            self.neutron.delete_network(network_name)
            msg = 'Delete network complete!'
        else:   # delete by name
            if self._count_network(network_name) == 1:
                network_id = None
                for item in self.networks["networks"]:
                    if item["name"] == network_name:
                        network_id = item["id"]
                        print("ID : " + network_id)
                if network_id is not None:
                    self.delete_port(network_id)
                    self.neutron.delete_network(network_id)
                    msg = 'Delete network complete!'
            elif self._count_network(network_name) > 1:
                msg = network_name + ' is duplicate. Use id instead'
            else:      # equal 0
                msg = network_name + ' don\'t exist!'
        return msg
