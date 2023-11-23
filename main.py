from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import xmlrpc.client
from Keyboards.Keyboard import start_keyboard, lead_keyboard, registration_keyboard, ReplyKeyboardRemove
from DataBaseReader import cursor, conn
import re


bot = Bot(token='5974033961:AAHvtDT7kBa3soYSaIdI2BIWsnhvb595kbo')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
url = 'https://artlight.odoo.com/'
db = "artlight"
username = 'nich.dima2020@gmail.com'
password = 'admin'

class AuthStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

class OfferState(StatesGroup):
    waiting_for_name_of_offer = State()

last_created_lead_id = 0
user_states = {}


cursor.execute("SELECT * FROM Customers")
rows = cursor.fetchall()
for row in rows:
    print(row)


def create_lead(lead_description):
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    lead_data = {
        'name': lead_description,
        'contact_name': "test",
        'phone': "test",
        'mobile':'Telegram',
    }
    lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [lead_data])
    return lead_id


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
        telegram_id = message.from_user.id
        cursor.execute(
            "SELECT chat_id FROM Customers WHERE chat_id = ?", (telegram_id,))
        result = cursor.fetchone()
        if result is not None and result[0]:
            await message.answer("Головне меню:", reply_markup=start_keyboard)
        else:
            await message.answer("Ви ще не зареєстровані. Будь ласка, нажміть кнопку зареєструватись", reply_markup=registration_keyboard)
    #await bot.send_message(chat_id=message.from_user.id,text="Привіт, це бот РВК Артлайт.",reply_markup=start_keyboard)


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def process_user_input(message: types.Message):
    if message.text == "Мої замовлення":
        await bot.send_message(chat_id=message.from_user.id, text="Ваше замовлення", reply_markup=lead_keyboard)
    if message.text == "Зареєструватись":
        await message.answer("Вітаємо! Введіть своє ім'я.")
        await AuthStates.waiting_for_name.set()
    if message.text == "Створити замовлення":
        await bot.send_message(chat_id=message.from_user.id, text="Введіть описання замовлення")
        await OfferState.waiting_for_name_of_offer.set()


@dp.message_handler(state=OfferState.waiting_for_name_of_offer)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Дякую ваше замовлення прийнято!")
    await OfferState.waiting_for_name_of_offer.set()
    create_lead(message.text)
    state.finish()


@dp.message_handler(state=AuthStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Тепер введіть свій номер телефону.")
    await AuthStates.waiting_for_phone.set()


@dp.message_handler(state=AuthStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    if validate_phone_number(message.text):
        await state.update_data(phone=message.text)
        await message.answer("Дякуємо за реєстрацію!", reply_markup=start_keyboard)
        await state.finish()     
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Номер телефону введено некоректно! Спробуйте ще раз.")
        await AuthStates.waiting_for_phone.set()


def validate_phone_number(phone):
    pattern = r'^(\+?380|\b0)(\d{2})(\d{7})$'
    if re.match(pattern, phone):
        return True
    else:
        return False


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)