from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

#manage leads
async def create_inline_keyboard(users):
    manager_list = InlineKeyboardMarkup(row_width=1)
    for user in users:  
        button_text = user['name'] 
        callback_data = 'button_'+str(user['id'])+f'_{user["name"]}'
        button = InlineKeyboardButton(text=button_text, callback_data=callback_data)
        manager_list.add(button)
    return manager_list