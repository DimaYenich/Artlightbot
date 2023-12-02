from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

#main keyboard
button_chat_with_manager = KeyboardButton('Чат з менеджером')
button_create_lead = KeyboardButton('Створити замовлення')
button_leads_list = KeyboardButton('Мої замовлення')
button_settings = KeyboardButton('Налаштування')
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add('Чат з менеджером').add(button_leads_list).insert(button_create_lead).add(button_settings)

#registration keyboard
button_registration = KeyboardButton('Зареєструватись')
registration_keyboard =ReplyKeyboardMarkup(resize_keyboard=True).add(button_registration) 

#offer keyboard
button_delete_lead = InlineKeyboardButton(text='Видалити замовлення 🗑️',  callback_data='delete_lead')
button_change_manager = InlineKeyboardButton(text='Змінити менеджера 🧑‍💼',  callback_data='change_manager')
lead_keyboard = InlineKeyboardMarkup(row_width=1)
lead_keyboard.add(button_delete_lead).add(button_change_manager)

#Delete lead accept
butoon_is_sure = InlineKeyboardButton(text='Бажаєте видалити замовлення?', callback_data='none')
button_yes = InlineKeyboardButton(text='Так', callback_data='delete_yes')
button_no = InlineKeyboardButton(text='Ні', callback_data='delete_no')
yes_no_keyboard = InlineKeyboardMarkup(row_width=2)
yes_no_keyboard.add(butoon_is_sure)
yes_no_keyboard.add(button_yes, button_no)

#Соцільані мережі
button_inst = InlineKeyboardButton(text='Instagram 📷', url='www.instagram.com/artlight_rvk')
button_yt = InlineKeyboardButton(text='Youtube 📽️', url='www.youtube.com/channel/UCIZ3U28d1aRiut5WeRBDY3A')
buttton_website = InlineKeyboardButton(text='Веб-сайт 🌐', url='www.art-light.com.ua')
socialMedia_keyboard = InlineKeyboardMarkup(row_width=1).add(button_inst).add(button_yt).add(buttton_website)

#skip keyboard
button_skip_email = KeyboardButton('Пропустити')
skip_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_skip_email)

#cancel keyboard
button_cancel = KeyboardButton(text='Скасувати', callback_data='cancel')
cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)

#settings keyboard
button_as_admin = KeyboardButton('Увійти як адмін')
button_as_manager = KeyboardButton('Увійти як менеджер')
button_developer = KeyboardButton('Про розробника')
button_back = KeyboardButton('Назад')
setting_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_as_admin, button_as_manager).add(button_developer).add(button_back)
