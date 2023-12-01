from aiogram import types
from aiogram.dispatcher import FSMContext
from Utils.utils import *
from DataBaseReader import cursor
from Keyboards.UserKeyboard import start_keyboard, registration_keyboard  
from Config.config import dp, bot
from States.states import *

#Команда /start - user
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
        telegram_id = message.from_user.id
        cursor.execute(
            "SELECT chat_id FROM Users WHERE chat_id = ?", (telegram_id,))
        result = cursor.fetchone()
        if result is not None and result[0]:
            await message.answer("❗Головне меню:", reply_markup=start_keyboard)
        else:
            await message.answer("Ви ще не зареєстровані. Будь ласка, нажміть кнопку зареєструватись", reply_markup=registration_keyboard)
    #await bot.send_message(chat_id=message.from_user.id,text="Привіт, це бот РВК Артлайт.",reply_markup=start_keyboard)

#Admin password - user
@dp.message_handler(state=AdminPasswordState.waiting_for_admin_password)
async def get_admin_password(message: types.Message, state: FSMContext):
    if message.text != 'Скасувати':
        if message.text == admin_password:
            await bot.send_message(chat_id=message.from_user.id, text='Вхід в адмін-панель виконаний ✅', reply_markup=admin_settings_keyboard)
            cursor.execute("UPDATE Users SET isAdmin = ? WHERE chat_id = ? ",(1, message.from_user.id,))
            conn.commit()
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await state.finish()
        else:
            await bot.send_message(chat_id=message.from_user.id, text='Пароль не вірний ❌', reply_markup=setting_keyboard)
            await state.finish()
    else:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await bot.send_message(chat_id=message.from_user.id, text='Меню налаштувань 🛠️:', reply_markup=setting_keyboard)#замінити на 
        await state.finish()

##Реєстрація початок > user
@dp.message_handler(state=AuthStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Тепер введіть свій номер телефону.")
    await AuthStates.waiting_for_phone.set()

#Очікування номеру
@dp.message_handler(state=AuthStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    if validate_phone_number(message.text):
        await state.update_data(phone=message.text)
        await AuthStates.waiting_for_email.set()   
        await bot.send_message(message.from_user.id, "Введіть електрону пошту (необов'язково)📧:", reply_markup=skip_keyboard) 
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Номер телефону введено некоректно!❌📞\nСпробуйте ще раз.")
        await AuthStates.waiting_for_phone.set()


#Очікування пошту
@dp.message_handler(state=AuthStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    name = state_data.get('name')
    phone = state_data.get('phone')

    if message.text == 'Пропустити':
        await finish_registration(message, state, name, phone)
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        return
    await state.update_data(email=message.text)
    await message.answer("Email додано!", reply_markup=start_keyboard)
    await finish_registration(message, state, name, phone, message.text)
##Реєстрація кінець <