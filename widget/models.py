from contextlib import contextmanager
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import MetaData
import enum
from sqlalchemy import Table, Column, Integer, String, DECIMAL, ForeignKey, DateTime, Enum

engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost/thermalcamera')
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# session = Session()


class Department(Base):
    __tablename__ = 'departments'

    name = Column('Name', String(32), primary_key=True)

    def __init__(self, name):
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


class Employee(Base):
    __tablename__ = 'employees'

    id = Column('ID', Integer, primary_key=True, unique=True)
    name = Column('Name', String(32), primary_key=True)
    face = Column('Face', String(64))
    name_department = Column('NameDepartment', String(32),
                             ForeignKey('departments.Name', onupdate='CASCADE', ondelete='CASCADE'))
    gender = Column('Gender', Enum(GenderEnum))
    phone_number = Column('PhoneNumber', String(32))

    def __init__(self, id, name, name_department, face, gender, phone_number):
        self.id = id
        self.name = name
        self.name_department = name_department
        self.face = face
        self.gender = gender
        self.phone_number = phone_number

    def __repr__(self):
        return f'[EMPLOYEE] ID: {self.id}, Name: {self.name}, Face: {self.face}, Department: {self.name_department}, ' \
               f'Gender: {self.gender}, Phone Number: {self.phone_number}\n'


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

    id_employee = Column('IdEmployee', Integer,
                         ForeignKey('employees.ID', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    time = Column('Time', DateTime, primary_key=True)
    temperature = Column('Temperature', DECIMAL(4, 2))
    mask = Column('Mask', Enum(MaskEnum))
    similar = Column('Similar', DECIMAL(4, 2))

    def __init__(self, id_employee, time, temperature, mask, similar):
        self.id_employee = id_employee
        self.time = time
        self.temperature = temperature
        self.mask = mask
        self.similar = similar

    def __repr__(self):
        return f'[{self.time}] ID: {self.id_employee}, Similar: {self.similar}, Temperature: {self.temperature}, ' \
               f'Mask: {self.mask}\n'


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
