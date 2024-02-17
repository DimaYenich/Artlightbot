from aiogram import types
from aiogram.types import ReplyKeyboardRemove 
from Config.config import dp, bot, group_id
from States.states import AuthStates, AdminPasswordState, OfferState
from Utils.utils import is_admin 
from Odoo.odoo import search_manager_list, search_leads_by_chat_id
from Keyboards.AdminKeyboard import admin_settings_keyboard, exit_admin_keyboard, create_list_of_managers_keyboard, accept_chat_keyboard
from Keyboards.UserKeyboard import create_main_keyboard, cancel_keyboard, setting_keyboard, create_lead_keyboard
from db import get_user_data, change_chating_status

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
            if get_user_data(message.from_user.id):
                await OfferState.waiting_for_name_of_offer.set()
                await bot.send_message(chat_id=message.from_user.id, text="Введіть коротке описання замовлення📝:", reply_markup=cancel_keyboard)
            else:
                await bot.send_message(chat_id=message.from_user.id, text="❗Ви не зареєстровані!")
            

        case "Мої замовлення":
            if get_user_data(message.from_user.id):
                leads = search_leads_by_chat_id(message.from_user.id)
                if leads:
                    for lead in leads:
                        temp = (f"ID: {lead['id']} "
                                f"\nОпис замовлення: {lead['name']}."
                                f"\nВаший менеджер: {lead['user_id'][1]}."
                                f"\nДата створення: {lead['create_date']}.")
                        await bot.send_message(chat_id=message.from_user.id, text=temp, reply_markup=await create_lead_keyboard(False))
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="❗Ваший список замовлень пустий!")
            else:
                await bot.send_message(chat_id=message.from_user.id, text="❗Ви не зареєстровані!")

        case "Налаштування":
            if get_user_data(message.from_user.id):
                await bot.send_message(chat_id=message.from_user.id, text='Меню налаштувань 🛠️:',
                                    reply_markup=admin_settings_keyboard if is_admin(message.from_user.id) else setting_keyboard)
            else:
                await bot.send_message(chat_id=message.from_user.id, text="❗Ви не зареєстровані!")

        case "Назад":
            if get_user_data(message.from_user.id):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                await message.answer("❗Головне меню:", reply_markup=await create_main_keyboard(get_user_data(message.from_user.id)))
            else:
                await bot.send_message(chat_id=message.from_user.id, text="❗Ви не зареєстровані!")
            
        case "Про розробника":
            if get_user_data(message.from_user.id):
                await message.answer("🧑‍💻Контакт розробника: @DimaYenich", reply_markup=await create_main_keyboard(get_user_data(message.from_user.id)))
            else:
                await bot.send_message(chat_id=message.from_user.id, text="❗Ви не зареєстровані!")

        case "Увійти як адмін" if not is_admin(message.from_user.id):
            if get_user_data(message.from_user.id):
                await message.answer("Введіть пароль від адмін панелі 🔏: ", reply_markup=cancel_keyboard)
                await AdminPasswordState.waiting_for_admin_password.set()
            else:
                await bot.send_message(chat_id=message.from_user.id, text="❗Ви не зареєстровані!")

        case "Вийти з адмін-панелі":
            if is_admin(message.from_user.id):
                await bot.send_message(chat_id=message.from_user.id,text="❓Бажаєте вийти з адмін-панелі?",
                                       reply_markup=exit_admin_keyboard)
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

        case "Керувати замовленнями" if is_admin(message.from_user.id):
            users = search_manager_list()
            manager_keyboard = await create_list_of_managers_keyboard(users, False, False)
            await bot.send_message(chat_id=message.from_user.id, text="Оберіть менеджера ⬇️", reply_markup=manager_keyboard)

        case "Чат з менеджером":
            if get_user_data(message.from_user.id):
                user_data = get_user_data(chat_id=message.from_user.id)
                change_chating_status(1,  chat_id=message.from_user.id)
                await bot.send_message(chat_id=message.from_user.id, text="📨Запит на чат надіслано очікуйте підтвердження.", reply_markup=await create_main_keyboard(get_user_data(message.from_user.id)))
                await bot.send_message(chat_id=group_id,
                                    text=f"📨Запит на чат від користувача @{message.from_user.username} \n\n🧑‍💼Контактні дані: {user_data[1]}\n📞Номер телефону: {user_data[2]}",
                                    reply_markup=await accept_chat_keyboard(message)) 
            else:
                await bot.send_message(chat_id=message.from_user.id, text="❗Ви не зареєстровані!")
        case _:
            await message.answer("❗Невідома команда. Виберіть іншу опцію.")