from datetime import datetime
import json
import paho.mqtt.client as mqtt

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
        self._client.loop_stop()
        self._client.disconnect()

    def bind_device(self):
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 10,
            'device_id': self.device_id,
            'tag': 'bind_control',
            'bind_ctrl': 1
        }
        self._publish_data()

    def unbind_device(self):
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 10,
            'device_token': self.device_token,
            'device_id': self.device_id,
            'tag': 'unbind_control',
            'bind_ctrl': 0
        }
        self._publish_data()

    def add_profiles_data(self, *identifiers):
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 7,
            'device_token': self.device_token,
            'device_id': self.device_id,
            'tag': 'add_profiles',
            'piclib_manage': 0,
            'param': {
                'lib_name': '',
                'lib_id': '',
                'server_ip': self.host,
                'server_port': 7777,
                'pictures': []
            }
        }
        if identifiers:
            profiles = self._database_management.get_profiles(identifiers)
        else:
            profiles = self._database_management.get_profiles()
        for profile in profiles:
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
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 7,
            'device_token': self.device_token,
            'device_id': self.device_id,
            'tag': 'remove_all_profiles',
            'piclib_manage': 1
        }
        self._publish_data()

    def remove_profiles_data(self, *identifiers):
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 7,
            'device_token': self.device_token,
            'device_id': self.device_id,
            'tag': 'remove_profiles',
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
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 7,
            'device_token': self.device_token,
            'device_id': self.device_id,
            'tag': 'query_profiles',
            'piclib_manage': 4,
            'page': page
        }
        self._publish_data()

    def get_device_info(self):
        self.data = {
            'mqtt_cmd': 2,
            'device_id': self.device_id,
            'tag': 'device_info',
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
            'tag': 'platform define',
            'network_cofnig': {
                'id_addr': ip_address,
                'net_mask': net_mask,
                'gateway': gateway,
                'DDNS1': DDNS1,
                'DDNS2': DDNS2,
                'DHCP': DHCP
            }
        }
        self._publish_data()

    def update_face_recognition_configuration(self, dec_face_num: int = 1, dec_interval: int = 1):
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 3,
            'device_token': self.device_token,
            'device_id': self.device_id,
            'tag': 'face_recognition_config',
            'face_config': {
                'dec_face_num': dec_face_num,
                'dec_interval': dec_interval
            }
        }
        self._publish_data()

    def update_remote_configuration(self, volume: int = 0,
                                    screen_brightness: int = 45,
                                    light_supplementary: bool = False,
                                    wiegand_dir: int = 0,
                                    wiegand_write_bit: int = 26
                                    ):
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 4,
            'device_token': self.device_token,
            'device_id': self.device_id,
            'tag': 'remote_config',
            'remote_config': {
                'volume': volume,
                'screen_brightness': screen_brightness,
                'light_supplementary': light_supplementary,
                'wiegand_dir': wiegand_dir,
                'wiegand_write_bit': wiegand_write_bit
            }
        }
        self._publish_data()

    def reboot_device(self):
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 9,
            'device_token': self.device_token,
            'device_id': self.device_id,
            'tag': 'system_maintenance',
            'sys_maintain': {
                'reboot': 1,
                'reset': 0
            }
        }
        self._publish_data()

    def reset_device(self):
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 9,
            'device_token': self.device_token,
            'device_id': self.device_id,
            'tag': 'system_maintenance',
            'sys_maintain': {
                'reboot': 0,
                'reset': 1
            }
        }
        self._publish_data()

    def update_temperature_configuration(self,
                                         temperature_check: bool = True,
                                         stranger_passage: bool = False,
                                         mask_detection: bool = False,
                                         alarm_temperature: float = 37.5,
                                         temperature_compensation: float = 0,
                                         record_save_time: int = -1,
                                         save_record: bool = True,
                                         save_jpeg: bool = True,
                                         ):
        self.data = {
            'mqtt_cmd': 1,
            'mqtt_operate_id': 6,
            'device_token': self.device_token,
            'device_id': self.device_id,
            'tag': 'temperature_config',
            'temperature_fun': {
                'temp_dec_en': temperature_check,
                'stranger_pass_en': stranger_passage,
                'make_check_en': mask_detection,
                'alarm_temp': alarm_temperature,
                'temp_comp': temperature_compensation,
                'record_save_time': record_save_time,
                'save_record': save_record,
                'save_jpeg': save_jpeg
            }
        }
        self._publish_data()
