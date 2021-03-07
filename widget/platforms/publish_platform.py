import sys
import os
from datetime import datetime
import time
import json
import paho.mqtt.client as mqtt
import widget.models as models


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

    def set_device(self, device_id, device_token=None):
        self.device_id = device_id
        self.device_token = device_token

    def _publish_data(self):
        self.__client.connect(self.host, self.port)
        self.__client.loop_start()
        self.__client.publish(self.topic, json.dumps(self.data, indent=4))
        # time.sleep(1)
        self.__client.loop_stop()
        self.__client.disconnect()

    def bind_device(self):
        self.data = {"mqtt_cmd": 1,
                     "mqtt_operate_id": 10,
                     'device_id': self.device_id,
                     'tag': "platform define",
                     'bind_ctrl': 1}
        self._publish_data()

    def unbind_device(self):
        self.data = {"mqtt_cmd": 1,
                     "mqtt_operate_id": 10,
                     'device_token': self.device_token,
                     'device_id': self.device_id,
                     'tag': "platform define",
                     'bind_ctrl': 0}
        self._publish_data()

    def add_personnel_data(self, employees_id=list):
        self.data = {"mqtt_cmd": 1,
                     "mqtt_operate_id": 7,
                     'device_token': self.device_token,
                     'device_id': self.device_id,
                     'tag': "platform define",
                     'piclib_manage': 0,
                     'param':
                         {'lib_name': '',
                          'lib_id': '',
                          'server_ip': '192.168.1.2',
                          'server_port': 7777,
                          'pictures': []
                          }
                     }
        for employee_id in employees_id:
            self.data['param']['pictures'].append({})
            index = len(self.data['param']['pictures']) - 1
            self.data['param']['pictures'][index]['active_time'] \
                = f"{datetime.strftime(datetime.now(), '%Y')}/01/1 00:00:01"
            with models.get_session() as session:
                employee = session.query(models.Employee).filter(models.Employee.id == employee_id).scalar()
                self.data['param']['pictures'][index]['user_id'] = str(employee.id)
                self.data['param']['pictures'][index]['user_name'] = employee.name
                self.data['param']['pictures'][index]['end_time'] \
                    = f"{datetime.strftime(datetime.now(), '%Y')}/12/30 23:59:59"
                self.data['param']['pictures'][index]['p_id'] = 'null'
                self.data['param']['pictures'][index]['picture'] = employee.face
        self._publish_data()

    def remove_all_personnel_data(self):
        self.data = {"mqtt_cmd": 1,
                     "mqtt_operate_id": 7,
                     'device_token': self.device_token,
                     'device_id': self.device_id,
                     'tag': "platform define",
                     'piclib_manage': 1
                     }
        self._publish_data()

    def remove_personnel_data(self, employees_id=list):
        self.data = {"mqtt_cmd": 1,
                     "mqtt_operate_id": 7,
                     'device_token': self.device_token,
                     'device_id': self.device_id,
                     'tag': "platform define",
                     'piclib_manage': 3,
                     'param': {'users': [{'user_id': employee_id} for employee_id in employees_id]}
                     }
        self._publish_data()

    def query_personnel_data(self, page=-1):
        self.data = {"mqtt_cmd": 1,
                     "mqtt_operate_id": 7,
                     'device_token': self.device_token,
                     'device_id': self.device_id,
                     'tag': "platform define",
                     'piclib_manage': 4,
                     'page': page
                     }
        self._publish_data()

    def get_device_info(self):
        self.data = {"mqtt_cmd": 2,
                     'device_id': self.device_id,
                     'tag': "platform define",
                     'device_token': self.device_token
                     }
        self._publish_data()

    def _get_answer_device_info(self):
        client = mqtt.Client('SubscribePublishPlatform')
        client.connect(self.host, self.port)
        client.subscribe('PublishTest')
        client.on_message = self._on_message
        client.loop_start()
        while True:
            if self.code_result == -1:
                break
        client.loop_stop()
        client.disconnect()

    def _on_message(self, client, userdata, message):
        self.data = json.loads(message.payload.decode("utf-8"))
        print(self.data)
        self._decode_message()