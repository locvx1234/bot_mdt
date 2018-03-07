import pprint
from keystoneauth1.identity import v3
from keystoneauth1 import session
from neutronclient.v2_0 import client as neutronclient

from telebot.plugins import openstackutils


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

class Neutron(openstackutils.Base):
    def __init__(self, ip, username, password, project_name):
        super().__init__(ip, username, password, project_name)
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

    def list_network(self):
        """
        List all network
        Extract a list networks with a subset of keys
        """
        network_list = []
        for item in self.networks["networks"]:
            network_keys = {'admin_state_up', 'description', 'id', 'name', 'project_id', 'shared',
                            'status', 'subnets'}
            network_dict = {key: value for key, value in item.items() if key in network_keys}
            network_list.append(network_dict)
        return network_list

    def show_network(self, network_name):
        """
        Show infomation of network by name
        """
        network_list = []
        for item in self.list_network():
            if item['name'] == network_name:
                network_list.append(item)
        return network_list

    def create_network(self, network_options):
        """
        Create a network
        :command: /network create <network name>
                [-admin_state_up <True/False> -shared <True/False>]
        """
        # network_options = {'name': network_name, 'admin_state_up': True, 'shared': False}  # default
        self.neutron.create_network({'network': network_options})
        return

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
