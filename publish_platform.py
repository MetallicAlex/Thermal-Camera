import sys
import os
from datetime import datetime
import time
import json
import paho.mqtt.client as mqtt
import models


class PublishPlatform:
    def __init__(self, host, port=1883, client_name='PC'):
        self.host = host
        self.port = port
        self.client_name = client_name
        self.topic = 'SubscribeTest'
        self.device_id = '1'
        self.device_token = '2'
        self.data = {}
        self.__client = mqtt.Client(client_name)
        self.choice = {'0': ['Exit', sys.exit],
                       '1': ['Basic Parameter Configuration', self.__set_basic_parameter],
                       '2': ['Network Configuration', self.__set_network_configuration],
                       '3': ['Face Recognition Configuration', self.__set_face_recognition_configuration],
                       '4': ['Remote Parameter Configuration', self.__set_remote_parameter],
                       '5': ['Temperature Function Configuration', self.__set_temperature_function],
                       '6': ['Personnel Data Management', self.__set_personnel_data],
                       '7': ['System Maintenance', self.__set_system_maintenance],
                       '8': ['Binding Control', self.__bind_device]}

    def run(self):
        self.__client.connect(self.host, self.port)
        self.__client.loop_start()
        while True:
            option = self.__select_option('SEND MESSAGE TO DEVICE', self.choice)
            self.choice[option][1]()
            print(json.dumps(self.data, indent=4))
            self.__client.publish(self.topic, json.dumps(self.data, indent=4))
            if option == '8' and 'bind_ctrl' in self.data:
                if self.data['bind_ctrl'] == 1:
                    self.find_token()
        self.__client.loop_stop()

    def set_device(self, device_id, device_token=None):
        self.device_id = device_id
        self.device_token = device_token

    def unbind_device(self):
        self.__client.connect(self.host, self.port)
        self.__client.loop_start()
        for token in range(9999999999):
            self.device_token = f'{token}'.zfill(10)
            self.data['device_token'] = self.device_token
            self.data['device_id'] = self.device_id
            self.data['tag'] = "platform define"
            self.data['bind_ctrl'] = 0
            self.__client.publish(self.topic, json.dumps(self.data))
        self.__client.loop_stop()

    def find_token(self):
        while True:
            if os.path.isfile('token.txt'):
                time.sleep(2)
                with open('token.txt', 'r') as file:
                    self.device_token = file.readline()
                    print(self.device_token)
                break
        # os.remove('token.txt')

    def __select_option(self, title, choice):
        print(f'\n\n[{title}]')
        for key, value in choice.items():
            print(f'{key}) {value[0]}')
        return input('Select Option: ')

    def __normalize(self, value, min, max):
        if value < min:
            return min
        elif value > max:
            return max
        else:
            return value

    def __bind_device(self):
        choice = {'0': ['Unbinding'],
                  '1': ['Binding'],
                  '2': ['Back to Main Menu']
                  }
        bind_control = int(self.__select_option('BINDING CONTROL', choice))
        if bind_control == 2:
            return
        else:
            self.data = {"mqtt_cmd": 1, "mqtt_operate_id": 10}
        if bind_control == 0:
            self.data['device_token'] = self.device_token
        self.data['device_id'] = self.device_id
        self.data['tag'] = "platform define"
        self.data['bind_ctrl'] = bind_control

    def __set_basic_parameter(self):
        print(f'\n\n[BASIC PARAMETER CONFIGURATION]')
        self.data = {"mqtt_cmd": 1, "mqtt_operate_id": 1, 'device_token': self.device_token,
                     'device_id': self.device_id, 'tag': "platform define",
                     'basic_config': {}}
        self.data['basic_config']['dev_name'] = input('Device Name: ')
        self.data['basic_config']['dev_pwd'] = input('Device Password: ')
        self.data['basic_config']['sync_server_pts_en'] = True
        self.data['basic_config']['server_cur_pts'] = datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M')

    def __set_network_configuration(self):
        print(f'\n\n[NETWORK CONFIGURATION]')
        self.data = {"mqtt_cmd": 1, "mqtt_operate_id": 2, 'device_token': self.device_token,
                     'device_id': self.device_id, 'tag': "platform define",
                     'network_config': {}}  # 'network_cofnig'
        self.data['network_config']['ip_addr'] = input('IP-Address: ')
        self.data['network_config']['net_mask'] = input('Mask: ')
        self.data['network_config']['gateway'] = input('Gateway: ')
        self.data['network_config']['DDNS1'] = input('DDNS 1: ')
        self.data['network_config']['DDNS2'] = input('DDNS 2: ')
        self.data['network_config']['DHCP'] = input('DHCP (enter true or false): ')

    def __set_face_recognition_configuration(self):
        print(f'\n\n[FACE RECOGNITION CONFIGURATION]')
        self.data = {"mqtt_cmd": 1, "mqtt_operate_id": 3, 'device_token': self.device_token,
                     'device_id': self.device_id, 'tag': "platform define",
                     'face_config': {}}
        self.data['face_config']['dec_face_num'] = self.__normalize(int(input('Dec_Face_Num: ')), 0, 24)
        self.data['face_config']['dec_interval'] = self.__normalize(int(input('Dec_Interval: ')), 0, 24)
        print(self.data)

    def __set_remote_parameter(self):
        print(f'\n\n[REMOTE PARAMETER CONFIGURATION]')
        self.data = {"mqtt_cmd": 1, "mqtt_operate_id": 4, 'device_token': self.device_token,
                     'device_id': self.device_id, 'tag': "platform define",
                     'remote_config': {}}
        self.data['remote_config']['volume'] = self.__normalize(int(input('Volume: ')), 0, 24)
        self.data['remote_config']['screen_brightness'] = self.__normalize(int(input('Screen Brightness: ')), 45, 100)
        if input('Light Supplementary (enter true or false): ') == 'true':
            self.data['remote_config']['light_supplementary'] = True
        else:
            self.data['remote_config']['light_supplementary'] = False

    def __set_temperature_function(self):
        print(f'\n\n[TEMPERATURE FUNCTION CONFIGURATION]')
        self.data = {"mqtt_cmd": 1, "mqtt_operate_id": 6, 'device_token': self.device_token,
                     'device_id': self.device_id, 'tag': "platform define",
                     'temperature_fun': {}}
        self.data['temperature_fun']['temp_dec_en'] = input('Temperature Check (enter true or false): ')
        self.data['temperature_fun']['stranger_pass_en'] = input('Strangers Pass (enter true or false): ')
        self.data['temperature_fun']['make_check_en'] = input('Mask Detection (enter true or false): ')
        self.data['temperature_fun']['alarm_temp'] = float(input('Alarm Temperature: '))
        self.data['temperature_fun']['temp_comp'] = float(input('Temperature Compensation: '))
        self.data['temperature_fun']['record_save_time'] = int(input('How long the snapshot record is kept ('
                                                                     'unlimited = -1, not save = 0, corresponding '
                                                                     'time > 0): '))
        self.data['temperature_fun']['save_record'] = input('Recording Switch (enter true or false): ')
        self.data['temperature_fun']['save_jpeg'] = input('Snap Picture Switch (enter true or false): ')

    def __set_system_maintenance(self):
        print(f'\n\n[SYSTEM MAINTENANCE]')
        self.data = {"mqtt_cmd": 1, "mqtt_operate_id": 9, 'device_token': self.device_token,
                     'device_id': self.device_id, 'tag': "platform define",
                     'sys_maintain': {}}
        self.data['sys_maintain']['reboot'] = input('Reboot: ')
        self.data['sys_maintain']['reset'] = input('Reset: ')

    def __set_personnel_data(self):
        choice = {'0': ['Add User Face'],
                  '1': ['Delete User Face'],
                  '2': ['Delete All User Face'],
                  '3': ['Query All Face'],
                  '4': ['Back to Main Menu']
                  }
        option = int(self.__select_option(f'PERSONNEL DATA', choice))
        if option == 0:
            self.__add_personnel_data()
        elif option == 1:
            self.__delete_personnel_data()
        elif option == 2:
            self.data = {"mqtt_cmd": 1, "mqtt_operate_id": 7, 'device_token': self.device_token,
                         'device_id': self.device_id, 'tag': "platform define", 'piclib_manage': 1}
        elif option == 3:
            self.__query_personnel_data()
        elif option == 4:
            return

    def __add_personnel_data(self):
        print(f'\n\n[ADD USER FACE]')
        self.data = {"mqtt_cmd": 1, "mqtt_operate_id": 7, 'device_token': self.device_token,
                     'device_id': self.device_id, 'tag': "platform define", 'piclib_manage': 0,
                     'param': {}}
        self.data['param']['lib_name'] = ""
        self.data['param']['lib_id'] = ""
        self.data['param']['server_ip'] = '192.168.1.2'
        self.data['param']['server_port'] = 7777
        self.data['param']['pictures'] = []
        while True:
            command = input('Add user face (Y/N): ')
            if command == 'Y' or command == 'y':
                self.data['param']['pictures'].append({})
                self.data['param']['pictures'][len(self.data['param']['pictures']) - 1][
                    'active_time'] = f"{datetime.strftime(datetime.now(), '%Y')}/01/1 00:00:01"
                with models.get_session() as session:
                    employee = session.query(models.Employee).filter_by(id=int(input('User ID: '))).scalar()
                    self.data['param']['pictures'][len(self.data['param']['pictures']) - 1]['user_id'] = str(employee.id)
                    self.data['param']['pictures'][len(self.data['param']['pictures']) - 1]['user_name'] = employee.name
                    self.data['param']['pictures'][len(self.data['param']['pictures']) - 1][
                        'end_time'] = f"{datetime.strftime(datetime.now(), '%Y')}/12/30 23:59:59"
                    self.data['param']['pictures'][len(self.data['param']['pictures']) - 1]['p_id'] = 'null'
                    self.data['param']['pictures'][len(self.data['param']['pictures']) - 1]['picture'] = employee.face
            elif command == 'N' or command == 'n':
                break

    def __delete_personnel_data(self):
        print(f'\n\n[DELETE USER FACE]')
        self.data = {"mqtt_cmd": 1, "mqtt_operate_id": 7, 'device_token': self.device_token,
                     'device_id': self.device_id, 'tag': "platform define", 'piclib_manage': 3,
                     'param': {'users': []}}
        while True:
            command = input('Add user face (Y/N): ')
            if command == 'Y' or command == 'y':
                self.data['param']['users'].append({})
                self.data['param']['users'][len(self.data['param']['users']) - 1]['user_id'] = input('User ID: ')
            elif command == 'N' or command == 'n':
                break

    def __query_personnel_data(self):
        print(f'\n\n[QUERY ALL FACE]')
        self.data = {"mqtt_cmd": 1, "mqtt_operate_id": 7, 'device_token': self.device_token,
                     'device_id': self.device_id, 'tag': "platform define", 'piclib_manage': 4,
                     'page': int(input('Page (all pages = -1): '))}
