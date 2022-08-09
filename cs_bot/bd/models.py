from cs_bot.variables import CONNECTION_BD_CS, CONNECTION_BD_FULL_BASE
from sqlalchemy import String, Column, DateTime, Float, BigInteger, ForeignKey, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from datetime import datetime

Base = declarative_base()
engine_bd_cs = create_engine(CONNECTION_BD_CS)
engine_bd_full_base = create_engine(CONNECTION_BD_FULL_BASE)

# class BaseModel(Base):
#     __abstract__ = True
#
#     id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
#     created_on = Column(DateTime(), default=datetime.now)
#     updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
#
#     def __repr__(self):
#         return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Items(Base):
    __tablename__ = 'items'
    id = Column(BigInteger(), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    class_id = Column(BigInteger(), nullable=False)
    instance_id = Column(Integer(), nullable=False)

    price = relationship('Price', backref='Items')
    status = relationship('Status', backref="items")

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
    #items = relationship('Items', back_populates="price")


class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer(), primary_key=True)
    status = Column(String(4), default='hold')
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    item_id = Column(BigInteger(), ForeignKey('items.id', ondelete='CASCADE'))

    # items = relationship('Items', back_populates="status")



Base.metadata.create_all(engine_bd_cs)
