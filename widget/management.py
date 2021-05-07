import os
import re
import json
import socket
import requests
from datetime import datetime
import zipfile
from typing import Union
import pandas as pd
from sqlalchemy import func, or_
from sqlalchemy.orm import load_only

import widget.models as models


class DBManagement:
    def __init__(self):
        self._number_profile_passages = int
        self._number_stranger_passages = int
        self._number_normal_temperature_profile_passages = int
        self._number_normal_temperature_stranger_passages = int
        self._profile_name = str
        self._pattern = None
        self._devices = models.Device
        self._departments = models.Department
        self._profiles = models.Profile
        self._statistics = models.Statistic
        self._stranger_statistics = models.StrangerStatistic

    # DEVICES
    def get_devices(self):
        with models.get_session() as session:
            self._devices = session.query(models.Device) \
                .all()
            return self._devices

    def add_devices(self, *devices: models.Device):
        with models.get_session() as session:
            session.add_all(devices)
        self._devices = devices

    def update_device(self, identifier: str, new_device: Union[models.Device, dict]):
        with models.get_session() as session:
            if isinstance(new_device, models.Device):
                session.query(models.Device) \
                    .filter(models.Device.id == identifier) \
                    .update(
                    {
                        models.Device.id: new_device.id,
                        models.Device.name: new_device.name,
                        models.Device.model: new_device.model,
                        models.Device.mac_address: new_device.mac_address,
                        models.Device.ip_address: new_device.ip_address,
                        models.Device.version: new_device.version,
                        models.Device.token: new_device.token
                    }
                )
            elif isinstance(new_device, dict):
                session.query(models.Device) \
                    .filter(models.Device.id == identifier) \
                    .update(new_device)
        self._devices = new_device

    def remove_devices(self, *identifiers: str):
        with models.get_session() as session:
            session.query(models.Device) \
                .filter(models.Device.id.in_(identifiers)) \
                .delete(synchronize_session=False)
        self._devices = None

    # GENDERS
    @staticmethod
    def get_genders():
        with models.get_session() as session:
            genders = session.query(models.Gender).all()
            return genders

    @staticmethod
    def get_gender(identifier: int):
        with models.get_session() as session:
            genders = session.query(models.Gender).filter(models.Gender.id == identifier).scalar()
            return genders

    # DEPARTMENTS
    def get_departments(self, *identifiers: int):
        with models.get_session() as session:
            query = session.query(models.Department)
            if identifiers:
                query = query.filter(models.Department.id.in_(identifiers))
            self._departments = query.all()
            return self._departments

    def get_department_by_name(self, name: str):
        with models.get_session() as session:
            self._departments = session.query(models.Department) \
                .filter(models.Department.name == name) \
                .scalar()
            return self._departments

    def get_department(self, identifier: int):
        with models.get_session() as session:
            self._departments = session.query(models.Department) \
                .filter(models.Department.id == identifier) \
                .scalar()
            return self._departments

    def add_departments(self, *departments: models.Department):
        with models.get_session() as session:
            session.add_all(departments)
        self._departments = departments

    def update_department(self, identifier, new_department: models.Department):
        with models.get_session() as session:
            session.query(models.Department) \
                .filter(models.Department.id == identifier) \
                .update(
                {
                    models.Department.id: new_department.id,
                    models.Department.name: new_department.name,
                    models.Department.location: new_department.location
                }
            )
        self._departments = None

    def remove_departments(self, *identifiers: int):
        with models.get_session() as session:
            session.query(models.Department) \
                .filter(models.Department.id.in_(identifiers)) \
                .delete(synchronize_session=False)
        self._departments = None

    @staticmethod
    def reset_department_autoincrement():
        with models.get_session() as session:
            session.execute('ALTER TABLE thermalcamera.departments AUTO_INCREMENT = 1;')

    # PROFILES
    def is_id_profile_duplicate(self, identifier: int):
        with models.get_session() as session:
            profile = session.query(models.Profile) \
                .filter(models.Profile.id == identifier) \
                .first()
        if profile:
            self._profiles = profile
            return True
        return False

    def is_personnel_number_duplicate(self, personnel_number: str):
        with models.get_session() as session:
            profile = session.query(models.Profile) \
                .filter(models.Profile.personnel_number == personnel_number) \
                .first()
            if profile:
                self._profiles = profile
                return True
        return False

    def is_passport_duplicate(self, passport: str):
        with models.get_session() as session:
            profile = session.query(models.Profile) \
                .filter(models.Profile.passport == passport) \
                .first()
            if profile:
                self._profiles = profile
                return True
        return False

    def get_profile_name(self, identifier: int):
        with models.get_session() as session:
            profile_name = session.query(models.Profile.name) \
                .filter(models.Profile.id == identifier) \
                .scalar()
        self._profile_name = profile_name
        return profile_name

    def get_profile(self, **kwargs):
        with models.get_session() as session:
            for key, value in kwargs.items():
                if key == 'identifier':
                    query = session.query(models.Profile).filter(models.Profile.id == value)
                elif key == 'personnel_number':
                    query = session.query(models.Profile).filter(models.Profile.personnel_number == value)
                elif key == 'passport':
                    query = session.query(models.Profile).filter(models.Profile.passport == value)
                elif key == 'name':
                    query = session.query(models.Profile).filter(models.Profile.name == value)
        self._profiles = query.scalar()
        return self._profiles

    def get_profiles(self, *identifiers: int):
        with models.get_session() as session:
            query = session.query(models.Profile)
            if identifiers:
                query = query.filter(models.Profile.id.in_(identifiers))
            self._profiles = query.order_by(func.abs(models.Profile.id)).all()
        return self._profiles

    def create_profiles_pattern(self, filename):
        data = [['xxx', 'Ivanov Ivan', '', False, 'No Group', 'male', ''],
                ['', 'Ivanov Ilia', 'AB12332', True, '', '', 'Some text']]
        self._pattern = pd.DataFrame(
            data=data,
            columns=['Personnel Number', 'Name', 'Passport', 'Visitor', 'Department', 'Gender', 'Information']
        )
        self._pattern.to_csv(filename, sep=';', index=False)

    def import_profiles_data(self, filename):
        self._pattern = pd.read_csv(filename, sep=';')
        self._pattern = self._pattern.where(pd.notnull(self._pattern), None)
        profiles = [
            models.Profile(
                identifier=row['ID'],
                name=row['Name'],
                name_department=row['Department'],
                gender=row['Gender'],
                phone_number=row['Phone Number']
            )
            for index, row in self._pattern.iterrows()
        ]
        profiles = set(profiles)
        identifiers = [identifier for index, identifier in enumerate(self._pattern['ID'])]
        current_profiles = set(self.get_profiles(*identifiers))
        insert_profiles = list(profiles - current_profiles)
        # update_profiles = list(profiles & current_profiles)
        update_profiles = []
        for current_profile in current_profiles:
            for profile in profiles:
                if current_profile == profile:
                    update_profiles.append(profile.to_dict())
        self.add_profiles(*insert_profiles)
        for profile in update_profiles:
            if 'face' in profile:
                del profile['face']
            self.update_profile(profile['id'], profile)

    def import_photos(self, filename):
        if zipfile.is_zipfile(filename):
            file = zipfile.ZipFile(filename)
            application_path = f'{os.path.dirname(os.path.abspath(__file__))}/nginx/html/static/images'
            identifiers = []
            profiles = []
            for name in file.namelist():
                file.extract(name, application_path)
                data = name.split(sep='_')
                identifiers.append(data[0])
                profiles.append(
                    models.Profile(
                        identifier=data[0],
                        name=data[1].replace('.jpg', ''),
                        face=f'/static/images/{name}'
                    )
                )
            profiles = set(profiles)
            current_profiles = set(self.get_profiles(*identifiers))
            insert_profiles = list(profiles - current_profiles)
            update_profiles = list(current_profiles & profiles)
            self.add_profiles(*insert_profiles)
            for profile in update_profiles:
                values = profile.to_dict()
                self.update_profile(profile.id, values)

    def export_profiles_data(self):
        pass

    def add_profiles(self, *profiles: models.Profile):
        with models.get_session() as session:
            session.add_all(profiles)
        self._profiles = profiles

    def update_profile(self, identifier: int, new_profile: Union[models.Profile, dict]):
        with models.get_session() as session:
            if isinstance(new_profile, models.Profile):
                session.query(models.Profile) \
                    .filter(models.Profile.id == identifier) \
                    .update(
                    {
                        models.Profile.id: new_profile.id,
                        models.Profile.personnel_number: new_profile.personnel_number,
                        models.Profile.name: new_profile.name,
                        models.Profile.passport: new_profile.passport,
                        models.Profile.visitor: new_profile.visitor,
                        models.Profile.face: new_profile.face,
                        models.Profile.id_department: new_profile.id_department,
                        models.Profile.gender: new_profile.gender,
                        models.Profile.information: new_profile.information
                    }
                )
            elif isinstance(new_profile, dict):
                session.query(models.Profile) \
                    .filter(models.Profile.id == identifier) \
                    .update(new_profile)
        self._profiles = new_profile

    def remove_profiles(self, *identifiers: int):
        profiles = self.get_profiles(identifiers)
        path = os.path.dirname(os.path.abspath(__file__))
        for profile in profiles:
            if os.path.exists(f'{path}\\nginx\\html{profile.face}'):
                os.remove(f'{path}\\nginx\\html{profile.face}')
        with models.get_session() as session:
            session.query(models.Profile) \
                .filter(models.Profile.id.in_(identifiers)) \
                .delete(synchronize_session=False)
        self._profiles = None

    @staticmethod
    def reset_profile_autoincrement():
        with models.get_session() as session:
            session.execute('ALTER TABLE thermalcamera.profiles AUTO_INCREMENT = 1;')

    # STATISTICS
    def get_statistics(self,
                       low: Union[str, float] = None,
                       high: Union[str, float] = None,
                       identifiers: list = None,
                       profile_name: bool = False):
        with models.get_session() as session:
            if profile_name:
                query = session.query(models.Statistic, models.Profile.name) \
                    .join(models.Profile,
                          models.Profile.id == models.Statistic.id_profile,
                          isouter=True)
            else:
                query = session.query(models.Statistic)
            if isinstance(low, str) and isinstance(high, str):
                query = query.filter(models.Statistic.time >= low,
                                     models.Statistic.time <= high)
            elif isinstance(low, float) and isinstance(high, float):
                query = query.filter(models.Statistic.temperature >= low,
                                     models.Statistic.temperature <= high)
            if identifiers:
                query = query.filter(models.Statistic.id_profile.in_(identifiers))
            self._statistics = query.order_by(func.abs(models.Statistic.id_profile)).all()
        return self._statistics

    def add_statistics(self, *statistics: models.Statistic):
        with models.get_session() as session:
            session.add_all(statistics)
        self._statistics = statistics

    def get_number_statistics(self,
                              low: Union[str, float] = None,
                              high: Union[str, float] = None,
                              identifiers: list = None):
        with models.get_session() as session:
            query = session.query(models.Statistic)
            if isinstance(low, str) and isinstance(high, str):
                query = query.filter(models.Statistic.time >= low,
                                     models.Statistic.time <= high)
            elif isinstance(low, float) and isinstance(high, float):
                query = query.filter(models.Statistic.temperature >= low,
                                     models.Statistic.temperature <= high)
            if identifiers:
                query = query.filter(models.Statistic.id_profile.in_(identifiers))
            self._number_profile_passages = query.count()
        return self._number_profile_passages

    def get_number_normal_temperature_statistics(self,
                                                 threshold: float,
                                                 low: str = None,
                                                 high: str = None,
                                                 identifiers: list = None
                                                 ):
        with models.get_session() as session:
            query = session.query(models.Statistic)
            if isinstance(low, str) and isinstance(high, str):
                query = query.filter(models.Statistic.time >= low,
                                     models.Statistic.time <= high)
            if identifiers:
                query = query.filter(models.Statistic.id_profile.in_(identifiers))
            self._number_normal_temperature_profile_passages = query.filter(models.Statistic.temperature <= threshold) \
                .count()
        return self._number_normal_temperature_profile_passages

    def remove_statistics(self, *times: tuple):
        """
        :param times: tuple[identifier, datetime]
        :return: None
        """
        with models.get_session() as session:
            for time in times:
                session.query(models.Statistic) \
                    .filter(models.Statistic.time == time[1],
                            models.Statistic.id_profile == time[0]
                            ) \
                    .delete(synchronize_session=False)
        self._statistics = None

    def remove_statistic_duplicates(self):
        statistics = self.get_statistics()
        removable_statistics = set()
        for row_position, comparable_statistic in enumerate(statistics):
            for statistic in statistics[row_position:]:
                if comparable_statistic.id_profile == statistic.id_profile:
                    time_difference = (abs(statistic.time - comparable_statistic.time)).total_seconds()
                    if 0 < time_difference <= 60:
                        removable_statistics.add((statistic.id_profile, str(statistic.time)))
        self.remove_statistics(*list(removable_statistics))

    def create_temperatures_report(self, filename: str,
                                   identifiers: list = None,
                                   low: Union[str, float] = None,
                                   high: Union[str, float] = None):
        file_format = filename.split('.')[-1]
        if file_format == 'json':
            self.create_report_temperatures_json(filename, identifiers, low, high)
        elif file_format == 'csv':
            self.create_report_temperatures_csv(filename, identifiers, low, high)

    def create_passage_report(self, filename: str, identifiers: list = None, low: str = None, high: str = None):
        file_format = filename.split('.')[-1]
        if file_format == 'json':
            self.create_passage_report_json(filename, identifiers, low, high)
        elif file_format == 'csv':
            self.create_passage_report_csv(filename, identifiers, low, high)

    def create_passage_report_json(self, filename: str = None,
                                   identifiers: list = None,
                                   low: str = None,
                                   high: str = None):
        report = {}
        number_statistic = 0
        for statistic in self.get_statistics(identifiers=identifiers, low=low, high=high):
            name = self.get_profile_name(statistic.id_profile)
            statistic_datetime = str(statistic.time).split(' ')
            if name in report:
                if statistic_datetime[0] in report[name]:
                    if number_statistic % 2 == 1:
                        report[name][statistic_datetime[0]][int(number_statistic / 2)]['gone'] = statistic_datetime[1]
                    else:
                        report[name][statistic_datetime[0]].append(
                            {
                                'came': statistic_datetime[1],
                                'gone': statistic_datetime[1]
                            }
                        )
                    number_statistic += 1
                else:
                    number_statistic = 1
                    report[name][statistic_datetime[0]] = [
                        {
                            'came': statistic_datetime[1],
                            'gone': statistic_datetime[1]
                        }
                    ]
            else:
                number_statistic = 1
                report[name] = {
                    statistic_datetime[0]: [
                        {
                            'came': statistic_datetime[1],
                            'gone': statistic_datetime[1]
                        }
                    ]
                }
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(report, file, ensure_ascii=False, indent=4)

    def create_passage_report_csv(self, filename: str,
                                  identifiers: list = None,
                                  low: str = None,
                                  high: str = None):
        report = pd.DataFrame(columns=['Name', 'Date', 'Came', 'Gone'])
        number_statistic = 0
        for statistic in self.get_statistics(identifiers=identifiers, low=low, high=high):
            statistic_datetime = str(statistic.time).split(' ')
            name = self.get_profile_name(statistic.id_profile)
            if number_statistic % 2 == 0:
                row = {
                    'Name': name,
                    'Date': statistic_datetime[0],
                    'Came': statistic_datetime[1],
                    'Gone': statistic_datetime[1]
                }
                report = report.append(row, ignore_index=True)
                number_statistic += 1
            elif row['Name'] == name and row['Date'] == statistic_datetime[0]:
                report.iloc[-1]['Gone'] = statistic_datetime[1]
                number_statistic = 0
            else:
                row = {
                    'Name': name,
                    'Date': statistic_datetime[0],
                    'Came': statistic_datetime[1],
                    'Gone': statistic_datetime[1]
                }
                report = report.append(row, ignore_index=True)
                number_statistic += 1
        report.to_csv(filename, sep=';', header=True, encoding='cp1251')

    def create_report_temperatures_json(self, filename: str,
                                        identifiers: list = None,
                                        low: Union[str, float] = None,
                                        high: Union[str, float] = None):
        report = {}
        for statistic in self.get_statistics(low=low, high=high, identifiers=identifiers):
            name = self.get_profile_name(statistic.id_profile)
            statistic_datetime = str(statistic.time).split(' ')
            if name in report:
                if statistic_datetime[0] in report[name]:
                    report[name][statistic_datetime[0]][statistic_datetime[1]] = float(statistic.temperature)
                else:
                    report[name][statistic_datetime[0]] = {
                        statistic_datetime[1]: float(statistic.temperature)
                    }
            else:
                report[name] = {
                    statistic_datetime[0]: {
                        statistic_datetime[1]: float(statistic.temperature)
                    }
                }
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(report, file, ensure_ascii=False, indent=4)

    def create_report_temperatures_csv(self, filename: str,
                                       identifiers: list = None,
                                       low: Union[str, float] = None,
                                       high: Union[str, float] = None):
        report = pd.DataFrame(columns=['Name', 'Date', 'Time', 'Temperature'])
        for statistic in self.get_statistics(identifiers=identifiers, low=low, high=high):
            statistic_datetime = str(statistic.time).split(' ')
            report = report.append({
                'Name': self.get_profile_name(statistic.id_profile),
                'Date': statistic_datetime[0],
                'Time': statistic_datetime[1],
                'Temperature': float(statistic.temperature)
            }, ignore_index=True)
        report.to_csv(filename, sep=';', header=True, encoding='cp1251')

    # STRANGER STATISTICS
    def get_stranger_statistics(self, low: Union[str, float] = None, high: Union[str, float] = None):
        with models.get_session() as session:
            query = session.query(models.StrangerStatistic)
            if isinstance(low, str) and isinstance(high, str):
                query = query.filter(models.StrangerStatistic.time >= low,
                                     models.StrangerStatistic.time <= high)
            elif isinstance(low, float) and isinstance(high, float):
                query = query.filter(models.StrangerStatistic.temperature >= low,
                                     models.StrangerStatistic.temperature <= high)
            self._stranger_statistics = query.all()
        return self._stranger_statistics

    def get_number_stranger_statistics(self, low: Union[str, float] = None, high: Union[str, float] = None):
        with models.get_session() as session:
            query = session.query(models.StrangerStatistic)
            if isinstance(low, str) and isinstance(high, str):
                query = query.filter(models.StrangerStatistic.time >= low,
                                     models.StrangerStatistic.time <= high)
            elif isinstance(low, float) and isinstance(high, float):
                query = query.filter(models.StrangerStatistic.temperature >= low,
                                     models.StrangerStatistic.temperature <= high)
            self._number_stranger_passages = query.count()
        return self._number_stranger_passages

    def get_number_normal_temperature_stranger_statistics(self,
                                                          threshold: float,
                                                          low: str = None,
                                                          high: str = None):
        with models.get_session() as session:
            query = session.query(models.StrangerStatistic)
            if isinstance(low, str) and isinstance(high, str):
                query = query.filter(models.StrangerStatistic.time >= low,
                                     models.StrangerStatistic.time <= high)
            self._number_normal_temperature_stranger_passages = query \
                .filter(models.StrangerStatistic.temperature <= threshold) \
                .count()
        return self._number_normal_temperature_stranger_passages

    def add_stranger_statistics(self, *statistics: models.StrangerStatistic):
        with models.get_session() as session:
            session.add_all(statistics)
        self._stranger_statistics = statistics

    def remove_stranger_statistics(self, *times: str):
        with models.get_session() as session:
            session.query(models.StrangerStatistic) \
                .filter(models.StrangerStatistic.time.in_(times)) \
                .delete(synchronize_session=False)
        self._stranger_statistics = None


class DeviceManagement:
    def __init__(self):
        self._filepath = os.path.dirname(os.path.abspath(__file__))
        self._devices = []
        self._host_name = None
        self._host = None
        self._subnet = None
        self._port = None

    @property
    def host_name(self):
        return self._host_name

    @host_name.setter
    def host_name(self, value):
        self._host_name = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def subnet(self):
        return self._subnet

    @subnet.setter
    def subnet(self, value):
        self._subnet = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, value):
        self._devices = value

    def add_device(self, device: models.Device):
        self.devices.append(device)

    def remove_device(self, device: models.Device):
        self.devices.remove(device)

    def find_devices(self, binding_devices: list = None):
        os.popen('chcp 437')
        with os.popen(f'arp -a -N {self.host}') as file:
            data = file.read()
        interface = re.search('0x[a-f0-9]+', data).group()
        interface = socket.if_indextoname(int(interface, 16)).split('_')[0]
        if interface == 'ethernet':
            for device in re.findall('([-.0-9]+)\s+([-0-9a-f]{17})\s+(\w+)', data):
                if 'dynamic' in device and self.subnet == device[0][:self.host.rfind('.')]:
                    mac_address = device[1].upper()
                    if binding_devices is None or mac_address not in binding_devices:
                        self.get_info(device_ip=device[0])
            return 0
        else:
            return -1

    def get_info(self, device_ip: str):
        try:
            request = requests.get(f'http://{device_ip}:7080/ini.htm',
                                   headers={'Authorization': 'Basic YWRtaW46MTIzNDU='})
            if request.status_code == 200:
                print(request.text)
                for information in request.text.split('<br>'):
                    information = information.split('=')
                    if information[0] == 'getdeviceserial':
                        identifier = information[1]
                    elif information[0] == 'getdevname':
                        name = information[1]
                    elif information[0] == 'getdevicetype':
                        model = information[1]
                    elif information[0] == 'getsoftwareversion':
                        version = information[1]
                    elif information[0] == 'mac':
                        mac_address = information[1].replace(':', '-')
                    elif information[0] == 'netip':
                        ip_address = information[1]
                device = models.Device(
                    identifier=identifier,
                    name=name,
                    model=model,
                    firmware_version=version,
                    mac_address=mac_address,
                    ip_address=ip_address
                )
                self.add_device(device)
        except requests.exceptions.ConnectionError as e:
            pass

    def find_host_info(self):
        self.host_name = socket.gethostname()
        self.host = socket.gethostbyname(self.host_name)
        self.subnet = self.host[:self.host.rfind('.')]
