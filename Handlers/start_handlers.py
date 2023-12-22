from aiogram import types
from aiogram.dispatcher import FSMContext
from Utils.utils import *
from db import change_admin_status, get_user_data
from Keyboards.UserKeyboard import start_keyboard, registration_keyboard, setting_keyboard, skip_keyboard
from Keyboards.AdminKeyboard import admin_settings_keyboard, create_manager_keyboard 
from Config.config import dp, bot, admin_password
from States.states import *

#Команда /start - user
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
        result = get_user_data(message.from_user.id)
        await message.answer("❗Головне меню:" if result is not None and result[4] else 
                            "Ви ще не зареєстровані. Будь ласка, нажміть кнопку зареєструватись",
                            reply_markup=start_keyboard if result is not None and result[4] else registration_keyboard)

#Admin password - user
@dp.message_handler(state=AdminPasswordState.waiting_for_admin_password)
async def get_admin_password(message: types.Message, state: FSMContext):
    if message.text != 'Скасувати':
        if message.text == admin_password:
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Вхід в адмін-панель виконаний ✅',
                                   reply_markup=admin_settings_keyboard)
            change_admin_status(1,message.from_user.id)
            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=message.message_id)
            await state.finish()
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Пароль не вірний ❌',
                                   reply_markup=setting_keyboard)
            await state.finish()
    else:
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=message.message_id)
        await bot.send_message(chat_id=message.from_user.id,
                               text='Меню налаштувань 🛠️:',
                               reply_markup=setting_keyboard) 
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
        await bot.send_message(chat_id=message.from_user.id,
                               text="Введіть електрону пошту (необов'язково)📧:",
                               reply_markup=skip_keyboard) 
        await AuthStates.waiting_for_email.set()   
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Номер телефону введено некоректно!❌📞\nСпробуйте ще раз.")
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


@dp.callback_query_handler(lambda query: query.data.startswith('Button_'))
async def process_callback_button(query: types.CallbackQuery):
    print(query)
    manager_id = query.data.split('_')[1]
    name = query.data.split('_')[2]
    await bot.edit_message_text(text="🧑‍💼Менеджер: " + name, chat_id=query.from_user.id,
                                message_id=query.message.message_id,
                                reply_markup=await create_manager_keyboard(manager_id, name))