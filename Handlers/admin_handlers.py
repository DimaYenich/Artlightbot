from aiogram import types
from Keyboards.UserKeyboard import create_lead_keyboard, create_main_keyboard
from Keyboards.AdminKeyboard import create_list_of_managers_keyboard, create_manager_keyboard, keyboard_with_orders
from db import change_admin_status, get_user_data
from main import dp, bot
from Odoo.odoo import search_manager_list, user_leads, search_manager_list, search_leads_by_chat_id, lead_by_id

#Вибір менеджера з клавіатури
@dp.callback_query_handler(lambda query: query.data.startswith('adminButton_'))
async def process_callback_button(callback_query: types.CallbackQuery):
    if callback_query.data.split('_')[1] == 'cancel':
         await bot.delete_message(chat_id=callback_query.from_user.id,
                                  message_id=callback_query.message.message_id)
         return
    manager_id = callback_query.data.split('_')[1]
    name = callback_query.data.split('_')[2]
    await bot.edit_message_text(text="🧑‍💼Менеджер: " + name, chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id, reply_markup=await create_manager_keyboard(manager_id, name))
    
#Заміна менеджера
@dp.callback_query_handler(lambda query: query.data.startswith('change_manager'))
async def change_manager(callback_query: types.CallbackQuery):
     await bot.edit_message_text(text=callback_query.message.text,
                                 chat_id=callback_query.from_user.id,
                                 message_id=callback_query.message.message_id,
                                 reply_markup=await create_list_of_managers_keyboard(search_manager_list(), False, True))

#обробка меню менеджера - подія - admin
@dp.callback_query_handler(lambda query: query.data.startswith('manager_'))
async def manager_admin_st(callback_query: types.CallbackQuery):
        users = search_manager_list()
        managers_list_keyboard = await create_list_of_managers_keyboard(users, False, False)
        #Дані менеджера
        if(callback_query.data.split('_')[1]=='about'):
            id = callback_query.data.split('_')[2]
            name = callback_query.data.split('_')[3]
            await bot.edit_message_text(text="Оберіть менеджера ⬇️: ", chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id, reply_markup=managers_list_keyboard)
            await bot.send_message(chat_id= callback_query.from_user.id,
                                   text="Кнопка знаходиться в робробці! 🔩",)
        
        #Переглянути замовлення
        if(callback_query.data.split('_')[1]=='orders'):
            id = callback_query.data.split('_')[2]
            name = callback_query.data.split('_')[3]
            leads = user_leads(id, name)
            if len(leads)==0:
                 await bot.send_message(text=f'❗{name} немає замовлень.',
                                        chat_id=callback_query.from_user.id)
                 await bot.edit_message_text(text="Оберіть менеджера ⬇️: ", chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id, reply_markup=managers_list_keyboard)
            else:
                 await bot.edit_message_text(text=callback_query.message.text,
                                             chat_id=callback_query.from_user.id,
                                             message_id=callback_query.message.message_id,
                                             reply_markup=await keyboard_with_orders(leads))

        #Кнопка "назад"            
        if(callback_query.data.split('_')[1]=='back'):
            await bot.edit_message_text(text="Оберіть менеджера ⬇️: ",
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=managers_list_keyboard)

#вихід з адмін панелі - admin
@dp.callback_query_handler(lambda query: query.data.startswith('confirmExitAdmin_'))
async def confirm_exit_admin(callback_query: types.CallbackQuery):
    split_data = callback_query.data.split('_')
    action = split_data[1]

    if action in ['exit', 'cancel']:
        await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)

    if action == 'exit':
        await bot.send_message(callback_query.from_user.id,
                               text="Вихід з адмін-панелі виконаний ✅", 
                               reply_markup=await create_main_keyboard(get_user_data(callback_query.from_user.id)))
        change_admin_status(0, callback_query.from_user.id)
        
#керування лідами
@dp.callback_query_handler(lambda query: query.data.startswith('lead_'))
async def select_lead(callback_query: types.CallbackQuery):
    users = search_manager_list()
    managers_list_keyboard = await create_list_of_managers_keyboard(users, False, False)
    if(callback_query.data.split('_')[1]=='back'):
        await bot.edit_message_text(text="Оберіть менеджера ⬇️: ", chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=managers_list_keyboard)
    else:
         lead=lead_by_id(callback_query.data.split('_')[1])[0]
         await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=(f"ID: {lead['id']} "
                                    f"\nКонтактне ім'я: {lead['contact_name']}"
                                    f"\nНомер телефону: {lead['phone']}."
                                    f"\nОпис замовлення: {lead['name']}."
                                    f"\nМенеджер: {lead['user_id'][1]}." 
                                    f"\nДата створення: {lead['create_date']}."),
                                    reply_markup=create_lead_keyboard(True))

#прийняття чату з користувачем
@dp.callback_query_handler(lambda query: query.data.startswith('accept_chat_button'))
async def accpet_chat_with_user(callback_query: types.CallbackQuery):
     user_id = callback_query.data.split('_')[3]
     username = callback_query.data.split('_')[4]
     print(user_id, username)
     await bot.edit_message_text(chat_id=callback_query.message.chat.id, 
                                 message_id=callback_query.message.message_id,
                                 text=callback_query.message.text+f'\n\n✅Прийнято менеджером\n👉@{callback_query.from_user.username}')
     await bot.send_message(chat_id=callback_query.from_user.id,
                            text=f"✅Ви прийняли чат з юзером {callback_query.data.split('_')[3]}\n👉@{callback_query.from_user.username}")
     await bot.send_message(chat_id=user_id,
                            text=f"✅Ваший запит прийняв менеджер \n👉@{callback_query.from_user.username}")