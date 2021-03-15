import sys
import os
from datetime import datetime
import time
import json
import paho.mqtt.client as mqtt
import widget.models as models
from widget.management import DBManagement


class PublishPlatform:
    def __init__(self, host: str, port: int = 1883, client_name: str = 'PC'):
        self._host = host
        self._port = port
        self.client_name = client_name
        self._topic = 'SubscribeTest'
        self._device_id = str
        self._device_token = str
        self._data = {}
        self._client = mqtt.Client(client_name)
        self._database_management = DBManagement()

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, value):
        self._device_id = value

    @property
    def device_token(self):
        return self._device_token

    @device_token.setter
    def device_token(self, value):
        self._device_token = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if isinstance(value, dict):
            self._data = value

    def set_device(self, device_id: str, device_token: str = None):
        self.device_id = device_id
        self.device_token = device_token

    def _publish_data(self):
        self._client.connect(self.host, self.port)
        self._client.loop_start()
        self._client.publish(self._topic, json.dumps(self.data, indent=4))
        # time.sleep(1)
        self._client.loop_stop()
        self._client.disconnect()

    def bind_device(self):
        self.data = {"mqtt_cmd": 1,
                     "mqtt_operate_id": 10,
                     'device_id': self.device_id,
                     'tag': "platform define",
                     'bind_ctrl': 1}
        self._publish_data()

    def unbind_device(self):
        self.data = \
            {
                "mqtt_cmd": 1,
                "mqtt_operate_id": 10,
                'device_token': self.device_token,
                'device_id': self.device_id,
                'tag': "platform define",
                'bind_ctrl': 0
            }
        self._publish_data()

    def add_profiles_data(self, *identifiers):
        self.data = \
            {
                "mqtt_cmd": 1,
                "mqtt_operate_id": 7,
                'device_token': self.device_token,
                'device_id': self.device_id,
                'tag': "platform define",
                'piclib_manage': 0,
                'param':
                    {
                        'lib_name': '',
                        'lib_id': '',
                        'server_ip': self.host,
                        'server_port': 7777,
                        'pictures': []
                    }
            }
        for profile in self._database_management.get_profiles(identifiers):
            self.data['param']['pictures'].append({})
            index = len(self.data['param']['pictures']) - 1
            self.data['param']['pictures'][index]['active_time'] \
                = f"{datetime.strftime(datetime.now(), '%Y')}/01/1 00:00:01"
            self.data['param']['pictures'][index]['user_id'] = profile.id
            self.data['param']['pictures'][index]['user_name'] = profile.name
            self.data['param']['pictures'][index]['end_time'] \
                = f"{datetime.strftime(datetime.now(), '%Y')}/12/30 23:59:59"
            self.data['param']['pictures'][index]['p_id'] = 'null'
            self.data['param']['pictures'][index]['picture'] = profile.face
        self._publish_data()

    def remove_all_profiles_data(self):
        self.data = \
            {
                "mqtt_cmd": 1,
                "mqtt_operate_id": 7,
                'device_token': self.device_token,
                'device_id': self.device_id,
                'tag': "platform define",
                'piclib_manage': 1
            }
        self._publish_data()

    def remove_profiles_data(self, *identifiers):
        self.data = \
            {
                "mqtt_cmd": 1,
                "mqtt_operate_id": 7,
                'device_token': self.device_token,
                'device_id': self.device_id,
                'tag': "platform define",
                'piclib_manage': 3,
                'param': {
                    'users': [
                        {
                            'user_id': identifier
                        } for identifier in identifiers
                    ]
                }
            }
        self._publish_data()

    def query_profiles_data(self, page: int = -1):
        self.data = \
            {
                "mqtt_cmd": 1,
                "mqtt_operate_id": 7,
                'device_token': self.device_token,
                'device_id': self.device_id,
                'tag': "query",
                'piclib_manage': 4,
                'page': page
            }
        self._publish_data()

    def get_device_info(self):
        self.data = {
            'mqtt_cmd': 2,
            'device_id': self.device_id,
            'tag': 'device info',
            'device_token': self.device_token
        }
        self._publish_data()

    def update_network_configuration(self, ip_address: str,
                                     gateway: str,
                                     net_mask: str = '255.255.255.0',
                                     DDNS1: str = None,
                                     DDNS2: str = '8.8.8.8',
                                     DHCP: bool = False
                                     ):
        if not DDNS1:
            DDNS1 = gateway
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 2,
            'device_token': self.device_token,
            'device_id': self.device_id,
            'tag': 'network_config',
            'network_cofnig': {
                'id_addr': ip_address,
                'net_mask': net_mask,
                'gateway': gateway,
                'DDNS1': DDNS1,
                'DDNS2': DDNS2,
                'DHCP': DHCP
            }
        }
        print(self.data)
        self._publish_data()
