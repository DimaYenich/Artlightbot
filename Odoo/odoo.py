# from Utils.utils import connect_to_odoo 
from Config.config import url, db, username, password, uid, models
from db import get_user_data

#connect
# def connect_to_odoo(url, db, username, password):
    
#     return uid, models

# uid, models = connect_to_odoo(url, db, username, password)


#update
def update_lead_manager(lead_id, new_manager_id):
    lead_data = {'user_id': int(new_manager_id)} 
    models.execute_kw(db, uid, password, 'crm.lead', 'write',[[lead_id], lead_data])


#create
def create_lead(lead_description, chat_id, manager_id):
    data = get_user_data(chat_id)
    name = str(data[1])
    phone = str(data[2])
    email = str(data[3])
    lead_data = {
        'name': lead_description,
        'contact_name': name,
        'phone': phone,
        'email_from':email,
        'mobile':'Telegram',
        'user_id': manager_id
    }  
    lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [lead_data]) # to Odoo
    return lead_id

#delete

#read 
#Список лідів по айді телеграм
def search_leads_by_chat_id(chat_id):
    result = get_user_data(chat_id)   
    if result:
        phone_number = str(result[2]) 
        domain = [['phone', 'like', '%' + phone_number[-7:]]]  
        lead_ids = models.execute_kw(db, uid, password, 'crm.lead', 'search', [domain])
        fields = ['id', 'name', 'phone', 'contact_name', 'create_date', 'user_id']
        leads = models.execute_kw(db, uid, password, 'crm.lead', 'read', [lead_ids], {'fields': fields})
        return leads
    
#лід по айді
def lead_by_id(lead_id):
    domain = [['id', '=', lead_id]]
    lead_ids = models.execute_kw(db, uid, password, 'crm.lead', 'search', [domain])
    fields = ['id', 'name', 'phone', 'contact_name', 'create_date', 'user_id']
    leads = models.execute_kw(db, uid, password, 'crm.lead', 'read', [lead_ids], {'fields': fields})
    return leads
   
#Список користувачів/менеджерів - services - to Odoo
def search_manager_list():
    user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[]])
    users = models.execute_kw(db, uid, password, 'res.users', 'read', [user_ids], {'fields': ['id', 'name', 'login']})
    return users

#Ліди користувача
def user_leads(manager_id, manager_name): #to Odoo
    lead_ids = models.execute_kw(db, uid, password, 'crm.lead', 'search',[[['user_id', '=', [manager_id, manager_name]]]])
    leads_info = models.execute_kw(db, uid, password, 'crm.lead', 'read', [lead_ids], {'fields': ['id', 'name', 'phone', 'contact_name','create_date']})
    return leads_info


#edit
