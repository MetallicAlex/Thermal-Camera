from contextlib import contextmanager
from typing import Union

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import null
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
import enum
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime, Enum, Boolean

engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost/thermalcamera')
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class Device(Base):
    __tablename__ = 'devices'

    id = Column('ID', Integer, primary_key=True, unique=True, autoincrement=True)
    serial_number = Column('SerialNumber', unique=True)
    name = Column('Name', String(32), nullable=True)
    device_type = Column('Type', String(32), nullable=True)
    model = Column('Model', String(32), nullable=True)
    firmware_version = Column('FirmwareVersion', String(32), nullable=True)
    mac_address = Column('MacAddress', String(32), nullable=True)
    ip_address = Column('IpAddress', String(32), nullable=True)
    token = Column('Token', String(32), nullable=True)
    _online = False
    _volume = 0
    _brightness = 45
    _light_supplementary = False
    _temperature_check = True
    _temperature_alarm = 37.5
    _temperature_compensation = 0.0
    _mask_detection = False
    _stranger_passage = False
    _record_save = False
    _record_save_time = -1
    _save_jpeg = False

    def __init__(self,
                 # identifier: null(),
                 serial_number: str,
                 name: str = null(),
                 device_type: str = null(),
                 model: str = null(),
                 firmware_version: str = null(),
                 mac_address: str = null(),
                 ip_address: str = null(),
                 token: str = null()
                 ):
        # self.id = identifier
        self.serial_number = serial_number
        self.name = name
        self.device_type = device_type
        self.model = model
        self.firmware_version = firmware_version
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.token = token

    @property
    def online(self):
        return self._online

    @online.setter
    def online(self, value):
        if isinstance(value, bool):
            self._online = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        if isinstance(value, int):
            if 0 <= value <= 24:
                self._volume = value
            else:
                self._volume = 0

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if isinstance(value, int):
            if 45 <= value <= 100:
                self._brightness = value
            else:
                self._brightness = 45

    @property
    def light_supplementary(self):
        return self._light_supplementary

    @light_supplementary.setter
    def light_supplementary(self, value):
        if isinstance(value, bool):
            self._light_supplementary = value

    @property
    def temperature_check(self):
        return self._temperature_check

    @temperature_check.setter
    def temperature_check(self, value):
        if isinstance(value, bool):
            self._temperature_check = value

    @property
    def temperature_alarm(self):
        return self._temperature_alarm

    @temperature_alarm.setter
    def temperature_alarm(self, value):
        if isinstance(value, float) or isinstance(value, int):
            if 35.0 <= value <= 40.0:
                self._temperature_alarm = float(value)
            else:
                self._temperature_alarm = 37.5

    @property
    def temperature_compensation(self):
        return self._temperature_compensation

    @temperature_compensation.setter
    def temperature_compensation(self, value):
        if isinstance(value, float) or isinstance(value, int):
            if -5.0 <= value <= 5.0:
                self._temperature_compensation = float(value)
            else:
                self._temperature_compensation = 0.0

    @property
    def mask_detection(self):
        return self._mask_detection

    @mask_detection.setter
    def mask_detection(self, value):
        if isinstance(value, bool):
            self._mask_detection = value

    @property
    def stranger_passage(self):
        return self._stranger_passage

    @stranger_passage.setter
    def stranger_passage(self, value):
        if isinstance(value, bool):
            self._stranger_passage = value

    @property
    def record_save(self):
        return self._record_save

    @record_save.setter
    def record_save(self, value):
        if isinstance(value, bool):
            self._record_save = value

    @property
    def save_jpeg(self):
        return self._save_jpeg

    @save_jpeg.setter
    def save_jpeg(self, value):
        if isinstance(value, bool):
            self._save_jpeg = value

    @property
    def record_save_time(self):
        return self._record_save_time

    @record_save_time.setter
    def record_save_time(self, value):
        if isinstance(value, int):
            if -1 <= value:
                self._record_save_time = value
            else:
                self._record_save_time = -1

    def __repr__(self):
        return f'[ID: {self.id}, Ser.Number: {self.serial_number}, Name: {self.name}, Type: {self.device_type},' \
               f' Model: {self.model}, Firmware Version: {self.firmware_version},' \
               f' MAC-Address: {self.mac_address}, IP-Address: {self.ip_address}, Token: {self.token}]'

    def __eq__(self, other):
        if isinstance(other, Device):
            return self.id == other.id
        elif isinstance(other, str):
            return self.mac_address == other
        return NotImplemented

    def __hash__(self):
        return hash(self.id)


class Department(Base):
    __tablename__ = 'departments'

    id = Column('ID', Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column('Name', String(32))
    location = Column('Location', String(64), nullable=True)

    def __init__(self, identifier: int = null(),
                 name: str = null(),
                 location: str = null()):
        self.id = identifier
        self.name = name
        self.location = location

    def __repr__(self):
        return f'[ID {self.id}, Department: {self.name}, Location: {self.location}]'


class Gender(Base):
    __tablename__ = 'genders'

    id = Column('ID', Integer, primary_key=True, unique=True)
    value = Column('Gender', String(16))
    description = Column('Description', String(64))

    def __repr__(self):
        return f'{self.id}: {self.value} - {self.description}'


class Profile(Base):
    __tablename__ = 'profiles'

    id = Column('ID', Integer, primary_key=True, unique=True, autoincrement=True)
    personnel_number = Column('PersonnelNumber', String(32), unique=True)
    name = Column('Name', String(64))
    visitor = Column('Visitor', Boolean, default=False)
    passport = Column('Passport', String(32), nullable=True)
    face = Column('Face', String(128), nullable=True)
    id_department = Column('IdDepartment', Integer,
                           ForeignKey('departments.ID', onupdate='CASCADE', ondelete='SET NULL'),
                           nullable=True)
    gender = Column('Gender', Integer,
                    ForeignKey('genders.ID', onupdate='NO ACTION', ondelete='NO ACTION'), default=0)
    information = Column('Information', String(512), nullable=True)

    def __init__(self,
                 identifier: int = null(),
                 personnel_number: str = null(),
                 name: str = null(),
                 passport: str = null(),
                 visitor: bool = False,
                 id_department: int = null(),
                 face: str = null(),
                 gender: int = 0,
                 information: str = null()
                 ):
        self.id = identifier
        self.personnel_number = personnel_number
        self.name = name
        self.passport = passport
        self.visitor = visitor
        self.id_department = id_department
        self.face = face
        self.gender = gender
        self.information = information

    def __repr__(self):
        return f'[ID: {self.id}, Pers.Number: {self.personnel_number}, Name: {self.name}, ' \
               f'Passport: {self.passport}, Visitor: {self.visitor}, ' \
               f'Face: {self.face}, Department: {self.id_department}, ' \
               f'Gender: {self.gender}, Information: {self.information}]\n'

    def __eq__(self, other):
        if not isinstance(other, Profile):
            return NotImplemented
        elif not self.visitor and not other.visitor:
            return self.personnel_number == other.personnel_number
        elif self.visitor and other.visitor:
            return self.passport == other.passport
        return False

    def __hash__(self):
        if self.visitor:
            return hash(self.passport)
        else:
            return hash(self.personnel_number)

    def to_dict(self):
        values = {}
        for item in Profile.__dict__.items():
            field_name = item[0]
            field_type = item[1]
            is_column = isinstance(field_type, InstrumentedAttribute)
            if is_column:
                values[field_name] = getattr(self, field_name)
        return values


class Mask(Base):
    __tablename__ = 'masks'

    id = Column('ID', Integer, primary_key=True, unique=True)
    mask = Column('Mask', String(16))

    def __repr__(self):
        return f'{self.id}: {self.mask}'


class Statistic(Base):
    __tablename__ = 'statistics'

    id_profile = Column('IdProfile', Integer,
                        ForeignKey('profiles.ID', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    time = Column('Time', DateTime, primary_key=True)
    temperature = Column('Temperature', DECIMAL(4, 2))
    mask = Column('Mask', Integer,
                  ForeignKey('masks.ID', onupdate='NO ACTION', ondelete='NO ACTION'), default=0)
    similar = Column('Similar', DECIMAL(4, 2))
    face = Column('Face', String(128))

    def __init__(self, identifier: int,
                 time: str,
                 temperature: float = 0.0,
                 similar: float = 0.0,
                 mask: int = 0,
                 face: str = null()
                 ):
        self.id_profile = identifier
        self.time = time
        self.temperature = temperature
        self.mask = mask
        self.similar = similar
        self.face = face

    def __repr__(self):
        return f'[{self.time}] ID: {self.id_profile}, Similar: {self.similar},' \
               f' Temperature: {self.temperature}, Mask: {self.mask}, Face: {self.face}\n'


class StrangerStatistic(Base):
    __tablename__ = 'stranger_statistics'

    time = Column('Time', DateTime, primary_key=True)
    temperature = Column('Temperature', DECIMAL(4, 2))
    mask = Column('Mask',)
    face = Column('Face', String(64))

    def __init__(self, time: str, temperature: float, mask: Union[str] = 0, face: str = null()):
        self.time = time
        self.temperature = temperature
        self.mask = mask
        self.face = face

    def __repr__(self):
        return f'[{self.time}] Temperature: {self.temperature}, Mask: {self.mask}, Face: {self.face}\n'


@contextmanager
def get_session():
    session = Session()
    session.expire_on_commit = False
    try:
        yield session
    except:
        session.rollback()
        raise
    else:
        session.commit()
