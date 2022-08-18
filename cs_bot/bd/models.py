from cs_bot.variables import CONNECTION_BD_CS
from sqlalchemy import String, Column, DateTime, Float, BigInteger, ForeignKey, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Items(Base):
    __tablename__ = 'items'
    id = Column(BigInteger(), primary_key=True, index=True)
    hash_name = Column(String(200), nullable=False)
    name = Column(String(200), nullable=False)
    class_id = Column(BigInteger(), nullable=False)
    instance_id = Column(Integer(), nullable=False)

    price = relationship('Price', backref='Items', uselist=False)
    status = relationship('Status', backref="items", uselist=False)

    def __repr__(self):
        return f'id: {self.id} name: {self.name}'


class Price(Base):
    __tablename__ = 'price'
    id = Column(Integer(), primary_key=True)
    buy = Column(Float())
    sell = Column(Float())
    min_price = Column(Float())
    counter = Column(Integer, default=0)
    item_id = Column(BigInteger(), ForeignKey('items.id', ondelete='CASCADE'))



class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer(), primary_key=True)
    status = Column(String(5), default='hold')
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    item_id = Column(BigInteger(), ForeignKey('items.id', ondelete='CASCADE'))


Base.metadata.create_all(create_engine(CONNECTION_BD_CS))
