from aiogram import types
from Config.config import *
from States.states import AuthStates, AdminPasswordState, OfferState
from Utils.utils import *  

#Обробка повідомлень - user
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def process_user_input(message: types.Message):
    #math case >    
    if message.text == "Зареєструватись":
        await message.answer("Вітаємо! Введіть своє ім'я.📝",reply_markup=ReplyKeyboardRemove())
        await AuthStates.waiting_for_name.set()

    if message.text == "Створити замовлення":
        await bot.send_message(chat_id=message.from_user.id, text="Введіть коротке описання замовлення📝:", reply_markup=cancel_keyboard)
        await OfferState.waiting_for_name_of_offer.set()

    if message.text == "Мої замовлення":
        leads = search_leads_by_phone_number(message.from_user.id)
        if leads:
            for lead in leads:
                temp = (f"ID: {lead['id']} "
                        f"\nОпис замовлення: {lead['name']}."
                        f"\nВаший менеджер: {lead['user_id'][1]}."
                        f"\nДата створення: {lead['create_date']}.")
                await bot.send_message(chat_id=message.from_user.id, text=temp, reply_markup=lead_keyboard)
        else:
            await bot.send_message(chat_id=message.from_user.id,text="❗Ваший список замовлень пустий!")

    if message.text == "Налаштування":  
        if is_admin(message.from_user.id):
            await bot.send_message(chat_id=message.from_user.id, text='Меню налаштувань 🛠️:', reply_markup = admin_settings_keyboard)
        else:   
            await bot.send_message(chat_id=message.from_user.id, text='Меню налаштувань 🛠️:', reply_markup = setting_keyboard)

    if message.text == "Назад":
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer("❗Головне меню:", reply_markup=start_keyboard)

    if message.text == "Про розробника":
        await message.answer("🧑‍💻Контакт розробника: @DimaYenich", reply_markup=start_keyboard)

    if message.text == "Увійти як адмін":
        if is_admin(message.from_user.id):
            return
        else:
            await message.answer("Введіть пароль від адмін панелі 🔏: ", reply_markup=cancel_keyboard)
            await AdminPasswordState.waiting_for_admin_password.set()

    if message.text == "Вийти з адмін-панелі":
            if is_admin(message.from_user.id):
                await bot.send_message(chat_id=message.from_user.id,text="❓Бажаєте вийти з адмін-панелі?",
                                       reply_markup=exit_admin_keyboard)
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

    if message.text == "Керувати замовленнями":
        if is_admin(message.from_user.id):
            users = search_manager_list()
            manager_keyboard = await create_inline_keyboard(users)
            await bot.send_message(chat_id=message.from_user.id, text="Оберіть менеджера ⬇️", reply_markup=manager_keyboard)