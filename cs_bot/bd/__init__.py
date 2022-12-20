from sqlalchemy.orm import sessionmaker
from ..variables import CONNECTION_BD_CS, CONNECTION_BD_FULL_BASE
from sqlalchemy import create_engine


Session_cs = sessionmaker(create_engine(CONNECTION_BD_CS))
Session_full_base = sessionmaker(create_engine(CONNECTION_BD_FULL_BASE))
