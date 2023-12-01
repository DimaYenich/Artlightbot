from DataBaseReader import cursor
from Config.config import * 
from Keyboards.AdminKeyboard import *
from Keyboards.UserKeyboard import *
from DataBaseReader import conn
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