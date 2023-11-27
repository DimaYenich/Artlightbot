from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import xmlrpc.client
from Keyboards.Keyboard import start_keyboard, lead_keyboard, registration_keyboard, socialMedia_keyboard, skip_keyboard, yes_no_keyboard, cancel_keyboard, setting_keyboard, ReplyKeyboardRemove 
from DataBaseReader import cursor, conn
import re
from datetime import datetime



bot = Bot(token='5974033961:AAHvtDT7kBa3soYSaIdI2BIWsnhvb595kbo')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
url = 'https://artlight.odoo.com/'
db = "artlight"
username = 'nich.dima2020@gmail.com'
password = 'admin'
admin_password = 'testPassword'
class AuthStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_email = State()
    waiting_for_phone = State()

class OfferState(StatesGroup):
    waiting_for_name_of_offer = State()

class AdminPasswordState(StatesGroup):
    waiting_for_admin_password = State()


#user_states = {}


# cursor.execute("SELECT * FROM Users")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)


#створити лід
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


#Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
        telegram_id = message.from_user.id
        cursor.execute(
            "SELECT chat_id FROM Users WHERE chat_id = ?", (telegram_id,))
        result = cursor.fetchone()
        if result is not None and result[0]:
            await message.answer("Головне меню:", reply_markup=start_keyboard)
        else:
            await message.answer("Ви ще не зареєстровані. Будь ласка, нажміть кнопку зареєструватись", reply_markup=registration_keyboard)
    #await bot.send_message(chat_id=message.from_user.id,text="Привіт, це бот РВК Артлайт.",reply_markup=start_keyboard)


#Видаленя ліда
@dp.callback_query_handler(lambda query: query.data == 'delete_lead')
async def process_callback_delete_message(callback_query: types.CallbackQuery):
    uid, models = connect_to_odoo(url, db, username, password)
    await bot.edit_message_text(text=callback_query.message.text,
                                chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id, reply_markup=yes_no_keyboard)
    
    @dp.callback_query_handler(lambda query: query.data == 'yes')
    async def accept_delete(callback_query: types.CallbackQuery):
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
        
    @dp.callback_query_handler(lambda query: query.data == 'no')
    async def cancel_delete(callback_query: types.CallbackQuery):
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,text=callback_query.message.text, reply_markup=lead_keyboard)
    #await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


#Обробка повідомлень
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def process_user_input(message: types.Message):
    
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
        await bot.send_message(chat_id=message.from_user.id, text='Меню налаштувань 🛠️:', reply_markup = setting_keyboard)

    if message.text == "Назад":
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer("Головне меню:", reply_markup=start_keyboard)

    if message.text == "Розробник":
        await message.answer("🧑‍💻Контакт розробника: @DimaYenich", reply_markup=start_keyboard)

    if message.text == "Увійти як адмін":
        await message.answer("Введіть пароль від адмін панелі 🔏: ",reply_markup=cancel_keyboard)
        await AdminPasswordState.waiting_for_admin_password.set()


@dp.message_handler(state=AdminPasswordState.waiting_for_admin_password)
async def get_admin_password(message: types.Message, state: FSMContext):
    if message.text != 'Скасувати':
        if message.text == admin_password:
            await bot.send_message(chat_id=message.from_user.id, text='Вхід в адмін-панель виконаний ✅', reply_markup=setting_keyboard)
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await state.finish()
        else:
            await bot.send_message(chat_id=message.from_user.id, text='Пароль не вірний ❌', reply_markup=setting_keyboard)
            await state.finish()
    else:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await bot.send_message(chat_id=message.from_user.id, text='Меню налаштувань 🛠️:', reply_markup=setting_keyboard)
        await state.finish()


#Кнопка створити замовлення
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


##Реєстрація початок >
@dp.message_handler(state=AuthStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Тепер введіть свій номер телефону.")
    await AuthStates.waiting_for_phone.set()


@dp.message_handler(state=AuthStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    if validate_phone_number(message.text):
        await state.update_data(phone=message.text)
        await AuthStates.waiting_for_email.set()   
        await bot.send_message(message.from_user.id, "Введіть електрону пошту (необов'язково)📧:", reply_markup=skip_keyboard) 
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Номер телефону введено некоректно!❌📞\nСпробуйте ще раз.")
        await AuthStates.waiting_for_phone.set()


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


#Список користувачів/менеджерів
def search_manager_list():
    uid, models = connect_to_odoo(url, db, username, password)
    user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[]])
    users = models.execute_kw(db, uid, password, 'res.users', 'read', [user_ids], {'fields': ['id', 'name', 'login']})
    return users


#Список лідів
def search_leads_by_phone_number(chat_id):
    cursor.execute("SELECT number FROM Users WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    if result:
        phone_number = result[0]
        uid, models = connect_to_odoo(url, db, username, password)
        lead_ids = models.execute_kw(db, uid, password, 'crm.lead', 'search', [[['phone', '=', str(phone_number)]]])
        leads = models.execute_kw(db, uid, password, 'crm.lead', 'read', [lead_ids], {'fields': ['id', 'name', 'phone', 'contact_name','create_date','user_id']})
        return leads


def connect_to_odoo(url, db, username, password):
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    return uid, models


#Завершення реєстрації
async def finish_registration(message, state, name, phone, email=None):
    await message.answer("Дякуємо за реєстрацію! 🙏", reply_markup=start_keyboard)
    await message.answer("Слідкуй за нами в соціальних мережах! 👇", reply_markup=socialMedia_keyboard)

    if email:
        cursor.execute("INSERT INTO Users (name, number, email, chat_id) VALUES (?, ?, ?, ?)", (name, phone, email, message.from_user.id))
    else:
        cursor.execute("INSERT INTO Users (name, number, chat_id) VALUES (?, ?, ?)", (name, phone, message.from_user.id))
    conn.commit()
    await state.finish()


#Провірка номеру телефону
def validate_phone_number(phone):
    pattern = r'^(\+?380|\b0)(\d{2})(\d{7})$'
    if re.match(pattern, phone):
        return True
    else:
        return False
    

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)