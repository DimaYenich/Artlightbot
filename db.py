import sqlite3

connection = sqlite3.connect('bot.db')
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    number INTEGER NOT NULL,
    email TEXT,
    chat_id TEXT NOT NULL,
    isAdmin INTEGER NOT NULL,
    isManager INTEGER NOT NULL
);
""")

#додання нового користувача
ADD_NEW_USER = "INSERT INTO Users (name, number, email, chat_id, isAdmin, isManager) VALUES ('{name}','{number}','{email}','{chat_id}','{isAdmin}','{isManager}')"
def add_new_user(name, number, email, chat_id):
    with connection:
        cursor.execute(ADD_NEW_USER.format(name=name, number=number, email=email, chat_id=chat_id, isAdmin=0, isManager=0))
        connection.commit()

#дані користувача
GET_USER_DATA = "SELECT * FROM Users WHERE chat_id = '{chat_id}'"
def get_user_data(chat_id):
    with connection:
        cursor.execute(GET_USER_DATA.format(chat_id=chat_id))
        return cursor.fetchone()

#зміна адмін статусу
CHANGE_ADMIN_STATUS = "UPDATE Users SET isAdmin = '{admin_status}' WHERE chat_id = '{chat_id}'"
def change_admin_status(admin_status, chat_id):
    with connection:
        cursor.execute(CHANGE_ADMIN_STATUS.format(admin_status = admin_status, chat_id=chat_id))
        connection.commit()
