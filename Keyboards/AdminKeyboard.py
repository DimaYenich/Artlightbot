from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

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

#Замовлення менеджера 
button_view_manager = InlineKeyboardButton(text='Переглянути замовлення', callback_data= 'manager_orders')
button_about_manager = InlineKeyboardButton(text='Дані менеджера 📃', callback_data='manager_about')
button_back_to_managers = InlineKeyboardButton(text='Назад ⬅️', callback_data='manager_back')
manager_admin_settings = InlineKeyboardMarkup(row_width=1).add(button_view_manager, button_about_manager, button_back_to_managers)
