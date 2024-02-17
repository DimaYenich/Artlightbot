from Keyboards.UserKeyboard import socialMedia_keyboard, create_main_keyboard
from db import add_new_user, get_user_data
import re


#Завершення реєстрації
async def finish_registration(message, state, name, phone, email=None):
    await message.answer("Дякуємо за реєстрацію! 🙏", reply_markup=await create_main_keyboard(get_user_data(message.from_user.id)))
    await message.answer("Слідкуй за нами в соціальних мережах! 👇", reply_markup=socialMedia_keyboard)
    add_new_user(name, format_phone_number(phone), email if email else None, message.from_user.id)
    await state.finish()


def format_phone_number(phone_number):
    digits = ''.join(filter(str.isdigit, phone_number))

    if len(digits) == 10:
        formatted_number = '+380 ' + digits[1:3] + ' ' + digits[3:6] + ' ' + digits[6:]
    elif len(digits) == 12 and digits.startswith('380'):
        formatted_number = '+380 ' + digits[3:5] + ' ' + digits[5:8] + ' ' + digits[8:]
    elif len(digits) == 13 and digits.startswith('380'): 
        formatted_number = '+380 ' + digits[4:6] + ' ' + digits[6:9] + ' ' + digits[9:]
    else:
        formatted_number = 'Непідтримуваний формат номеру'
    return formatted_number


#Провірка номеру телефону - services
def validate_phone_number(phone):
    pattern = r'^(\+?380|\b0)(\d{2})(\d{7})$'
    if re.match(pattern, phone):
        return True
    else:
        return False


#Провірка на адміна - 
def is_admin(user_id):
    result = get_user_data(user_id)
    return result[5] == 1 if result else False