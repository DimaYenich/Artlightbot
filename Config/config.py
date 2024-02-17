from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import xmlrpc.client
import os

load_dotenv(find_dotenv())

url = os.getenv("DATABASE_URL")
db = os.getenv("DATABASE_NAME")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
admin_password = os.getenv("ADMIN_PASSWORD")
manager_password = os.getenv("MANAGER_PASSWORD")
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
group_id = os.getenv("GROUP_ID")