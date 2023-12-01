from aiogram import executor
from Handlers.start_handlers import *
from Handlers.lead_handlers import *
from Handlers.admin_handlers import *
from Handlers.message_handlers import *


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)