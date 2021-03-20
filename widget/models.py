from contextlib import contextmanager
from typing import Union

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import null
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
import enum
from sqlalchemy import Column, String, DECIMAL, ForeignKey, DateTime, Enum

engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost/thermalcamera')
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


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
    face = Column('Face', String(64), nullable=True)
    name_department = Column('NameDepartment', String(32),
                             ForeignKey('departments.Name', onupdate='CASCADE', ondelete='CASCADE'),
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
    name_profile = Column('NameProfile', String(32),
                          ForeignKey('profiles.Name', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    time = Column('Time', DateTime, primary_key=True)
    temperature = Column('Temperature', DECIMAL(4, 2))
    mask = Column('Mask', Enum(MaskEnum))
    similar = Column('Similar', DECIMAL(4, 2))
    face = Column('Face', String(64))

    def __init__(self, identifier: str,
                 name_profile: str,
                 time: str,
                 temperature: float,
                 mask: Union[str, MaskEnum],
                 similar: float,
                 face: str = None
                 ):
        self.id_profile = identifier
        self.name_profile = name_profile
        self.time = time
        self.temperature = temperature
        self.mask = mask
        self.similar = similar
        self.face = face

    def __repr__(self):
        return f'[{self.time}] ID: {self.id_profile}, Name: {self.name_profile}, Similar: {self.similar},' \
               f' Temperature: {self.temperature}, Mask: {self.mask}, Face: {self.face}\n'


class StrangerStatistic(Base):
    __tablename__ = 'stranger_statistics'

    time = Column('Time', DateTime, primary_key=True)
    temperature = Column('Temperature', DECIMAL(4, 2))
    mask = Column('Mask', Enum(MaskEnum))
    face = Column('Face', String(64))

    def __init__(self, time: str, temperature: float, mask: Union[str, MaskEnum], face: str):
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
