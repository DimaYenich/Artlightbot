from aiogram.dispatcher.filters.state import State, StatesGroup

class AuthStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_email = State()
    waiting_for_phone = State()

class OfferState(StatesGroup):
    waiting_for_name_of_offer = State()

class AdminPasswordState(StatesGroup):
    waiting_for_admin_password = State()