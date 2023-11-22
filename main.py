from aiogram import Bot, Dispatcher, executor, types
import xmlrpc.client
from Keyboards.Keyboard import start_keyboard, lead_keyboard, ReplyKeyboardRemove

bot = Bot(token='5974033961:AAHvtDT7kBa3soYSaIdI2BIWsnhvb595kbo')
dp = Dispatcher(bot)
url = 'https://artlight.odoo.com/'
db = "artlight"
username = 'nich.dima2020@gmail.com'
password = 'admin'

last_created_lead_id = 0
user_states = {}

def create_lead(name, phone, lead_description):
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    lead_data = {
        'name': lead_description,
        'contact_name': name,
        'phone': phone,
        'mobile':'Telegram',
    }
    lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [lead_data])
    return lead_id

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,text="Привіт",reply_markup=start_keyboard)


@dp.message_handler(commands=['create_lead'])
async def create_lead_command(message: types.Message):
    await message.reply("Введіть ваше ім'я:", reply_markup=ReplyKeyboardRemove())
    user_states[message.from_user.id] = {'expected': 'name'}




@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def process_user_input(message: types.Message):
    if message.text == "Мої замовлення":
        await bot.send_message(chat_id=message.from_user.id, text="Ваше замовлення", reply_markup=lead_keyboard)
    user_id = message.from_user.id
    if user_id in user_states:
        current_state = user_states[user_id].get('expected')
        if current_state == 'name':
            name = message.text
            await message.reply("Введіть ваш номер телефону:")
            message.delete()
            user_states[user_id]['expected'] = 'phone'
            user_states[user_id]['name'] = name
        elif current_state == 'phone':
            phone = message.text
            await message.reply("Введіть опис ліда:")
            user_states[user_id]['expected'] = 'description'
            user_states[user_id]['phone'] = phone
        elif current_state == 'description':
            lead_description = message.text
            name = user_states[user_id]['name']
            phone = user_states[user_id]['phone']
            lead_id = create_lead(name, phone, lead_description)
            last_created_lead_id = lead_id
            await message.reply(f"Створено новий лід з ID: {lead_id}", reply_markup=start_keyboard)
            # Clear user state after lead creation
            del user_states[user_id]


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)