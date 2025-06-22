from aiogram.fsm.state import State, StatesGroup


class CartFSM(StatesGroup):
    waiting_for_quantity = State()
    waiting_for_address = State()
