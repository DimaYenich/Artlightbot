from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

#main keyboard
button_create_lead = KeyboardButton('Створити замовлення')
button_leads_list = KeyboardButton('Мої замовлення')
button_back = KeyboardButton('Назад')
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_leads_list).insert(button_create_lead)

#registration keyboard
button_registration = KeyboardButton('Зареєструватись')
registration_keyboard =ReplyKeyboardMarkup(resize_keyboard=True).add(button_registration) 

#offer keyboard
button_delete_lead = InlineKeyboardButton(text='Видалити замовлення ❌', url="google.com")
lead_keyboard = InlineKeyboardMarkup(row_width=1)
lead_keyboard.add(button_delete_lead)

#social media keyboard
button_inst = InlineKeyboardButton(text='Instagram 📷', url='www.instagram.com/artlight_rvk')
button_yt = InlineKeyboardButton(text='Youtube 📽️', url='www.youtube.com/channel/UCIZ3U28d1aRiut5WeRBDY3A')
buttton_website = InlineKeyboardButton(text='Веб-сайт 🌐', url='www.art-light.com.ua')
socialMedia_keyboard = InlineKeyboardMarkup(row_width=1).add(button_inst).add(button_yt).add(buttton_website)

#skip keyboard
button_skip_email = KeyboardButton('Пропустити')
skip_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_skip_email)