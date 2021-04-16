from contextlib import contextmanager
from typing import Union

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import null
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
import enum
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime, Enum

engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost/thermalcamera')
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class Device(Base):
    __tablename__ = 'devices'

    id = Column('ID', String(32), primary_key=True, unique=True)
    name = Column('Name', String(32), nullable=True)
    model = Column('Model', String(32), nullable=True)
    version = Column('Version', String(32), nullable=True)
    mac_address = Column('MAC-Address', String(32), nullable=True)
    ip_address = Column('IP-Address', String(32), nullable=True)
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

    def __init__(self, identifier: str,
                 name: str = null(),
                 model: str = null(),
                 version: str = null(),
                 mac_address: str = null(),
                 ip_address: str = null(),
                 token: str = null()
                 ):
        self.id = identifier
        self.name = name
        self.model = model
        self.version = version
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
        return f'[ID: {self.id}, Name: {self.name}, Model: {self.model}, Version: {self.version},' \
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

    name = Column('Name', String(32), primary_key=True)

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f'[Department] {self.name}'


class GenderEnum(enum.Enum):
    male = 1
    female = 2

    def __str__(self):
        if self.value == 1:
            return 'male'
        else:
            return 'female'


class Profile(Base):
    __tablename__ = 'profiles'

    id = Column('ID', String(32), primary_key=True, unique=True)
    name = Column('Name', String(32), primary_key=True, unique=True)
    face = Column('Face', String(128), nullable=True)
    name_department = Column('NameDepartment', String(32),
                             ForeignKey('departments.Name', onupdate='CASCADE', ondelete='SET NULL'),
                             nullable=True)
    gender = Column('Gender', Enum(GenderEnum), nullable=True)
    phone_number = Column('PhoneNumber', String(32), nullable=True)

    def __init__(self, identifier: str,
                 name: str,
                 name_department: str = null(),
                 face: str = null(),
                 gender: Union[str, GenderEnum] = null(),
                 phone_number: str = null()
                 ):
        self.id = identifier
        self.name = name
        self.name_department = name_department
        self.face = face
        self.gender = gender
        self.phone_number = phone_number

    def __repr__(self):
        return f'[PROFILE] ID: {self.id}, Name: {self.name}, Face: {self.face}, Department: {self.name_department}, ' \
               f'Gender: {self.gender}, Phone Number: {self.phone_number}\n'

    def __eq__(self, other):
        if not isinstance(other, Profile):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def to_dict(self):
        values = {}
        for item in Profile.__dict__.items():
            field_name = item[0]
            field_type = item[1]
            is_column = isinstance(field_type, InstrumentedAttribute)
            if is_column:
                values[field_name] = getattr(self, field_name)
        return values


class MaskEnum(enum.Enum):
    unknow = 1
    true = 2
    false = 3

    def __str__(self):
        if self.value == 3:
            return 'false'
        elif self.value == 2:
            return 'true'
        else:
            return 'unknow'


class Statistic(Base):
    __tablename__ = 'statistics'

    id_profile = Column('IdProfile', String(32),
                        ForeignKey('profiles.ID', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    time = Column('Time', DateTime, primary_key=True)
    temperature = Column('Temperature', DECIMAL(4, 2))
    mask = Column('Mask', Enum(MaskEnum))
    similar = Column('Similar', DECIMAL(4, 2))
    face = Column('Face', String(128))

    def __init__(self, identifier: str,
                 time: str,
                 temperature: float,
                 similar: float,
                 mask: Union[str, MaskEnum] = MaskEnum.unknow,
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
    mask = Column('Mask', Enum(MaskEnum))
    face = Column('Face', String(64))

    def __init__(self, time: str, temperature: float, mask: Union[str, MaskEnum] = MaskEnum.unknow, face: str = null()):
        self.time = time
        self.temperature = temperature
        self.mask = mask
        self.face = face

    def __repr__(self):
        return f'[{self.time}] Temperature: {self.temperature}, Mask: {self.mask}, Face: {self.face}\n'


@contextmanager
def get_session():
    session = Session()
    try:
        yield session
    except:
        session.rollback()
        raise
    else:
        session.commit()
