from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

button_create_lead = KeyboardButton('Створити замовлення')
button_leads_list = KeyboardButton('Мої замовлення')
button_back = KeyboardButton('Назад')
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_leads_list).insert(button_create_lead)

button_registration = KeyboardButton('Зареєструватись')
registration_keyboard =ReplyKeyboardMarkup(resize_keyboard=True).add(button_registration) 

button_delete_lead = InlineKeyboardButton(text='Видалити замовлення ❌', url="google.com")
lead_keyboard = InlineKeyboardMarkup(row_width=1)
lead_keyboard.add(button_delete_lead)