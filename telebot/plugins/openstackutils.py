from keystoneauth1.identity import v3
from keystoneauth1 import session

class Base:
    def __init__(self, ip, username, password, project_name):
        self.ip = ip
        self.username = username
        self.password = password
        self.project_name = project_name
        auth_url = 'http://{}/identity/v3'.format(self.ip)
        auth = v3.Password(auth_url = auth_url,
                           user_domain_name = 'default',
                           username = self.username,
                           password = self.password,
                           project_domain_name = 'default',
                           project_name = self.project_name)
        self.sess = session.Session(auth = auth)
