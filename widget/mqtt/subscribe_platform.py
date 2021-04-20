import os
from datetime import datetime
import base64
import json
import paho.mqtt.client as mqtt
from PyQt5 import QtCore

from widget.management import DBManagement
import widget.models as models


class SubscribePlatform(QtCore.QObject):
    statistic = QtCore.pyqtSignal(object)
    device = QtCore.pyqtSignal(dict)
    token = QtCore.pyqtSignal(str)
    profiles = QtCore.pyqtSignal(object)

    running = False
    _host = None
    _port = 1883
    device_id = None
    device_token = None
    topic = 'PublishTest'
    client_name = 'SP'
    _client = mqtt.Client(client_name)
    code_result = 0
    _data = dict
    _prev_statistic = models.Statistic('-1', '2021/01/01 00:00:00', '37.5', '0.0')
    _prev_statistic.time = datetime.now()
    _database_management = DBManagement()

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
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if isinstance(value, dict):
            self._data = value

    def set_host_port(self, host: str, port: int = 1883, client_name: str = 'SP'):
        self.host = host
        self.port = port
        self.client_name = client_name
        self._client = mqtt.Client(client_name)

    def set_device(self, device_id: str, device_token: str = None):
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
        self.define_message()

    def define_message(self):
        if self.data['code'] == -1:
            self.log('error.log',
                     f'[{datetime.now()}][{self.data["device_id"]}] {self.data["tag"]}: {self.data["msg"]}\n')
        else:
            if self.data['tag'] == 'UploadPersonInfo':
                self.record_person_information()
            elif self.data['tag'] == 'query_profiles':
                self.profiles.emit(self.data['datas'])
            elif self.data['tag'] == 'bind_control':
                if 'device_token' in self.data['datas']:
                    self.token.emit(f"{self.data['device_id']}_{self.data['datas']['device_token']}")
            elif self.data['tag'] == 'device_info':
                self.device.emit(self.data)

    def record_person_information(self):
        if self.data['datas']['matched'] == '1':
            self.record_profile_information()
        elif self.data['datas']['matched'] == '0':
            self.record_stranger_information()

    def record_profile_information(self):
        statistic = models.Statistic(
            identifier=self.data['datas']['user_id'],
            time=self.data['datas']['time'],
            temperature=self.data['datas']['temperature'],
            similar=self.data['datas']['similar'],
            mask=self.is_mask_on()
        )
        if not self.is_duplicate_statistic(statistic):
            if 'imageFile' in self.data['datas']:
                face = self.record_face_person()
                statistic.face = face
            self._database_management.add_statistics(statistic)
            self.statistic.emit(statistic)
            self._prev_statistic = statistic

    def record_stranger_information(self):
        face = None
        if 'imageFile' in self.data['datas']:
            face = self.record_face_person()
        statistic = models.StrangerStatistic(
            time=self.data['datas']['time'],
            temperature=self.data['datas']['temperature'],
            mask=self.is_mask_on(),
            face=face
        )
        self._database_management.add_stranger_statistics(statistic)

    def record_face_person(self):
        snapshot_path = os.path.abspath('snapshot')
        file_path = f"{snapshot_path}/{self.data['datas']['time'].split(' ')[0]}"
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        filename = f"{file_path}/{self.data['datas']['time'].replace(':', '-')}" \
                   f"_{self.data['datas']['name']}" \
                   f"_{self.data['datas']['temperature']}.jpg"
        with open(filename, 'wb') as file:
            file.write(base64.standard_b64decode(self.data['datas']['imageFile'].replace('data:image/jpg;base64,', '')))
        return filename.replace(snapshot_path, '')

    def log(self, filename: str, information: str):
        dir_path = os.path.abspath('logs')
        with open(f'{dir_path}/{filename}', 'a+') as file:
            file.write(information)

    def is_mask_on(self):
        if self.data['datas']['mask'] == 1:
            mask = 'true'
        elif self.data['datas']['mask_excep'] == 0:
            mask = 'false'
        else:
            mask = 'unknow'
        return mask

    def is_duplicate_statistic(self, statistic: models.Statistic):
        if isinstance(self._prev_statistic.time, datetime):
            prev_time = self._prev_statistic.time
        else:
            prev_time = datetime.strptime(self._prev_statistic.time, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.strptime(statistic.time, '%Y-%m-%d %H:%M:%S')
        time_difference = (abs(current_time - prev_time)).total_seconds()
        if self._prev_statistic.id_profile == statistic.id_profile and 0 < time_difference <= 60:
            return True
        return False
