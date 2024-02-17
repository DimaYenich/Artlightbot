from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from Utils.utils import is_admin
import random

async def accept_chat_keyboard(message):
    id = message.from_user.id
    username = message.from_user.username
    accept_chat_button = InlineKeyboardButton(text='Прийняти', callback_data=f'accept_chat_button_{id}_{username}')
    accept_chat_keyboard = InlineKeyboardMarkup(row_width=1).add(accept_chat_button)
    return accept_chat_keyboard

#Вихід з адмін панелі
button_exit = InlineKeyboardButton(text='Так', callback_data='confirmExitAdmin_exit')
button_cancel = InlineKeyboardButton(text='Ні', callback_data='confirmExitAdmin_cancel')
exit_admin_keyboard = InlineKeyboardMarkup(row_width=1).add(button_exit, button_cancel)

#admin keyboard 
button_exit_admin = KeyboardButton('Вийти з адмін-панелі')
button_developer = KeyboardButton('Про розробника')
button_managers = KeyboardButton('Керувати замовленнями')
button_back = KeyboardButton('Назад')
admin_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_exit_admin).add(button_developer).add(button_managers).add(button_back)


#Створення клавіатури з списком менеджерів
async def create_list_of_managers_keyboard(users, isCreating, isChange):
    manager_list = InlineKeyboardMarkup(row_width=1)
    buttons = []

    for user in users:  
        button_text = user['name'] 
        if isChange:
            callback_data = 'changeManager_' + str(user['id']) + '_' + user['name']
        else:
            callback_data = ('adminButton_' if not isCreating else 'button_') + str(user['id']) + '_' + user['name']
        button = InlineKeyboardButton(text=button_text, callback_data=callback_data)
        buttons.append(button)
    if isCreating: 
        (random.shuffle(buttons))
    for button in buttons:
        manager_list.add(button)
    button_inline_cancel = InlineKeyboardButton(text='Назад ◀️' if isChange else ('Скасувати ❌'),
                                                callback_data='changeManager_cancel' if isChange else ('button_cancel' if isCreating else 'adminButton_cancel'))
    manager_list.add(button_inline_cancel)
    return manager_list


#Клавіатура з налаштуванням обраного менеджера
async def create_manager_keyboard(user_id, user_name):
    button_view_manager = InlineKeyboardButton(text='Переглянути замовлення', callback_data= f'manager_orders_{user_id}_{user_name}')
    button_about_manager = InlineKeyboardButton(text='Дані менеджера 📃', callback_data=f'manager_about_{user_id}_{user_name}')
    button_back_to_managers = InlineKeyboardButton(text='Назад ⬅️', callback_data=f'manager_back')
    manager_admin_settings = InlineKeyboardMarkup(row_width=1).add(button_view_manager, button_about_manager, button_back_to_managers)
    return manager_admin_settings


async def keyboard_with_orders(leads):
    orders_list = InlineKeyboardMarkup(row_width=1)
    for lead in leads:
        button_text = lead['name']
        callback_data = 'lead_'+str(lead['id'])
        button = InlineKeyboardButton(text=button_text,
                                      callback_data=callback_data)
        orders_list.add(button)
    lead_back_button = InlineKeyboardButton(text='Назад ◀️',
                                       callback_data='lead_back')
    orders_list.add(lead_back_button)
    return orders_list