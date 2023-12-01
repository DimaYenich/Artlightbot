from aiogram import types
from Keyboards.UserKeyboard import lead_keyboard, yes_no_keyboard, start_keyboard
from Keyboards.AdminKeyboard import manager_admin_settings, create_inline_keyboard
from main import search_manager_list  
from DataBaseReader import cursor, conn
from main import connect_to_odoo, url, db, username, password
from main import dp, bot

#обробка кнопки менеджера - подія - admin
@dp.callback_query_handler(lambda query: query.data.startswith('button_'))
async def process_callback_button(query: types.CallbackQuery):
    name = query.data.split('_')[2]
    await bot.edit_message_text(text="🧑‍💼Менеджер: " + name, chat_id=query.from_user.id,
                                message_id=query.message.message_id, reply_markup=manager_admin_settings)


#обробка меню менеджера - подія - admin
@dp.callback_query_handler(lambda query: query.data.startswith('manager_'))
async def manager_admin_st(query: types.CallbackQuery):
        if(query.data.split('_')[1]=='back'):
            users = search_manager_list()
            manager_keyboard = await create_inline_keyboard(users)
            await bot.edit_message_text(text="Оберіть менеджера ⬇️: ", chat_id=query.from_user.id,
                                        message_id=query.message.message_id, reply_markup=manager_keyboard)
        
        if(query.data.split('_')[1]=='about'):
            users = search_manager_list()
            await bot.send_message(chat_id=query.from_user.id, text=users)

        if(query.data.split('_')[1]=='orders'):
            users = search_manager_list()
            
                                    
#вихід з адмін панелі - admin
@dp.callback_query_handler(lambda query: query.data.startswith('confirmExitAdmin_'))
async def confirm_exit_admin(callback_query: types.CallbackQuery):
    if(callback_query.data.split('_')[1]=='exit'):
        await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, text = "Вихід з адмін-панелі виконаний ✅",reply_markup=start_keyboard)
        cursor.execute("UPDATE Users SET isAdmin = ? WHERE chat_id = ? ",(0, callback_query.from_user.id,))
        conn.commit()
    if(callback_query.data.split('_')[1]=='cancel'):
        await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)
        