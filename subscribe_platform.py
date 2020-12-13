import sys
from datetime import datetime
import base64
import json
import paho.mqtt.client as mqtt


class SubscribePlatform:
    def __init__(self, host, port=1883, client_name='PC'):
        self.host = host
        self.port = port
        self.client_name = client_name
        self.topic = 'PublishTest'
        self.device_id = '1'
        self.device_token = '2'
        self.data = {}
        self.params_camera = {}
        self.__client = mqtt.Client(client_name)
        self.code = 0

    def run(self):
        self.__client.connect(self.host, self.port)
        self.__client.subscribe(self.topic)
        self.__client.on_message = self.__on_message
        self.__client.loop_start()
        while True:
            if self.code == -1:
                break
        self.__client.loop_stop()

    def set_device(self, device_id, device_token='1'):
        self.device_id = device_id
        self.device_token = device_token

    def unbind_device(self):
        self.__client.connect(self.host, self.port)
        self.__client.subscribe(self.topic)
        self.__client.on_message = self.__on_unbind_message
        self.__client.loop_start()
        while True:
            if len(self.data) > 0:
                if self.data['code'] == 0:
                    print(f"[INFO] {self.data['msg']}")
                    break
                elif self.data['code'] == -1:
                    print('bad')
        self.__client.loop_stop()

    def __on_unbind_message(self, client, userdata, message):
        self.data = json.loads(message.payload.decode("utf-8"))

    def __on_message(self, client, userdata, message):
        self.data = json.loads(message.payload.decode("utf-8"))
        print(self.data)
        self.__decode_message()

    def __decode_message(self):
        if self.data['code'] == -1:
            self.__store_error()
        elif self.__is_person():
            self.__upload_person()
        elif self.__is_bind():
            self.__write_token()

    def __store_error(self):
        with open('logs/error.log', 'a+') as file:
            file.write(f'\n[{datetime.now()}] {self.data}')

    def __is_person(self):
        if self.data['msg'] == 'Upload Person Info!':
            return True
        else:
            return False

    def __upload_person(self):
        if self.data['datas']['matched'] == '1':
            self.__store_information_employee()
        else:
            self.__store_information_stranger()
        if 'imageFile' in self.data['datas']:
            self.__save_image_person()

    def __store_information_stranger(self):
        with open('logs/strangers.log', 'a+') as file:
            file.write(f"\n[{self.data['datas']['time']}] Temperature: {self.data['datas']['temperature']}")

    def __store_information_employee(self):
        with open('logs/employees.log', 'a+') as file:
            file.write(f"\n[{self.data['datas']['time']}] User ID: {self.data['datas']['user_id']}, "
                       f"Name: {self.data['datas']['name']}, Similar: {self.data['datas']['similar']}, "
                       f"Temperature: {self.data['datas']['temperature']}")

    def __save_image_person(self):
        with open(f"person/{self.data['datas']['name']}"
                  f"_{self.data['datas']['temperature']}.jpg", 'wb') as file:
            file.write(base64.standard_b64decode(self.data['datas']['imageFile'].replace('data:image/jpg;base64,', '')))

    def __is_bind(self):
        if self.data['msg'] == 'mqtt bind ctrl success':
            return True
        else:
            return False

    def __write_token(self):
        with open('token.txt', 'w') as file:
            file.write(self.data['datas']['device_token'])