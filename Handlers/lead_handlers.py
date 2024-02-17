from aiogram import types
from aiogram.dispatcher import FSMContext
from Odoo.odoo import create_lead, update_lead_manager
from Keyboards.UserKeyboard import create_lead_keyboard, yes_no_keyboard, create_main_keyboard
from Keyboards.AdminKeyboard import create_list_of_managers_keyboard
from States.states import OfferState  
from Config.config import db, password
from Config.config import dp, bot
from Odoo.odoo import uid, models
from Odoo.odoo import search_manager_list
from db import get_user_data

#Подія кнопка створити замовлення - user
@dp.message_handler(state=OfferState.waiting_for_name_of_offer)
async def process_offer(message: types.Message, state: FSMContext):
    if message.text != 'Скасувати':
        await state.update_data(name=message.text)
        
        await OfferState.waiting_for_name_of_offer.set()
        await bot.send_message(chat_id=message.from_user.id,
                               text="🧑‍💼Оберіть свого менеджера:",
                               reply_markup=await create_list_of_managers_keyboard(search_manager_list(), True, False))
        await OfferState.waiting_for_manager.set()
    else:
        await bot.delete_message(chat_id=message.from_user.id,
                                  message_id=message.message_id)
        await message.answer(text="Створення замовлення відмінено ❌",
                             reply_markup=await create_main_keyboard(get_user_data(message.from_user.id)))
        await state.finish()


#Вибір менеджера при створені
@dp.callback_query_handler(lambda query: query.data.startswith('button_'), state=OfferState.waiting_for_manager)
async def select_manager(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data != 'button_cancel':
        manager_id = callback_query.data.split('_')[1]
        state_data = await state.get_data()
        name_of_lead = state_data.get('name')
        create_lead(name_of_lead, callback_query.from_user.id, manager_id)
        await state.finish()
        await bot.send_message(chat_id=callback_query.from_user.id,
                                text="✅Дякую, Ваше замовлення прийнято!"
                                     "\n\n📞Очікуйте дзвінок від менеджера для підтвердження та уточнення інформції!"
                                     "\n\n ℹ️Ви можете керувати своїми замовленями в категорії 'Мої замовлення'.",
                               reply_markup=get_user_data(callback_query.from_user.id))
        await bot.delete_message(chat_id=callback_query.from_user.id,
                                 message_id=callback_query.message.message_id)
    else:
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="Створення замовлення відмінено ❌",
                               reply_markup=get_user_data(callback_query.from_user.id))
        await bot.delete_message(chat_id=callback_query.from_user.id,
                                 message_id=callback_query.message.message_id)
        await state.finish()


#Натиснення кнопки "Видалити замовлення" та вивід підтвердження 
@dp.callback_query_handler(lambda query: query.data == 'delete_lead')
async def process_callback_delete_message(callback_query: types.CallbackQuery):
    await bot.edit_message_text(text=callback_query.message.text,
                                chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id, reply_markup=yes_no_keyboard)

#заміна менеджера в ліді
@dp.callback_query_handler(lambda query: query.data.startswith('changeManager_'))
async def process_callback_delete_message(callback_query: types.CallbackQuery):
    if callback_query.data.split('_')[1]=='cancel':
        await bot.edit_message_text(text=callback_query.message.text,
                                 chat_id=callback_query.from_user.id,
                                 message_id=callback_query.message.message_id,
                                 reply_markup=await create_lead_keyboard(False))
        return
    manager_id = callback_query.data.split('_')[1]
    manager_name = callback_query.data.split('_')[2]
    print(callback_query.data)
    update_lead_manager(int(callback_query.message.text.split(' ')[1]), manager_id)
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text=f"✅В замовлені з ID: {callback_query.message.text.split(' ')[1]}\nБуло замінено менеджера на {manager_name}") 
    await bot.edit_message_text(text=callback_query.message.text,
                                 chat_id=callback_query.from_user.id,
                                 message_id=callback_query.message.message_id,
                                 reply_markup=await create_lead_keyboard(False))
    await bot.delete_message(chat_id=callback_query.from_user.id, 
                             message_id=callback_query.message.message_id)
        

#Підтвердженян видалення замовлення 
@dp.callback_query_handler(lambda query: query.data.startswith('delete_')) # delete from Odoo
async def accept_delete(callback_query: types.CallbackQuery):
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
                                        message_id=callback_query.message.message_id,
                                        text=callback_query.message.text, reply_markup=create_lead_keyboard(False))