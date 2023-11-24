from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

#main keyboard
button_create_lead = KeyboardButton('Створити замовлення')
button_leads_list = KeyboardButton('Мої замовлення')
#button_back = KeyboardButton('Назад')
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_leads_list).insert(button_create_lead)

#registration keyboard
button_registration = KeyboardButton('Зареєструватись')
registration_keyboard =ReplyKeyboardMarkup(resize_keyboard=True).add(button_registration) 

#offer keyboard
button_delete_lead = InlineKeyboardButton(text='Видалити замовлення 🗑️',  callback_data='delete_message')
button_change_manager = InlineKeyboardButton(text='Змінити менеджера 🧑‍💼',  callback_data='delete_lead')
lead_keyboard = InlineKeyboardMarkup(row_width=1)
lead_keyboard.add(button_delete_lead).add(button_change_manager)

#Yes No Keyboard
butoon_is_sure = InlineKeyboardButton(text='Бажаєте видалити замовлення?', callback_data='none')
button_yes = InlineKeyboardButton(text='Так', callback_data='yes')
button_no = InlineKeyboardButton(text='Ні', callback_data='no')
yes_no_keyboard = InlineKeyboardMarkup(row_width=2)
yes_no_keyboard.add(butoon_is_sure)
yes_no_keyboard.add(button_yes, button_no)


#social media keyboard
button_inst = InlineKeyboardButton(text='Instagram 📷', url='www.instagram.com/artlight_rvk')
button_yt = InlineKeyboardButton(text='Youtube 📽️', url='www.youtube.com/channel/UCIZ3U28d1aRiut5WeRBDY3A')
buttton_website = InlineKeyboardButton(text='Веб-сайт 🌐', url='www.art-light.com.ua')
socialMedia_keyboard = InlineKeyboardMarkup(row_width=1).add(button_inst).add(button_yt).add(buttton_website)

#skip keyboard
button_skip_email = KeyboardButton('Пропустити')
skip_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_skip_email)