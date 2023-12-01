from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from DataBaseReader import cursor
from Keyboards.UserKeyboard import lead_keyboard, yes_no_keyboard, start_keyboard
from States.states import OfferState  
from main import connect_to_odoo, url, db, username, password
from main import dp, bot

#створити лід - user
def create_lead(lead_description, chat_id):
    uid, models = connect_to_odoo(url, db, username, password)
    cursor.execute("SELECT * FROM Users WHERE chat_id = ?", (chat_id,))
    data = cursor.fetchall()
    name = str(data[0][1])
    phone = str(data[0][2])
    lead_data = {
        'name': lead_description,
        'contact_name': name,#name,
        'phone': phone,#phone,
        'mobile':'Telegram',
        'user_id': 2
    }  
    lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [lead_data])
    return lead_id

#Подія кнопка створити замовлення - user
@dp.message_handler(state=OfferState.waiting_for_name_of_offer)
async def process_offer(message: types.Message, state: FSMContext):
    if message.text != 'Скасувати':
        await state.update_data(name=message.text)
        await message.answer(text="✅Дякую, Ваше замовлення прийнято!\n\n"
                            "📞Очікуйте дзвінок від менеджера для підтвердження та уточнення інформції!\n\nℹ️Ви можете керувати своїми замовленями в категорії 'Мої замовлення'.", reply_markup=start_keyboard)
        await OfferState.waiting_for_name_of_offer.set()
        create_lead(message.text, message.from_user.id)
        await state.finish()
    else:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(text="Створення замовлення відмінено ❌",reply_markup=start_keyboard)
        await state.finish()
        return

#Видаленя ліда - user
@dp.callback_query_handler(lambda query: query.data == 'delete_lead')
async def process_callback_delete_message(callback_query: types.CallbackQuery):
    await bot.edit_message_text(text=callback_query.message.text,
                                chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id, reply_markup=yes_no_keyboard)

#обробка підтвердження видалення - user
@dp.callback_query_handler(lambda query: query.data.startswith('delete_'))
async def accept_delete(callback_query: types.CallbackQuery):
    uid, models = connect_to_odoo(url, db, username, password)
    if(callback_query.data.split('_')[1]=='yes'):
        if models.execute_kw(db, uid, password,
                                'crm.lead', 'search_count',
                                [[['id', '=', int(callback_query.message.text.split(' ')[1])]]])==0:
            await bot.edit_message_text(text="Видалено ❌\n" + callback_query.message.text,
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
            await bot.send_message(chat_id=callback_query.message.chat.id,
                                    text=f"❗Замовлення з ID {callback_query.message.text.split(' ')[1]} не знайдено або видалено.")
            return
        
        models.execute_kw(db, uid, password, 'crm.lead', 'unlink', [[int(callback_query.message.text.split(' ')[1])]])
        await bot.send_message(chat_id=callback_query.message.chat.id, text=f"❗Замовлення з ID {callback_query.message.text.split(' ')[1]} видалено!")
        await bot.edit_message_text(text="Видалено ❌\n" + callback_query.message.text,
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
        
    if(callback_query.data.split('_')[1]=='no'):
        
        if models.execute_kw(db, uid, password,
                                'crm.lead', 'search_count',
                                [[['id', '=', int(callback_query.message.text.split(' ')[1])]]])==0:
            await bot.edit_message_text(text="Видалено ❌\n" + callback_query.message.text,
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
            await bot.send_message(chat_id=callback_query.message.chat.id,
                                    text=f"❗Замовлення з ID {callback_query.message.text.split(' ')[1]} не знайдено або видалено.")
        else:
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,text=callback_query.message.text, reply_markup=lead_keyboard)