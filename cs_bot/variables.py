from utils import read_yaml

config = read_yaml('config.yaml')

"""Подключение к БД"""
CONNECTION_BD_CS = config['bd_cs_bot']
CONNECTION_BD_FULL_BASE = config['bd_full_base']

"""API Ключи"""
API_CS_KEY = config['cs']
API_STEAM_KEY = config['steam']

"""STEAM_ID"""
STEAM_ID = config['steam_id']

"""Для подтверждения сделок"""
ANDROID = config['config']['android']
IDENTITY_SECRET = config['config']['identity_secret']
STEAM_LOGIN_SEC = config['config']['steam_login_sec']
