from Config.config import db, url, username, password 
from Keyboards.UserKeyboard import start_keyboard, socialMedia_keyboard
from db import add_new_user, get_user_data
import xmlrpc.client
import re

#Список користувачів/менеджерів - services
def search_manager_list():
    uid, models = connect_to_odoo(url, db, username, password)
    # fields_info = models.execute_kw(db, uid, password, models, 'fields_get', [], {'attributes': ['string', 'type']})
    # for field_name, field_info in fields_info.items():
    #     print(f"Field Name: {field_name}, Type: {field_info['type']}, Label: {field_info['string']}")
    user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[]])
    users = models.execute_kw(db, uid, password, 'res.users', 'read', [user_ids], {'fields': ['id', 'name', 'login']})
    return users

#Список лідів за номером телефону - services
def search_leads_by_phone_number(chat_id):
    result = get_user_data(chat_id)
    if result:
        phone_number = result[2]
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
    add_new_user(name, phone, email if email else None, message.from_user.id)
    await state.finish()

#Провірка номеру телефону - services
def validate_phone_number(phone):
    pattern = r'^(\+?380|\b0)(\d{2})(\d{7})$'
    if re.match(pattern, phone):
        return True
    else:
        return False


def user_leads(manager_id, manager_name):
    uid, models = connect_to_odoo(url,db,username, password)
    lead_ids = models.execute_kw(db, uid, password, 'crm.lead', 'search',[[['user_id', '=', [manager_id, manager_name]]]])
    leads_info = models.execute_kw(db, uid, password, 'crm.lead', 'read', [lead_ids], {'fields': ['id', 'name', 'phone', 'contact_name','create_date']})
    return leads_info

#Провірка на адміна - 
def is_admin(user_id):
    result = get_user_data(user_id)
    return result[5] == 1 if result else False