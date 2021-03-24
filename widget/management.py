import os
import re
import json
import socket
from datetime import datetime
import zipfile
from typing import Union
import pandas as pd

import widget.models as models


class DBManagement:
    def __init__(self):
        self._profile_name = str
        self._pattern = None
        self._departments = models.Department
        self._profiles = models.Profile
        self._statistics = models.Statistic
        self._stranger_statistics = models.StrangerStatistic

    # DEPARTMENTS
    def get_departments(self):
        with models.get_session() as session:
            self._departments = session.query(models.Department) \
                .all()
            return self._departments

    def add_departments(self, *departments: models.Department):
        with models.get_session() as session:
            session.add_all(departments)
        self._departments = departments

    def edit_department(self, old_name: str, new_name: str):
        with models.get_session() as session:
            session.query(models.Department) \
                .filter(models.Department.name == old_name) \
                .update({models.Department.name: new_name})
        self._departments = None

    def remove_departments(self, *names: str):
        with models.get_session() as session:
            session.query(models.Department) \
                .filter(models.Department.name.in_(names)) \
                .delete(synchronize_session=False)
        self._departments = None

    # PROFILES
    def exists_profile(self, identifier: str):
        with models.get_session() as session:
            profile = session.query(models.Profile) \
                .filter(models.Profile.id == identifier) \
                .first()
        if profile:
            self._profiles = profile
            return True
        return False

    def get_profile_name(self, identifier):
        with models.get_session() as session:
            profile_name = session.query(models.Profile.name) \
                .filter(models.Profile.id == identifier) \
                .scalar()
        self._profile_name = profile_name
        return profile_name

    def get_profiles(self, *identifiers: str):
        with models.get_session() as session:
            if not identifiers:
                self._profiles = session.query(models.Profile) \
                    .all()
            else:
                self._profiles = session.query(models.Profile) \
                    .filter(models.Profile.id.in_(identifiers)) \
                    .all()
        return self._profiles

    def create_profiles_pattern(self, filename):
        data = [['xxx', 'Ivanov Ivan', 'No Group', 'male', ''],
                ['yyy', 'Ivanov Ilia', '', '', '+375(33)9999999']]
        self._pattern = pd.DataFrame(data=data, columns=['ID', 'Name', 'Department', 'Gender', 'Phone Number'])
        self._pattern.to_csv(filename, sep=';', index=False)

    def add_profiles_from_pattern(self, filename):
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
        update_profiles = list(profiles & current_profiles)
        self.add_profiles(*insert_profiles)
        for profile in update_profiles:
            self.update_profile(profile.id, profile)

    def add_profiles_from_images(self, filename):
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

    def add_profiles(self, *profiles: models.Profile):
        with models.get_session() as session:
            session.add_all(profiles)
        self._profiles = profiles

    def update_profile(self, identifier: str, new_profile: Union[models.Profile, dict]):
        with models.get_session() as session:
            if isinstance(new_profile, models.Profile):
                session.query(models.Profile) \
                    .filter(models.Profile.id == identifier) \
                    .update(
                    {
                        models.Profile.id: new_profile.id,
                        models.Profile.name: new_profile.name,
                        models.Profile.face: new_profile.face,
                        models.Profile.name_department: new_profile.name_department,
                        models.Profile.gender: new_profile.gender,
                        models.Profile.phone_number: new_profile.phone_number
                    }
                )
            elif isinstance(new_profile, dict):
                session.query(models.Profile) \
                    .filter(models.Profile.id == identifier) \
                    .update(new_profile)
        self._profiles = new_profile

    def remove_profiles(self, *identifiers: str):
        with models.get_session() as session:
            session.query(models.Profile) \
                .filter(models.Profile.id.in_(identifiers)) \
                .delete(synchronize_session=False)
        self._profiles = None

    # STATISTICS
    def get_statistics(self,
                       low: Union[str, float] = None,
                       high: Union[str, float] = None,
                       identifiers: list = None,
                       profile_name: bool = False):
        with models.get_session() as session:
            if profile_name:
                query = session.query(models.Statistic, models.Profile.name)\
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
            self._statistics = query.all()
        return self._statistics

    def add_statistics(self, *statistics: models.Statistic):
        with models.get_session() as session:
            session.add_all(statistics)
        self._statistics = statistics

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

    def create_temperatures_report(self, filename: str):
        pass

    def create_passage_report(self, filename: str):
        report = {}
        for statistic in self.get_statistics():
            pass


    # STRANGER STATISTICS
    def get_stranger_statistics(self, low: Union[str, float] = None, high: Union[str, float] = None):
        with models.get_session() as session:
            if isinstance(low, str) and isinstance(high, str):
                self._stranger_statistics = session.query(models.StrangerStatistic) \
                    .filter(
                    models.StrangerStatistic.time >= low,
                    models.StrangerStatistic.time <= high) \
                    .all()
            elif isinstance(low, float) and isinstance(high, float):
                self._stranger_statistics = session.query(models.StrangerStatistic) \
                    .filter(models.StrangerStatistic.temperature >= low,
                            models.StrangerStatistic.temperature <= high) \
                    .all()
            else:
                self._stranger_statistics = session.query(models.StrangerStatistic) \
                    .all()
        return self._stranger_statistics

    def add_stranger_statistics(self, *statistics: models.StrangerStatistic):
        with models.get_session() as session:
            session.add(statistics)
        self._stranger_statistics = statistics

    def remove_stranger_statistics(self, *times: str):
        with models.get_session() as session:
            session.query(models.StrangerStatistic) \
                .filter(models.StrangerStatistic.time.in_(times)) \
                .delete(synchronize_session=False)
        self._stranger_statistics = None


class DeviceManagement:
    def __init__(self):
        self._path_file = os.path.dirname(os.path.abspath(__file__))
        with open(f'{self._path_file}/data/devices.json') as file:
            self._devices = json.load(file, strict=False)
        self._host_name = None
        self._host = None
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
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def devices(self):
        return self._devices

    def add_device(self):
        pass

    def remove_device(self):
        pass

    def save_devices(self):
        with open(f'{self._path_file}/data/devices.json', 'w') as file:
            json.dump(self.devices, file)

    def find_devices(self):
        os.system('chcp 437')
        with os.popen(f'arp -a -N {self.host_ip}') as file:
            data = file.read()
        devices = []
        for device in re.findall('([-.0-9]+)\s+([-0-9a-f]{17})\s+(\w+)', data):
            if 'dynamic' in device:
                devices.append(device[:2])

    def find_host_info(self):
        self.host_name = socket.gethostname()
        self.host = socket.gethostbyname(self.host_name)
