from aiogram import types
from Keyboards.UserKeyboard import start_keyboard
from Keyboards.AdminKeyboard import create_list_of_managers_keyboard, create_manager_keyboard
from db import change_admin_status
from main import dp, bot
from Utils.utils import search_manager_list, user_leads

#обробка кнопки менеджера - подія - admin
@dp.callback_query_handler(lambda query: query.data.startswith('button_'))
async def process_callback_button(query: types.CallbackQuery):
    manager_id = query.data.split('_')[1]
    name = query.data.split('_')[2]
    await bot.edit_message_text(text="🧑‍💼Менеджер: " + name, chat_id=query.from_user.id,
                                message_id=query.message.message_id, reply_markup=await create_manager_keyboard(manager_id, name))

#обробка меню менеджера - подія - admin
@dp.callback_query_handler(lambda query: query.data.startswith('manager_'))
async def manager_admin_st(query: types.CallbackQuery):
        users = search_manager_list()
        managers_list_keyboard = await create_list_of_managers_keyboard(users)
        #Дані менеджера
        if(query.data.split('_')[1]=='about'):
            id = query.data.split('_')[2]
            name = query.data.split('_')[3]
            print('test')#)
        
        #Переглянути замовлення
        if(query.data.split('_')[1]=='orders'):
            id = query.data.split('_')[2]
            name = query.data.split('_')[3]
            leads = user_leads(id, name)
            if len(leads)==0:
                 await bot.send_message(text=f'❗{name} немає замовлень.', chat_id=query.from_user.id)
                 await bot.edit_message_text(text="Оберіть менеджера ⬇️: ", chat_id=query.from_user.id,
                                        message_id=query.message.message_id, reply_markup=managers_list_keyboard)
                 return
            for lead in leads:
                 await bot.send_message(text=lead, chat_id=query.from_user.id)

        #Кнопка "назад"            
        if(query.data.split('_')[1]=='back'):
            await bot.edit_message_text(text="Оберіть менеджера ⬇️: ", chat_id=query.from_user.id,
                                        message_id=query.message.message_id, reply_markup=managers_list_keyboard)
                                    
#вихід з адмін панелі - admin
@dp.callback_query_handler(lambda query: query.data.startswith('confirmExitAdmin_'))
async def confirm_exit_admin(callback_query: types.CallbackQuery):
    split_data = callback_query.data.split('_')
    action = split_data[1]

    if action in ['exit', 'cancel']:
        await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)

    if action == 'exit':
        await bot.send_message(callback_query.from_user.id, text="Вихід з адмін-панелі виконаний ✅", reply_markup=start_keyboard)
        change_admin_status(0, callback_query.from_user.id)
        