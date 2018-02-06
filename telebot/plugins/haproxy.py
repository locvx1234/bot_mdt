import json
from haproxystats import HAProxyServer
from prettytable import PrettyTable
from telebot import config

def handle(bot, update):
    print('minh')
    haproxy = HAProxyServer(config.url_monitor_ha, user=config.user_name_ha,
                            password=
                            config.pass_ha)
    data = json.loads(haproxy.to_json())
    print(data)
    tables = PrettyTable(['Name backend', 'status', ''])
    for i in range(len(data[haproxy.name]["backends"][0]["listeners"])):
        name_sv = data[haproxy.name]["backends"][0]["listeners"][i]["svname"]
        status_sv = data[haproxy.name]["backends"][0]["listeners"][i]["status"]
        type_sv = data[haproxy.name]["backends"][0]["listeners"][i]["act"]
        if type_sv == 1:
            a = 'ACTIVE'
        else:
            a = 'BACKUP'
        tables.add_row([str(name_sv), str(status_sv), a])
    print(tables)
    update.message.reply_text(str(tables))

