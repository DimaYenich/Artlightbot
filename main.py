from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import xmlrpc.client
from States.states import AuthStates, OfferState, AdminPasswordState
from Keyboards.Keyboard import create_inline_keyboard
from Keyboards.UserKeyboard import socialMedia_keyboard, skip_keyboard, yes_no_keyboard, cancel_keyboard, setting_keyboard,start_keyboard, lead_keyboard, registration_keyboard
from Keyboards.AdminKeyboard import admin_settings_keyboard, exit_admin_keyboard, manager_admin_settings
from DataBaseReader import cursor, conn
import re
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
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


#створити лід - user
def create_lead(lead_description, chat_id):
    uid, models = connect_to_odoo(url, db, username, password)
    cursor.execute("SELECT * FROM Users WHERE chat_id = ?", (chat_id,))
    data = cursor.fetchall()
    name = str(data[0][1])
    phone = str(data[0][2])
    lead_data = {
        'name': lead_description,
        'contact_name': name,#name,
        'phone': phone,#phone,
        'mobile':'Telegram',
        'user_id': 2
    }  
    lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [lead_data])
    return lead_id


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

#Видаленя ліда - user
@dp.callback_query_handler(lambda query: query.data == 'delete_lead')
async def process_callback_delete_message(callback_query: types.CallbackQuery):
    await bot.edit_message_text(text=callback_query.message.text,
                                chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id, reply_markup=yes_no_keyboard)

#обробка підтвердження видалення - user
@dp.callback_query_handler(lambda query: query.data.startswith('delete_'))
async def accept_delete(callback_query: types.CallbackQuery):
    uid, models = connect_to_odoo(url, db, username, password)
    if(callback_query.data.split('_')[1]=='yes'):
        if models.execute_kw(db, uid, password,
                                'crm.lead', 'search_count',
                                [[['id', '=', int(callback_query.message.text.split(' ')[1])]]])==0:
            await bot.edit_message_text(text="Видалено ❌\n" + callback_query.message.text,
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
            await bot.send_message(chat_id=callback_query.message.chat.id,
                                    text=f"❗Замовлення з ID {callback_query.message.text.split(' ')[1]} не знайдено або видалено.")
            return
        
        models.execute_kw(db, uid, password, 'crm.lead', 'unlink', [[int(callback_query.message.text.split(' ')[1])]])
        await bot.send_message(chat_id=callback_query.message.chat.id, text=f"❗Замовлення з ID {callback_query.message.text.split(' ')[1]} видалено!")
        await bot.edit_message_text(text="Видалено ❌\n" + callback_query.message.text,
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
        
    if(callback_query.data.split('_')[1]=='no'):
        if models.execute_kw(db, uid, password,
                                'crm.lead', 'search_count',
                                [[['id', '=', int(callback_query.message.text.split(' ')[1])]]])==0:
            await bot.edit_message_text(text="Видалено ❌\n" + callback_query.message.text,
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
            await bot.send_message(chat_id=callback_query.message.chat.id,
                                    text=f"❗Замовлення з ID {callback_query.message.text.split(' ')[1]} не знайдено або видалено.")
        else:
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,text=callback_query.message.text, reply_markup=lead_keyboard)


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


#обробка кнопки менеджера - подія - admin
@dp.callback_query_handler(lambda query: query.data.startswith('button_'))
async def process_callback_button(query: types.CallbackQuery):
    name = query.data.split('_')[2]
    await bot.edit_message_text(text="🧑‍💼Менеджер: " + name, chat_id=query.from_user.id,
                                message_id=query.message.message_id, reply_markup=manager_admin_settings)


#обробка меню менеджера - подія - admin
@dp.callback_query_handler(lambda query: query.data.startswith('manager_'))
async def manager_admin_st(query: types.CallbackQuery):
        if(query.data.split('_')[1]=='back'):
            users = search_manager_list()
            manager_keyboard = await create_inline_keyboard(users)
            await bot.edit_message_text(text="Оберіть менеджера ⬇️: ", chat_id=query.from_user.id,
                                        message_id=query.message.message_id, reply_markup=manager_keyboard)
        
        if(query.data.split('_')[1]=='about'):
            users = search_manager_list()
            await bot.send_message(chat_id=query.from_user.id, text=users)

        if(query.data.split('_')[1]=='orders'):
            users = search_manager_list()
            
                                    
#вихід з адмін панелі - admin
@dp.callback_query_handler(lambda query: query.data.startswith('confirmExitAdmin_'))
async def confirm_exit_admin(callback_query: types.CallbackQuery):
    if(callback_query.data.split('_')[1]=='exit'):
        await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, text = "Вихід з адмін-панелі виконаний ✅",reply_markup=start_keyboard)
        cursor.execute("UPDATE Users SET isAdmin = ? WHERE chat_id = ? ",(0, callback_query.from_user.id,))
        conn.commit()
    if(callback_query.data.split('_')[1]=='cancel'):
        await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)
        

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


#Подія кнопка створити замовлення - user
@dp.message_handler(state=OfferState.waiting_for_name_of_offer)
async def process_offer(message: types.Message, state: FSMContext):
    if message.text != 'Скасувати':
        await state.update_data(name=message.text)
        await message.answer(text="✅Дякую, Ваше замовлення прийнято!\n\n"
                            "📞Очікуйте дзвінок від менеджера для підтвердження та уточнення інформції!\n\nℹ️Ви можете керувати своїми замовленями в категорії 'Мої замовлення'.", reply_markup=start_keyboard)
        await OfferState.waiting_for_name_of_offer.set()
        create_lead(message.text, message.from_user.id)
        await state.finish()
    else:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(text="Створення замовлення відмінено ❌",reply_markup=start_keyboard)
        await state.finish()
        await state.finish()
        return


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


#Список користувачів/менеджерів - services
def search_manager_list():
    uid, models = connect_to_odoo(url, db, username, password)
    user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[]])
    users = models.execute_kw(db, uid, password, 'res.users', 'read', [user_ids], {'fields': ['id', 'name', 'login']})
    return users


#Список лідів - services
def search_leads_by_phone_number(chat_id):
    cursor.execute("SELECT number FROM Users WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    if result:
        phone_number = result[0]
        uid, models = connect_to_odoo(url, db, username, password)
        lead_ids = models.execute_kw(db, uid, password, 'crm.lead', 'search', [[['phone', '=', str(phone_number)]]])
        leads = models.execute_kw(db, uid, password, 'crm.lead', 'read', [lead_ids], {'fields': ['id', 'name', 'phone', 'contact_name','create_date','user_id']})
        return leads


#Підключення до Odoo - services
def connect_to_odoo(url, db, username, password):
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    return uid, models


#Завершення реєстрації - services
async def finish_registration(message, state, name, phone, email=None):
    await message.answer("Дякуємо за реєстрацію! 🙏", reply_markup=start_keyboard)
    await message.answer("Слідкуй за нами в соціальних мережах! 👇", reply_markup=socialMedia_keyboard)

    if email:
        cursor.execute("INSERT INTO Users (name, number, email, chat_id, isAdmin, isManager) VALUES (?, ?, ?, ?, ?, ?)", (name, phone, email, message.from_user.id, 0, 0))
    else:
        cursor.execute("INSERT INTO Users (name, number, chat_id, isAdmin, isManager) VALUES (?, ?, ?, ?, ?)", (name, phone, message.from_user.id, 0, 0))
    conn.commit()
    await state.finish()


#Провірка номеру телефону - services
def validate_phone_number(phone):
    pattern = r'^(\+?380|\b0)(\d{2})(\d{7})$'
    if re.match(pattern, phone):
        return True
    else:
        return False


#Провірка на адміна - 
def is_admin(user_id):
        cursor.execute("SELECT isAdmin FROM Users WHERE chat_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] == 1 if result else False


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)