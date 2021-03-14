import sys
import os
from datetime import datetime, date
import base64
import json
import paho.mqtt.client as mqtt
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor

import widget.models as models


class SubscribePlatform(QtCore.QObject):
    statistic = QtCore.pyqtSignal(object)
    device = QtCore.pyqtSignal(dict)
    running = False

    def set_host_port(self, host, port=1883, client_name='PC'):
        self.host = host
        self.port = port
        self.client_name = client_name
        self.topic = 'PublishTest'
        self.device_id = '1'
        self.device_token = '2'
        self.data = {}
        self.params_camera = {}
        self._client = mqtt.Client(client_name)
        self.code_result = 0

    def set_device(self, device_id, device_token=None):
        self.device_id = device_id
        self.device_token = device_token

    def run(self):
        self._client.connect(self.host, self.port)
        self._client.subscribe(self.topic)
        self._client.on_message = self._on_message
        self._client.loop_start()
        while True:
            if self.code_result == -1:
                break
        self._client.loop_stop()

    def _on_message(self, client, userdata, message):
        self.data = json.loads(message.payload.decode("utf-8"))
        print(self.data)
        self._decode_message()

    def _decode_message(self):
        if self.data['code'] == -1:
            self._store_error()
        elif self._is_person():
            self._upload_person()
        elif self._is_bind():
            self._write_token()
        elif self._is_param_device():
            self.device.emit(self.data)

    def _store_error(self):
        with open('logs/error.log', 'a+') as file:
            file.write(f'\n[{datetime.now()}] {self.data}')

    def _is_person(self):
        if self.data['msg'] == 'Upload Person Info!':
            return True
        else:
            return False

    def _upload_person(self):
        if self.data['datas']['matched'] == '1':
            self._store_information_employee()
        else:
            self._store_information_stranger()
        if 'imageFile' in self.data['datas']:
            self._save_image_person()

    def _store_information_stranger(self):
        with open('logs/strangers.log', 'a+') as file:
            file.write(f"\n[{self.data['datas']['time']}] Temperature: {self.data['datas']['temperature']}")

    def _store_information_employee(self):
        with open('logs/employees.log', 'a+') as file:
            file.write(f"\n[{self.data['datas']['time']}] User ID: {self.data['datas']['user_id']}, "
                       f"Name: {self.data['datas']['name']}, Similar: {self.data['datas']['similar']}, "
                       f"Temperature: {self.data['datas']['temperature']}")
        with models.get_session() as session:
            if self.data['datas']['mask'] == 1:
                mask = 'true'
            elif self.data['datas']['mask_excep'] == 0:
                mask = 'false'
            else:
                mask = 'unknow'
            statistic = models.Statistic(identifier=int(self.data['datas']['user_id']),
                                         time=self.data['datas']['time'],
                                         temperature=float(self.data['datas']['temperature']),
                                         similar=float(self.data['datas']['similar']),
                                         mask=mask)
            self.statistic.emit(statistic)
            session.add(statistic)

    def _save_image_person(self):
        if not os.path.exists(f'snapsnot/{date.today()}'):
            os.mkdir(f'snapsnot/{date.today()}')
        with open(f"snapsnot/{date.today()}/{self.data['datas']['time'].replace(':', '-')}_{self.data['datas']['name']}"
                  f"_{self.data['datas']['temperature']}.jpg", 'wb') as file:
            file.write(base64.standard_b64decode(self.data['datas']['imageFile'].replace('data:image/jpg;base64,', '')))

    def _is_bind(self):
        if self.data['msg'] == 'mqtt bind ctrl success':
            return True
        else:
            return False

    def _write_token(self):
        with open('token.txt', 'w') as file:
            file.write(self.data['datas']['device_token'])

    def _is_param_device(self):
        if self.data['msg'] == 'get param success':
            return True
        else:
            return False
