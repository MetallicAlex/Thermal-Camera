import os
import re
import json
import socket
import smtplib, ssl
import requests
import zipfile
import numpy as np
from typing import Union
import pandas as pd

from widget.setting import Setting
import widget.models as models


class DBManagement:
    def __init__(self):
        self._setting = None
        self._number_profile_passages = int
        self._number_stranger_passages = int
        self._number_normal_temperature_profile_passages = int
        self._number_normal_temperature_stranger_passages = int
        self._profile_name = str
        self._pattern = None
        self._devices = models.Device
        self._device_id = None
        self._device_serial_number = None
        self._departments = models.Department
        self._profiles = models.Profile
        self._statistics = models.Statistic

    @property
    def setting(self):
        return self._setting

    @setting.setter
    def setting(self, value):
        if isinstance(value, Setting):
            self._setting = value

    # SMTP CONFIG
    @staticmethod
    def get_smtp_config(self, sender: str):
        with models.get_session() as session:
            config = session.query(models.SMTPConfig).filter(models.SMTPConfig.default_sender).scalar()
        return config

    # DEVICES
    def get_devices(self):
        with models.get_session() as session:
            self._devices = session.query(models.Device) \
                .all()
            return self._devices

    def get_device_id(self, serial_number: str):
        with models.get_session() as session:
            self._device_id = session.query(models.Device.id) \
                .filter(models.Device.serial_number == serial_number) \
                .scalar()
        return self._device_id

    def get_device_serial_number(self, identifier: int):
        with models.get_session() as session:
            self._device_serial_number = session.query(models.Device.serial_number) \
                .filter(models.Device.id == identifier) \
                .scalar()
        return self._device_serial_number

    def add_devices(self, *devices: models.Device):
        with models.get_session() as session:
            session.add_all(devices)
        self._devices = devices

    def update_device(self, identifier: int, new_device: Union[models.Device, dict]):
        with models.get_session() as session:
            if isinstance(new_device, models.Device):
                session.query(models.Device) \
                    .filter(models.Device.id == identifier) \
                    .update(
                    {
                        models.Device.serial_number: new_device.serial_number,
                        models.Device.name: new_device.name,
                        models.Device.model: new_device.model,
                        models.Device.mac_address: new_device.mac_address,
                        models.Device.ip_address: new_device.ip_address,
                        models.Device.firmware_version: new_device.firmware_version,
                        models.Device.token: new_device.token
                    }
                )
            elif isinstance(new_device, dict):
                session.query(models.Device) \
                    .filter(models.Device.id == identifier) \
                    .update(new_device)
        self._devices = new_device

    def remove_devices(self, *identifiers: int):
        with models.get_session() as session:
            session.query(models.Device) \
                .filter(models.Device.id.in_(identifiers)) \
                .delete(synchronize_session=False)
        self._devices = None

    # MASKS
    @staticmethod
    def get_masks():
        with models.get_session() as session:
            masks = session.query(models.Mask).all()
            return masks

    @staticmethod
    def get_mask(identifier: int):
        with models.get_session() as session:
            mask = session.query(models.Mask).filter(models.Mask.id == identifier).scalar()
            return mask

    # GENDERS
    @staticmethod
    def get_genders():
        with models.get_session() as session:
            genders = session.query(models.Gender).all()
            return genders

    @staticmethod
    def get_gender(identifier: Union[int, str]):
        with models.get_session() as session:
            if isinstance(identifier, int):
                query = session.query(models.Gender).filter(models.Gender.id == identifier)
            elif isinstance(identifier, str):
                query = session.query(models.Gender).filter(models.Gender.value == identifier)
            gender = query.scalar()
            return gender

    # DEPARTMENTS
    def is_department_duplicate(self, department: Union[models.Department, str]):
        with models.get_session() as session:
            query = session.query(models.Department)
            if isinstance(department, models.Department):
                query = query.filter(models.Department.name == department.name)
            else:
                query = query.filter(models.Department.name == department)
            self._departments = query.first()
            if self._departments:
                return True
        return False

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

    def get_profiles_by_department(self, department: int):
        with models.get_session() as session:
            query = session.query(models.Profile).filter(models.Profile.id_department == department)
        self._profiles = query.all()
        return self._profiles

    def get_profiles(self, *identifiers: int):
        with models.get_session() as session:
            query = session.query(models.Profile)
            if identifiers:
                query = query.filter(models.Profile.id.in_(identifiers))
            self._profiles = query.all()
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
        self._pattern = pd.read_csv(filename, sep=';', encoding='1251')
        self._pattern = self._pattern.where(pd.notnull(self._pattern), None)
        profiles = []
        for index, row in self._pattern.iterrows():
            profile = None
            if row['Visitor']:
                if row['Passport'] is None:
                    continue
                else:
                    profile = self.get_profile(passport=row['Passport'])
            else:
                if row['Personnel Number'] is None:
                    continue
                else:
                    profile = self.get_profile(personnel_number=row['Personnel Number'])
            if profile:
                is_new_profile = False
            else:
                is_new_profile = True
                profile = models.Profile()
            if row['Personnel Number']:
                profile.personnel_number = row['Personnel Number']
            if row['Name']:
                profile.name = row['Name']
            if row['Passport']:
                profile.passport = row['Passport']
            profile.visitor = row['Visitor']
            if row['Department']:
                department = self.get_department_by_name(row['Department'])
                if department is None:
                    department = models.Department(name=row['Department'])
                    self.add_departments(department)
                profile.id_department = department.id
            if row['Gender']:
                profile.gender = self.get_gender(row['Gender']).id
            if row['Information']:
                profile.information = row['Information']
            if not is_new_profile:
                self.update_profile(profile.id, profile)
            else:
                profiles.append(profile)
        if len(profiles) > 0:
            self.add_profiles(*profiles)

    def import_photos(self, filename):
        if zipfile.is_zipfile(filename):
            file_zip = zipfile.ZipFile(filename)
            # application_path = f'{self.setting.paths["nginx"]}/html/static/images'
            application_path = f'{os.path.dirname(os.path.abspath(__file__))}/nginx/html/static/images'
            profiles = []
            for file in file_zip.infolist():
                name = file.filename
                if file.flag_bits & 0x800:
                    name = name.decode('utf-8')
                else:
                    name = name.encode('cp437').decode('cp866')
                profile = None
                file_zip.extract(file.filename, application_path)
                data = name.split(sep='_')
                if data[2][0] == '0':
                    profile = self.get_profile(personnel_number=data[0])
                elif data[2][0] == '1':
                    profile = self.get_profile(passport=data[0])
                if profile:
                    if data[1] != '':
                        profile.name = data[1]
                    rng = np.random.default_rng()
                    if profile.face is None:
                        image = np.array2string(rng.integers(10, size=16), separator='')[1:-1] + '.jpg'
                        while os.path.exists(f'{application_path}/{image}'):
                            image = np.array2string(rng.integers(10, size=16), separator='')[1:-1] + '.jpg'
                    else:
                        image = profile.face.split('/')[-1]
                        os.remove(f'{application_path}/{image}')
                    os.rename(f'{application_path}/{file.filename}', f'{application_path}/{image}')
                    profile.face = f'/static/images/{image}'
                    self.update_profile(profile.id, profile)
                else:
                    profile = models.Profile()
                    if data[1] != '':
                        profile.name = data[1]
                    if data[2][0] == '0':
                        profile.visitor = False
                        profile.personnel_number = data[0]
                    else:
                        profile.visitor = True
                        profile.passport = data[0]
                    rng = np.random.default_rng()
                    image = np.array2string(rng.integers(10, size=16), separator='')[1:-1] + '.jpg'
                    while os.path.exists(f'{application_path}/{image}'):
                        image = np.array2string(rng.integers(10, size=16), separator='')[1:-1] + '.jpg'
                    os.rename(f'{application_path}/{file.filename}', f'{application_path}/{image}')
                    profile.face = f'/static/images/{image}'
                    profiles.append(profile)
            self.add_profiles(*profiles)

    def export_profiles_data(self, filename: str):
        file_format = filename.split('.')[-1]
        if file_format == 'json':
            self.export_profiles_data_to_json(filename)
        elif file_format == 'csv':
            self.export_profiles_data_to_csv(filename)

    def export_profiles_data_to_json(self, filename: str):
        data = []
        for profile in self.get_profiles():
            data.append(profile.to_dict())
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def export_profiles_data_to_csv(self, filename: str):
        data = []
        for profile in self.get_profiles():
            data.append(profile.to_dict())
        df = pd.DataFrame(data=data)
        df.to_csv(filename, sep=';', header=True, encoding='cp1251')

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
        profiles = self.get_profiles(*identifiers)
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
    def get_statistic(self,
                      time: str,
                      temperature: float = None):
        with models.get_session() as session:
            query = session.query(models.Statistic)
            query = query.filter(models.Statistic.time == time)
            if temperature:
                query = query.filter(models.Statistic.temperature == temperature)
            self._statistics = query.scalar()
        return self._statistics

    def get_statistics(self,
                       time: tuple = None,
                       temperature: tuple = None,
                       identifiers: list = None,
                       devices: list = None
                       ):
        """
        :param time: (start, end)
        :param temperature: (min, max)
        :param identifiers: list[int]
        :param devices: list[int]
        :return: list[models.Statistics]
        """
        with models.get_session() as session:
            query = session.query(models.Statistic)
            if time:
                query = query.filter(models.Statistic.time >= time[0],
                                     models.Statistic.time <= time[1])
            if temperature:
                query = query.filter(models.Statistic.temperature >= temperature[0],
                                     models.Statistic.temperature <= temperature[1])
            if identifiers:
                query = query.filter(models.Statistic.id_profile.in_(identifiers))
            if devices:
                query = query.filter(models.Statistic.id_device.in_(devices))
            self._statistics = query.all()
        return self._statistics

    def get_statistics_name_serial_number(self,
                                          time: tuple = None,
                                          temperature: tuple = None,
                                          name: str = None,
                                          identifiers: list = None,
                                          devices: list = None
                                          ):
        """
        :param time: (start, end)
        :param temperature: (min, max)
        :param name: example, 'Name' from ['Nma', 'Name1, 1_Name, Name], result is ['Name1, 1_Name, Name]
        :param identifiers: list[int]
        :param devices: list[int]
        :return: list[(models.Statistics, models.Profile.name)]
        """
        with models.get_session() as session:
            query = session.query(models.Statistic, models.Profile.name, models.Device.serial_number) \
                .join(models.Profile, models.Profile.id == models.Statistic.id_profile, isouter=True) \
                .join(models.Device, models.Device.id == models.Statistic.id_device, isouter=True)
            if name:
                query = query.filter(models.Profile.name.like(f'%{name}%'))
            if time:
                query = query.filter(models.Statistic.time >= time[0],
                                     models.Statistic.time <= time[1])
            if temperature:
                query = query.filter(models.Statistic.temperature >= temperature[0],
                                     models.Statistic.temperature <= temperature[1])
            if identifiers:
                query = query.filter(models.Statistic.id_profile.in_(identifiers))
            if devices:
                query = query.filter(models.Statistic.id_device.in_(devices))
            self._statistics = query.all()
        return self._statistics

    def get_number_statistics(self,
                              time: tuple = None,
                              temperature: tuple = None,
                              name: str = None,
                              identifiers: list = None,
                              devices: list = None
                              ):
        """
        :param time: (start, end)
        :param temperature: (min, max)
        :param name: example, 'Name' from ['Nma', 'Name1, 1_Name, Name], result is ['Name1, 1_Name, Name]
        :param identifiers: list[int]
        :param devices: list[int]
        :return: (int, int)
        """
        with models.get_session() as session:
            query = session.query(models.Statistic, models.Profile.name) \
                .join(models.Profile, models.Profile.id == models.Statistic.id_profile, isouter=True)
            if name:
                query = query.filter(models.Profile.name.like(f'%{name}%'))
            if time:
                query = query.filter(models.Statistic.time >= time[0],
                                     models.Statistic.time <= time[1])
            if temperature:
                query = query.filter(models.Statistic.temperature >= temperature[0],
                                     models.Statistic.temperature <= temperature[1])
            if identifiers:
                query = query.filter(models.Statistic.id_profile.in_(identifiers))
            if devices:
                query = query.filter(models.Statistic.id_device.in_(devices))
            self._number_profile_passages = query.filter(models.Statistic.id_profile.isnot(None)).count()
            self._number_stranger_passages = query.filter(models.Statistic.id_profile.is_(None)).count()
        return self._number_profile_passages, self._number_stranger_passages

    def get_number_normal_temperature_statistics(self,
                                                 threshold: float,
                                                 time: tuple = None,
                                                 temperature: tuple = None,
                                                 name: str = None,
                                                 identifiers: list = None,
                                                 devices: list = None
                                                 ):
        """
        :param threshold: max normal temperature
        :param time: (start, end)
        :param temperature: (min, max)
        :param name: example, 'Name' from ['Nma', 'Name1, 1_Name, Name], result is ['Name1, 1_Name, Name]
        :param identifiers: list[int]
        :param devices: list[int]
        :return: (int, int)
        """
        with models.get_session() as session:
            query = session.query(models.Statistic, models.Profile.name) \
                .join(models.Profile, models.Profile.id == models.Statistic.id_profile, isouter=True)
            if name:
                query = query.filter(models.Profile.name.like(f'%{name}%'))
            if time:
                query = query.filter(models.Statistic.time >= time[0],
                                     models.Statistic.time <= time[1])
            if temperature:
                query = query.filter(models.Statistic.temperature >= temperature[0],
                                     models.Statistic.temperature <= temperature[1])
            if identifiers:
                query = query.filter(models.Statistic.id_profile.in_(identifiers))
            if devices:
                query = query.filter(models.Statistic.id_device.in_(devices))
            self._number_normal_temperature_profile_passages = query.filter(models.Statistic.temperature <= threshold,
                                                                            models.Statistic.id_profile.isnot(None)) \
                .count()
            self._number_normal_temperature_stranger_passages = query.filter(models.Statistic.temperature <= threshold,
                                                                             models.Statistic.id_profile.is_(None)) \
                .count()
        return self._number_normal_temperature_profile_passages, self._number_normal_temperature_stranger_passages

    def add_statistics(self, *statistics: models.Statistic):
        with models.get_session() as session:
            session.add_all(statistics)
        self._statistics = statistics

    def remove_statistics(self, *times: tuple):
        """
        :param times: tuple[profile_identifier, datetime]
        :return: None
        """
        path = os.path.dirname(os.path.abspath(__file__))
        with models.get_session() as session:
            for time in times:
                statistic = session.query(models.Statistic) \
                    .filter(models.Statistic.time == time[1],
                            models.Statistic.id_profile == time[0]) \
                    .scalar()
                if statistic.face is not None and os.path.exists(f'{path}/snapshot{statistic.face}'):
                    os.remove(f'{path}/snapshot{statistic.face}')
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
                if comparable_statistic.id_profile == statistic.id_profile and comparable_statistic is not None:
                    time_difference = (abs(statistic.time - comparable_statistic.time)).total_seconds()
                    if 0 < time_difference <= 60:
                        removable_statistics.add((statistic.id_profile, str(statistic.time)))
        self.remove_statistics(*list(removable_statistics))

    def export_stats_data(self,
                          filename: str,
                          time: tuple = None,
                          temperature: float = None,
                          name: str = None,
                          identifiers: list = None):
        file_format = filename.split('.')[-1]
        if file_format == 'json':
            self.export_stats_data_json(
                filename,
                time=time,
                temperature=temperature,
                name=name,
                identifiers=identifiers
            )
        elif file_format == 'csv':
            self.export_stats_data_csv(
                filename,
                time=time,
                temperature=temperature,
                name=name,
                identifiers=identifiers
            )

    def export_stats_data_passage(self,
                                  filename: str,
                                  time: tuple = None,
                                  temperature: float = None,
                                  name: str = None,
                                  identifiers: list = None):
        file_format = filename.split('.')[-1]
        if file_format == 'json':
            self.export_stats_data_passage_json(
                filename,
                time=time,
                temperature=temperature,
                name=name,
                identifiers=identifiers
            )
        elif file_format == 'csv':
            self.export_stats_data_passage_csv(
                filename,
                time=time,
                temperature=temperature,
                name=name,
                identifiers=identifiers
            )

    def export_stats_data_temperatures(self,
                                       filename: str,
                                       time: tuple = None,
                                       temperature: float = None,
                                       name: str = None,
                                       identifiers: list = None):
        file_format = filename.split('.')[-1]
        if file_format == 'json':
            self.export_stats_data_temperatures_json(
                filename,
                time=time,
                temperature=temperature,
                name=name,
                identifiers=identifiers
            )
        elif file_format == 'csv':
            self.export_stats_data_temperatures_csv(
                filename,
                time=time,
                temperature=temperature,
                name=name,
                identifiers=identifiers
            )

    def export_stats_data_json(self,
                               filename: str = None,
                               time: tuple = None,
                               temperature: float = None,
                               name: str = None,
                               identifiers: list = None):
        report = {}
        for (statistic, name) in self.get_statistics_name_serial_number(
                identifiers=identifiers,
                time=time,
                temperature=temperature,
                name=name
        ):
            statistic_datetime = str(statistic.time).split(' ')
            if name in report:
                if statistic_datetime[0] in report[name]:
                    report[name][statistic_datetime[0]][statistic_datetime[1]] = \
                        {
                            'temperature': float(statistic.temperature),
                            'similar': float(statistic.similar),
                            'mask': self.get_mask(statistic.mask).mask
                        }
                else:
                    report[name][statistic_datetime[0]] = {
                        statistic_datetime[1]: {
                            'temperature': float(statistic.temperature),
                            'similar': float(statistic.similar),
                            'mask': self.get_mask(statistic.mask).mask
                        }
                    }
            else:
                report[name] = {
                    statistic_datetime[0]: {
                        statistic_datetime[1]: {
                            'temperature': float(statistic.temperature),
                            'similar': float(statistic.similar),
                            'mask': self.get_mask(statistic.mask).mask
                        }
                    }
                }
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(report, file, ensure_ascii=False, indent=4)

    def export_stats_data_csv(self,
                              filename: str,
                              time: tuple = None,
                              temperature: float = None,
                              name: str = None,
                              identifiers: list = None):
        report = pd.DataFrame(columns=['Name', 'Date', 'Time', 'Temperature', 'Mask', 'Similar'])
        for (statistic, profile_name) in self.get_statistics_name_serial_number(
                identifiers=identifiers,
                time=time,
                temperature=temperature,
                name=name
        ):
            statistic_datetime = str(statistic.time).split(' ')
            report = report.append({
                'Name': profile_name,
                'Date': statistic_datetime[0],
                'Time': statistic_datetime[1],
                'Temperature': float(statistic.temperature),
                'Mask': self.get_mask(statistic.mask).mask,
                'Similar': float(statistic.similar)
            }, ignore_index=True)
        report.to_csv(filename, sep=';', header=True, encoding='cp1251')

    def export_stats_data_passage_json(self,
                                       filename: str = None,
                                       time: tuple = None,
                                       temperature: float = None,
                                       name: str = None,
                                       identifiers: list = None):
        report = {}
        number_statistic = 0
        for (statistic, name) in self.get_statistics_name_serial_number(
                identifiers=identifiers,
                time=time,
                temperature=temperature,
                name=name
        ):
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

    def export_stats_data_passage_csv(self,
                                      filename: str,
                                      time: tuple = None,
                                      temperature: float = None,
                                      name: str = None,
                                      identifiers: list = None):
        report = pd.DataFrame(columns=['Name', 'Date', 'Came', 'Gone'])
        number_statistic = 0
        for (statistic, profile_name) in self.get_statistics_name_serial_number(
                identifiers=identifiers,
                time=time,
                temperature=temperature,
                name=name
        ):
            statistic_datetime = str(statistic.time).split(' ')
            if number_statistic % 2 == 0:
                row = {
                    'Name': profile_name,
                    'Date': statistic_datetime[0],
                    'Came': statistic_datetime[1],
                    'Gone': statistic_datetime[1]
                }
                report = report.append(row, ignore_index=True)
                number_statistic += 1
            elif row['Name'] == profile_name and row['Date'] == statistic_datetime[0]:
                report.iloc[-1]['Gone'] = statistic_datetime[1]
                number_statistic = 0
            else:
                row = {
                    'Name': profile_name,
                    'Date': statistic_datetime[0],
                    'Came': statistic_datetime[1],
                    'Gone': statistic_datetime[1]
                }
                report = report.append(row, ignore_index=True)
                number_statistic += 1
        report.to_csv(filename, sep=';', header=True, encoding='cp1251')

    def export_stats_data_temperatures_json(self,
                                            filename: str,
                                            time: tuple = None,
                                            temperature: float = None,
                                            name: str = None,
                                            identifiers: list = None):
        report = {}
        for (statistic, name) in self.get_statistics_name_serial_number(
                identifiers=identifiers,
                time=time,
                temperature=temperature,
                name=name
        ):
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

    def export_stats_data_temperatures_csv(self,
                                           filename: str,
                                           time: tuple = None,
                                           temperature: float = None,
                                           name: str = None,
                                           identifiers: list = None):
        report = pd.DataFrame(columns=['Name', 'Date', 'Time', 'Temperature'])
        for (statistic, name) in self.get_statistics_name_serial_number(
                identifiers=identifiers,
                time=time,
                temperature=temperature,
                name=name
        ):
            statistic_datetime = str(statistic.time).split(' ')
            report = report.append({
                'Name': self.get_profile_name(statistic.id_profile),
                'Date': statistic_datetime[0],
                'Time': statistic_datetime[1],
                'Temperature': float(statistic.temperature)
            }, ignore_index=True)
        report.to_csv(filename, sep=';', header=True, encoding='cp1251')


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

    def clear_devices(self):
        self.devices.clear()

    def find_devices(self, binding_devices: list = None):
        os.popen('chcp 437')
        with os.popen(f'arp -a -N {self.host}') as file:
            data = file.read()
        result = -1
        # interface = re.search('0x[a-f0-9]+', data).group()
        # interface = socket.if_indextoname(int(interface, 16)).split('_')[0]
        for device in re.findall('([-.0-9]+)\s+([-0-9a-f]{17})\s+(\w+)', data):
            if 'dynamic' in device and self.subnet == device[0][:self.host.rfind('.')]:
                mac_address = device[1].upper()
                if binding_devices is None or mac_address not in binding_devices:
                    self.get_device_basic(device_ip=device[0])
        return result

    def get_device_basic(self, device_ip: str, password: str, port: int = 7080):
        try:
            request = requests.get(f'http://{device_ip}:{port}/ini.htm',
                                   headers={'Authorization': f'Basic YWRtaW46{password}'})
            if request.status_code == 200:
                for information in request.text.split('<br>'):
                    information = information.split('=')
                    if information[0] == 'getdeviceserial':
                        serial_number = information[1]
                    elif information[0] == 'getdevname':
                        name = information[1]
                    elif information[0] == 'getdevicetype':
                        device_type = information[1]
                    elif information[0] == 'getdevicemodel':
                        model = information[1]
                    elif information[0] == 'getsoftwareversion':
                        version = information[1]
                    elif information[0] == 'mac':
                        mac_address = information[1].replace(':', '-')
                    elif information[0] == 'netip':
                        ip_address = information[1]
                self.device = models.Device(
                    serial_number=serial_number,
                    name=name,
                    device_type=device_type,
                    model=model,
                    firmware_version=version,
                    mac_address=mac_address,
                    ip_address=ip_address
                )
                self.device.password = password
                self.add_device(self.device)
                return self.device
            else:
                return None
        except requests.exceptions.ConnectionError as e:
            return None

    def find_host_info(self):
        self.host_name = socket.gethostname()
        self.host = socket.gethostbyname(self.host_name)
        self.subnet = self.host[:self.host.rfind('.')]
