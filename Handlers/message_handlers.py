from aiogram import types
from aiogram.types import ReplyKeyboardRemove 
from Config.config import dp, bot
from States.states import AuthStates, AdminPasswordState, OfferState
from Utils.utils import is_admin 
from Odoo.odoo import search_manager_list, search_leads
from Keyboards.AdminKeyboard import admin_settings_keyboard, exit_admin_keyboard, create_list_of_managers_keyboard
from Keyboards.UserKeyboard import start_keyboard, cancel_keyboard, setting_keyboard, lead_keyboard
from db import get_user_data

#Обробка повідомлень - user
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def process_user_input(message: types.Message):    
    text = message.text
    match text:
        case "Зареєструватись": 
            ((await message.answer("Вітаємо! Введіть своє ім'я.📝", reply_markup=ReplyKeyboardRemove())
            and await AuthStates.waiting_for_name.set()) if text == "Зареєструватись" and not get_user_data(message.from_user.id)
                                                            else await message.answer("Ви вже зареєстровані!"))

        case "Створити замовлення":
            await OfferState.waiting_for_name_of_offer.set()
            await bot.send_message(chat_id=message.from_user.id, text="Введіть коротке описання замовлення📝:", reply_markup=cancel_keyboard)

        case "Мої замовлення":
            leads = search_leads(message.from_user.id)
            if leads:
                for lead in leads:
                    temp = (f"ID: {lead['id']} "
                            f"\nОпис замовлення: {lead['name']}."
                            f"\nВаший менеджер: {lead['user_id'][1]}."
                            f"\nДата створення: {lead['create_date']}.")
                    await bot.send_message(chat_id=message.from_user.id, text=temp, reply_markup=lead_keyboard)
            else:
                await bot.send_message(chat_id=message.from_user.id, text="❗Ваший список замовлень пустий!")

        case "Налаштування":
            await bot.send_message(chat_id=message.from_user.id, text='Меню налаштувань 🛠️:',
                                    reply_markup=admin_settings_keyboard if is_admin(message.from_user.id) else setting_keyboard)

        case "Назад":
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await message.answer("❗Головне меню:", reply_markup=start_keyboard)

        case "Про розробника":
            await message.answer("🧑‍💻Контакт розробника: @DimaYenich", reply_markup=start_keyboard)

        case "Увійти як адмін" if not is_admin(message.from_user.id):
            await message.answer("Введіть пароль від адмін панелі 🔏: ", reply_markup=cancel_keyboard)
            await AdminPasswordState.waiting_for_admin_password.set()

        case "Вийти з адмін-панелі":
            if is_admin(message.from_user.id):
                await bot.send_message(chat_id=message.from_user.id,text="❓Бажаєте вийти з адмін-панелі?",
                                       reply_markup=exit_admin_keyboard)
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

        case "Керувати замовленнями" if is_admin(message.from_user.id):
            users = search_manager_list()
            manager_keyboard = await create_list_of_managers_keyboard(users, False, False)
            await bot.send_message(chat_id=message.from_user.id, text="Оберіть менеджера ⬇️", reply_markup=manager_keyboard)

        case _:
            await message.answer("❗Невідома команда. Виберіть іншу опцію.")